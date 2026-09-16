"""Testes da CV2.DS2.US5 — Governança de controle e prevenção de perda.

Cobrem as três regras que o débito `debt-apelidos-e-transferencia-de-controle`
pede na sua condição de fechamento (parte A4):

- promover concede PERMISSÃO e não entrega o placar;
- passar o controle para quem está offline é recusado;
- o controle volta sozinho ao admin depois de `controle_timeout_seconds`.

Todo teste de permissão aqui bate no backend, nunca na interface: esconder o
botão não é controle de acesso.
"""

from datetime import UTC, datetime, timedelta

import pytest
from starlette.testclient import TestClient

from app.comandos import snapshot_sync
from app.config import settings
from app.db import get_db, init_db_sync
from app.identidade import SESSION_COOKIE
from app.main import app
from app.sucessao import verificar_controle_ocioso_sync


@pytest.fixture(autouse=True)
def banco(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "db_path", str(tmp_path / "governanca.db"))
    monkeypatch.setattr(settings, "presenca_ttl_seconds", 120)
    monkeypatch.setattr(settings, "controle_timeout_seconds", 15)
    init_db_sync()


class Cliente:
    """Uma identidade de navegador dentro do mesmo servidor de teste."""

    def __init__(self, base, token):
        self._base = base
        self.token = token

    def post(self, url, **kwargs):
        headers = {**kwargs.pop("headers", {}), "x-session-id": self.token}
        return self._base.post(url, headers=headers, **kwargs)

    def get(self, url, **kwargs):
        headers = {**kwargs.pop("headers", {}), "x-session-id": self.token}
        return self._base.get(url, headers=headers, **kwargs)

    def websocket_connect(self, url):
        return self._base.websocket_connect(
            url, headers={"cookie": f"{SESSION_COOKIE}={self.token}"}
        )


def envelhecer_participante(participante_id: str, segundos: int) -> None:
    """Joga o último sinal de vida de alguém para trás no tempo.

    Preferido a `sleep`: o teste passa a depender de um dado observável no
    banco, e não da velocidade da suíte.
    """
    passado = (datetime.now(UTC) - timedelta(seconds=segundos)).isoformat()
    with get_db(settings.db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            "UPDATE participantes SET ultimo_visto_em = ? WHERE id = ?",
            (passado, participante_id),
        )
        conn.commit()


def test_promover_concede_permissao_sem_entregar_o_placar():
    """Autorizar alguém a ajudar não pode tirar o placar da mão do admin."""
    with TestClient(app) as base:
        admin = Cliente(base, "sessao-admin")
        ajudante = Cliente(base, "sessao-ajudante")

        sala = admin.post("/api/quadras", json={"apelido": "Admin"}).json()
        quadra_id = sala["id"]
        admin_id = sala["participante"]["id"]

        entrada = ajudante.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Ajudante"}
        ).json()
        ajudante_id = entrada["participante"]["id"]

        promovido = admin.post(
            f"/api/quadras/{quadra_id}/participantes/{ajudante_id}/promover"
        )
        assert promovido.status_code == 200
        dados = promovido.json()

        papel = next(p["papel"] for p in dados["participantes"] if p["id"] == ajudante_id)
        assert papel == "CONTROLADOR"
        # A permissão mudou; a posse do placar, não.
        assert dados["quadra"]["controle_id"] == admin_id

        # E o admin continua conseguindo marcar ponto sem reassumir nada.
        ponto = admin.post(
            f"/api/quadras/{quadra_id}/pontos",
            json={"equipe": "A"},
            headers={"x-control-version": str(dados["quadra"]["controle_versao"])},
        )
        assert ponto.status_code == 201


def test_transferencia_exige_admin_e_participante_com_permissao():
    with TestClient(app) as base:
        admin = Cliente(base, "sessao-admin")
        espectador = Cliente(base, "sessao-espectador")

        sala = admin.post("/api/quadras", json={"apelido": "Admin"}).json()
        quadra_id = sala["id"]
        entrada = espectador.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Torcida"}
        ).json()
        espectador_id = entrada["participante"]["id"]

        # Espectador não recebe o placar: não tem permissão.
        recusado = admin.post(
            f"/api/quadras/{quadra_id}/participantes/{espectador_id}/controle"
        )
        assert recusado.status_code == 400
        assert "controlador" in recusado.json()["detail"].lower()

        # E o próprio espectador não pode passar o placar para si.
        forjado = espectador.post(
            f"/api/quadras/{quadra_id}/participantes/{espectador_id}/controle"
        )
        assert forjado.status_code == 403


def test_controle_nao_passa_para_participante_offline():
    """O repasse às cegas é o que deixa a partida sem operador."""
    with TestClient(app) as base:
        admin = Cliente(base, "sessao-admin")
        ausente = Cliente(base, "sessao-ausente")

        sala = admin.post("/api/quadras", json={"apelido": "Admin"}).json()
        quadra_id = sala["id"]
        admin_id = sala["participante"]["id"]
        entrada = ausente.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Sumido"}
        ).json()
        ausente_id = entrada["participante"]["id"]

        admin.post(f"/api/quadras/{quadra_id}/participantes/{ausente_id}/promover")

        # Sem socket aberto e com o sinal de vida vencido, ele está offline.
        envelhecer_participante(ausente_id, settings.presenca_ttl_seconds + 60)

        recusado = admin.post(
            f"/api/quadras/{quadra_id}/participantes/{ausente_id}/controle"
        )
        assert recusado.status_code == 409
        assert "offline" in recusado.json()["detail"].lower()

        estado = snapshot_sync(settings.db_path, quadra_id)
        assert estado["quadra"]["controle_id"] == admin_id


def test_controle_passa_para_controlador_conectado():
    with TestClient(app) as base:
        admin = Cliente(base, "sessao-admin")
        ajudante = Cliente(base, "sessao-ajudante")

        sala = admin.post("/api/quadras", json={"apelido": "Admin"}).json()
        quadra_id = sala["id"]
        entrada = ajudante.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Ajudante"}
        ).json()
        ajudante_id = entrada["participante"]["id"]
        admin.post(f"/api/quadras/{quadra_id}/participantes/{ajudante_id}/promover")

        with ajudante.websocket_connect(f"/ws/{quadra_id}") as ws:
            ws.receive_json()  # ESTADO_INICIAL
            transferido = admin.post(
                f"/api/quadras/{quadra_id}/participantes/{ajudante_id}/controle"
            )
            assert transferido.status_code == 200
            dados = transferido.json()
            assert dados["quadra"]["controle_id"] == ajudante_id
            assert dados["evento"]["tipo"] == "CONTROLE_TRANSFERIDO"

            # E agora quem marca ponto é ele, não mais o admin.
            versao = str(dados["quadra"]["controle_versao"])
            assert (
                ajudante.post(
                    f"/api/quadras/{quadra_id}/pontos",
                    json={"equipe": "B"},
                    headers={"x-control-version": versao},
                ).status_code
                == 201
            )
            assert (
                admin.post(
                    f"/api/quadras/{quadra_id}/pontos",
                    json={"equipe": "A"},
                    headers={"x-control-version": versao},
                ).status_code
                == 403
            )

        linha = admin.get(f"/api/quadras/{quadra_id}/linha-do-tempo").json()["itens"]
        assert any("passou o controle para Ajudante" in i["descricao"] for i in linha)


def test_controle_volta_ao_admin_apos_ausencia_do_controlador():
    """Auto-retorno em 15s: a partida não fica refém de um celular no bolso."""
    with TestClient(app) as base:
        admin = Cliente(base, "sessao-admin")
        ajudante = Cliente(base, "sessao-ajudante")

        sala = admin.post("/api/quadras", json={"apelido": "Admin"}).json()
        quadra_id = sala["id"]
        admin_id = sala["participante"]["id"]
        entrada = ajudante.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Ajudante"}
        ).json()
        ajudante_id = entrada["participante"]["id"]
        admin.post(f"/api/quadras/{quadra_id}/participantes/{ajudante_id}/promover")

        with ajudante.websocket_connect(f"/ws/{quadra_id}") as ws:
            ws.receive_json()
            transferido = admin.post(
                f"/api/quadras/{quadra_id}/participantes/{ajudante_id}/controle"
            )
            assert transferido.status_code == 200
            assert transferido.json()["quadra"]["controle_id"] == ajudante_id

            # O sinal de vida é envelhecido com o socket ainda aberto de
            # propósito: o servidor só reescreve `ultimo_visto_em` na conexão e
            # na desconexão, então aqui o dado fica estável e o teste não
            # depende de quando a desconexão termina de ser processada.
            envelhecer_participante(ajudante_id, settings.controle_timeout_seconds + 5)

            # A ausência entra na rotina como valor: `online_ids` sem o
            # controlador é exatamente o que o hub reporta depois da queda.
            ausente = {admin_id}

            # Antes do prazo, nada acontece.
            assert (
                verificar_controle_ocioso_sync(
                    settings.db_path, quadra_id, ausente, timeout_seconds=600
                )
                is None
            )

            depois = verificar_controle_ocioso_sync(
                settings.db_path, quadra_id, ausente, timeout_seconds=15
            )
            assert depois is not None
            assert depois["quadra"]["controle_id"] == admin_id
            assert any(i["tipo"] == "CONTROLE_DEVOLVIDO" for i in depois["linha_do_tempo"])

            # A rotina é idempotente: com o controle já no admin, nada muda.
            assert (
                verificar_controle_ocioso_sync(
                    settings.db_path, quadra_id, ausente, timeout_seconds=15
                )
                is None
            )

            # E o admin volta a marcar ponto sem precisar reassumir nada.
            versao = str(depois["quadra"]["controle_versao"])
            assert (
                admin.post(
                    f"/api/quadras/{quadra_id}/pontos",
                    json={"equipe": "A"},
                    headers={"x-control-version": versao},
                ).status_code
                == 201
            )


def test_controle_nao_volta_enquanto_o_controlador_esta_online():
    with TestClient(app) as base:
        admin = Cliente(base, "sessao-admin")
        ajudante = Cliente(base, "sessao-ajudante")

        sala = admin.post("/api/quadras", json={"apelido": "Admin"}).json()
        quadra_id = sala["id"]
        admin_id = sala["participante"]["id"]
        entrada = ajudante.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Ajudante"}
        ).json()
        ajudante_id = entrada["participante"]["id"]
        admin.post(f"/api/quadras/{quadra_id}/participantes/{ajudante_id}/promover")

        with ajudante.websocket_connect(f"/ws/{quadra_id}") as ws:
            ws.receive_json()
            admin.post(f"/api/quadras/{quadra_id}/participantes/{ajudante_id}/controle")

            # Mesmo com o sinal de vida antigo, a conexão viva manda.
            envelhecer_participante(ajudante_id, 600)
            assert (
                verificar_controle_ocioso_sync(
                    settings.db_path,
                    quadra_id,
                    {admin_id, ajudante_id},
                    timeout_seconds=15,
                )
                is None
            )


def test_controle_nao_volta_sem_admin_conectado():
    """Sem admin presente, quem cuida do caso é a sucessão, não esta rotina."""
    with TestClient(app) as base:
        admin = Cliente(base, "sessao-admin")
        ajudante = Cliente(base, "sessao-ajudante")

        sala = admin.post("/api/quadras", json={"apelido": "Admin"}).json()
        quadra_id = sala["id"]
        entrada = ajudante.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Ajudante"}
        ).json()
        ajudante_id = entrada["participante"]["id"]
        admin.post(f"/api/quadras/{quadra_id}/participantes/{ajudante_id}/promover")

        with ajudante.websocket_connect(f"/ws/{quadra_id}") as ws:
            ws.receive_json()
            admin.post(f"/api/quadras/{quadra_id}/participantes/{ajudante_id}/controle")
            envelhecer_participante(ajudante_id, 600)

            # Ninguém online: nem o controlador, nem o admin.
            assert (
                verificar_controle_ocioso_sync(
                    settings.db_path, quadra_id, set(), timeout_seconds=15
                )
                is None
            )
