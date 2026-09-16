"""Testes da CV2.DS1 — Blindagem e Confiabilidade do Placar em Tempo Real.

Cobre os três débitos quitados pela story:

- `debt-codigo-mestre-no-websocket` (C1): o snapshot só transporta a allowlist
  pública de campos da quadra.
- `debt-lotacao-fantasma` (C2): a capacidade da sala conta presença efetiva.
- `debt-integridade-de-toques-e-erros-422` (A7): 422 legível e estável.
"""

import json
import time
from datetime import UTC, datetime, timedelta

import pytest
from starlette.testclient import TestClient

from app.comandos import CAMPOS_PUBLICOS_QUADRA, snapshot_sync
from app.config import settings
from app.db import get_db, init_db_sync
from app.identidade import SESSION_COOKIE
from app.main import app
from app.quadras import criar_quadra_sync


@pytest.fixture(autouse=True)
def banco(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "db_path", str(tmp_path / "blindagem.db"))
    monkeypatch.setattr(settings, "max_quadras", 20)
    monkeypatch.setattr(settings, "max_participantes_por_quadra", 20)
    monkeypatch.setattr(settings, "presenca_ttl_seconds", 120)
    init_db_sync()


class Cliente:
    """Uma identidade de navegador dentro do mesmo servidor de teste."""

    def __init__(self, base, token):
        self._base = base
        self.token = token

    def post(self, url, **kwargs):
        headers = {**kwargs.pop("headers", {}), "x-session-id": self.token}
        return self._base.post(url, headers=headers, **kwargs)

    def websocket_connect(self, url):
        return self._base.websocket_connect(
            url, headers={"cookie": f"{SESSION_COOKIE}={self.token}"}
        )


def criar_sala(client, apelido="Admin"):
    resposta = client.post("/api/quadras", json={"apelido": apelido})
    assert resposta.status_code == 201
    return resposta.json()


def marcar_ponto(client, quadra_id, versao=1):
    return client.post(
        f"/api/quadras/{quadra_id}/pontos",
        json={"equipe": "A"},
        headers={"x-control-version": str(versao)},
    )


def ler_codigo_mestre(quadra_id):
    with get_db() as conn:
        linha = conn.execute(
            "SELECT codigo_mestre FROM quadras WHERE id = ?", (quadra_id,)
        ).fetchone()
    return linha["codigo_mestre"]


def envelhecer_participantes(quadra_id, segundos):
    """Recua o `ultimo_visto_em` de todos da sala, simulando fantasmas."""
    momento = (datetime.now(UTC) - timedelta(seconds=segundos)).isoformat()
    with get_db() as conn:
        conn.execute(
            "UPDATE participantes SET ultimo_visto_em = ? WHERE quadra_id = ?",
            (momento, quadra_id),
        )
        conn.commit()


# --- C1: BLINDAGEM DO WEBSOCKET ---


def test_espectador_nao_recebe_codigo_mestre_em_nenhum_frame():
    """Nenhum frame recebido por um espectador carrega o código mestre da sala."""
    with TestClient(app) as base:
        quadra = criar_sala(base)
        quadra_id = quadra["id"]
        codigo_mestre = ler_codigo_mestre(quadra_id)
        assert codigo_mestre, "a sala precisa ter código mestre para o teste valer"

        espectador = Cliente(base, "sessao-espectadora")
        entrada = espectador.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Torcida"}
        )
        assert entrada.status_code == 200
        assert entrada.json()["participante"]["papel"] == "ESPECTADOR"

        with espectador.websocket_connect(f"/ws/{quadra_id}") as ws:
            inicial = ws.receive_json()
            assert inicial["tipo"] == "ESTADO_INICIAL"

            assert marcar_ponto(base, quadra_id).status_code == 201

            frames = [inicial]
            tipos = {inicial["tipo"]}
            for _ in range(6):
                frame = ws.receive_json()
                frames.append(frame)
                tipos.add(frame["tipo"])
                if "PLACAR_ATUALIZADO" in tipos:
                    break

        assert "PLACAR_ATUALIZADO" in tipos, (
            "o teste precisa observar o frame de placar atualizado"
        )
        bruto = json.dumps(frames, ensure_ascii=False)
        assert "codigo_mestre" not in bruto
        assert codigo_mestre not in bruto

        # A chave `quadra` traz exatamente a allowlist pública (mais `partida_id`).
        for frame in frames:
            sala = frame["payload"].get("quadra")
            if sala is not None:
                assert set(sala) == set(CAMPOS_PUBLICOS_QUADRA) | {"partida_id"}


def test_coluna_sensivel_futura_fica_fora_do_snapshot_por_padrao():
    """Uma coluna nova em `quadras` não vaza sozinha: a allowlist é explícita."""
    quadra = criar_quadra_sync(
        settings.db_path, nome="Quadra Blindada", session_id="s1", apelido="Admin"
    )
    with get_db() as conn:
        conn.execute("ALTER TABLE quadras ADD COLUMN token_de_operacao TEXT")
        conn.execute("UPDATE quadras SET token_de_operacao = 'segredo-futuro'")
        conn.commit()

    snap = snapshot_sync(settings.db_path, quadra["id"])
    assert "token_de_operacao" not in snap["quadra"]
    assert "segredo-futuro" not in json.dumps(snap, ensure_ascii=False)
    assert set(snap["quadra"]) == set(CAMPOS_PUBLICOS_QUADRA) | {"partida_id"}


# --- C2: CAPACIDADE REAL / PREVENÇÃO DE FANTASMAS ---


def test_sala_genuinamente_cheia_continua_bloqueando(monkeypatch):
    """Com todo mundo presente de verdade, o limite continua valendo."""
    monkeypatch.setattr(settings, "max_participantes_por_quadra", 2)
    with TestClient(app) as base:
        quadra_id = criar_sala(base)["id"]

        segunda = Cliente(base, "sessao-2").post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Bia"}
        )
        assert segunda.status_code == 200

        terceira = Cliente(base, "sessao-3").post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Caio"}
        )
        assert terceira.status_code == 400
        assert "Limite máximo de 2 participantes" in terceira.json()["detail"]


def test_entrada_liberada_apos_expiracao_dos_fantasmas(monkeypatch):
    """Quem fechou o navegador e saiu da janela de presença devolve a vaga."""
    monkeypatch.setattr(settings, "max_participantes_por_quadra", 2)
    monkeypatch.setattr(settings, "presenca_ttl_seconds", 60)
    with TestClient(app) as base:
        quadra_id = criar_sala(base)["id"]
        assert (
            Cliente(base, "sessao-2")
            .post(f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Bia"})
            .status_code
            == 200
        )
        assert (
            Cliente(base, "sessao-3")
            .post(f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Caio"})
            .status_code
            == 400
        )

        # As duas pessoas somem da quadra: sem socket e sem sinal de vida recente.
        envelhecer_participantes(quadra_id, 3600)

        tardia = Cliente(base, "sessao-4").post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Duda"}
        )
        assert tardia.status_code == 200
        # Fantasma expirado libera vaga, mas não promove o recém-chegado a ADMIN:
        # o papel inicial continua olhando a sala inteira.
        assert tardia.json()["participante"]["papel"] == "ESPECTADOR"


def test_conexao_ativa_ocupa_vaga_mesmo_sem_sinal_recente(monkeypatch):
    """Com o mesmo `ultimo_visto_em` velho, quem decide é a conexão no hub."""
    monkeypatch.setattr(settings, "max_participantes_por_quadra", 1)
    monkeypatch.setattr(settings, "presenca_ttl_seconds", 60)
    with TestClient(app) as base:
        quadra_id = criar_sala(base)["id"]
        visitante = Cliente(base, "sessao-visitante")

        with base.websocket_connect(f"/ws/{quadra_id}") as ws:
            assert ws.receive_json()["tipo"] == "ESTADO_INICIAL"
            envelhecer_participantes(quadra_id, 3600)

            bloqueada = visitante.post(
                f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Bia"}
            )
            assert bloqueada.status_code == 400

        # Socket fechado e sinal de vida novamente velho: a vaga é devolvida.
        # A liberação é eventual por natureza: sair do `with` devolve o controle
        # ao cliente antes de o servidor concluir o `finally` que tira a conexão
        # do hub. Esperar pelo comportamento observável mantém o teste honesto —
        # se a vaga nunca fosse devolvida, o laço esgota e o teste falha.
        limite = time.monotonic() + 3
        while True:
            envelhecer_participantes(quadra_id, 3600)
            liberada = visitante.post(
                f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Bia"}
            )
            if liberada.status_code == 200 or time.monotonic() > limite:
                break
            time.sleep(0.02)
        assert liberada.status_code == 200


# --- A7: NORMALIZAÇÃO DE ERROS 422 ---


def test_422_de_campo_obrigatorio_tem_detalhe_legivel():
    with TestClient(app) as base:
        quadra_id = criar_sala(base)["id"]
        resposta = Cliente(base, "sessao-2").post(
            f"/api/quadras/{quadra_id}/entrar", json={}
        )
        assert resposta.status_code == 422
        corpo = resposta.json()
        assert isinstance(corpo["detail"], str)
        assert corpo["detail"] == "Apelido é obrigatório."
        assert corpo["erros"] == [
            {
                "campo": "apelido",
                "rotulo": "Apelido",
                "mensagem": "é obrigatório",
                "tipo": "missing",
            }
        ]


def test_422_de_limites_descreve_cada_campo():
    with TestClient(app) as base:
        resposta = base.post(
            "/api/quadras",
            json={"apelido": "a" * 31, "alvo": 0, "nome": "n" * 51},
        )
        assert resposta.status_code == 422
        corpo = resposta.json()
        assert isinstance(corpo["detail"], str)
        assert "Apelido deve ter no máximo 30 caractere(s)." in corpo["detail"]
        assert "Nome da sala deve ter no máximo 50 caractere(s)." in corpo["detail"]
        assert "Pontuação-alvo deve ser no mínimo 1." in corpo["detail"]
        campos = {erro["campo"] for erro in corpo["erros"]}
        assert campos == {"apelido", "nome", "alvo"}


def test_422_de_regra_de_negocio_continua_string_simples():
    """O 422 lançado à mão pela regra de teto segue com `detail` em texto."""
    with TestClient(app) as base:
        resposta = base.post("/api/quadras", json={"alvo": 15, "teto": 10})
        assert resposta.status_code == 422
        detalhe = resposta.json()["detail"]
        assert isinstance(detalhe, str)
        assert "teto da vantagem" in detalhe
