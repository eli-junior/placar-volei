from contextlib import contextmanager
from pathlib import Path

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app import main
from app.config import settings
from app.main import app
from app.rate_limit import owner_rate_limiter

CABECALHO = {"x-owner-secret": "segredo-teste"}


@pytest.fixture
def cliente(tmp_path: Path, monkeypatch):
    settings.db_path = str(tmp_path / "quadras.db")
    settings.gerenciador_db_path = str(tmp_path / "gerenciador.db")
    settings.owner_secret = "segredo-teste"
    settings.gerenciador_backup_dir = ""
    monkeypatch.setattr(main, "PRAZO_AUTENTICACAO", 0.4)
    owner_rate_limiter.resetar()
    with TestClient(app, headers=CABECALHO) as c:
        yield c
    owner_rate_limiter.resetar()


@contextmanager
def conectar(cliente, segredo="segredo-teste", enviar=True):
    with cliente.websocket_connect("/ws/gerenciador") as ws:
        if enviar:
            ws.send_json({"tipo": "AUTENTICAR", "segredo": segredo})
        yield ws


def fechado(ws):
    with pytest.raises(WebSocketDisconnect) as e:
        ws.receive_json()
    return e.value.code


def test_autentica_pela_primeira_mensagem_e_recebe_o_estado(cliente):
    cliente.post("/api/sessao")
    with conectar(cliente) as ws:
        msg = ws.receive_json()
    assert msg["tipo"] == "ESTADO_INICIAL"
    assert msg["payload"]["sessao"] is not None and msg["payload"]["presentes"] == []


@pytest.mark.parametrize("segredo", ["errado", "", None, 123])
def test_segredo_errado_fecha_com_4401(cliente, segredo):
    with conectar(cliente, segredo) as ws:
        assert fechado(ws) == 4401


def test_primeira_mensagem_que_nao_e_autenticar_e_recusada(cliente):
    with cliente.websocket_connect("/ws/gerenciador") as ws:
        ws.send_json({"tipo": "OUTRA", "segredo": "segredo-teste"})
        assert fechado(ws) == 4401


def test_sem_mensagem_no_prazo_fecha(cliente):
    with conectar(cliente, enviar=False) as ws:
        assert fechado(ws) == 4401


def test_tentativas_erradas_pelo_ws_contam_no_limite(cliente):
    for _ in range(12):
        with conectar(cliente, "errado") as ws:
            assert fechado(ws) == 4401
    with conectar(cliente) as ws:  # mesmo IP já bloqueado: nem o segredo certo passa
        assert fechado(ws) == 4401


def test_mudancas_chegam_aos_dois_aparelhos(cliente):
    cliente.post("/api/sessao")
    with conectar(cliente) as a, conectar(cliente) as b:
        assert a.receive_json()["tipo"] == b.receive_json()["tipo"] == "ESTADO_INICIAL"

        j = cliente.post(
            "/api/jogadores", json={"nome": "Ana Souza", "genero": "M"}
        ).json()
        for ws in (a, b):  # novo jogador aparece em "ausentes" nos dois
            msg = ws.receive_json()
            assert msg["tipo"] == "ESTADO_ATUALIZADO"
            assert [x["nome"] for x in msg["payload"]["ausentes"]] == ["Ana Souza"]

        cliente.put(f"/api/sessao/presencas/{j['id']}")
        for ws in (a, b):
            assert [x["nome"] for x in ws.receive_json()["payload"]["presentes"]] == [
                "Ana Souza"
            ]

        cliente.post(f"/api/jogadores/{j['id']}/inativar")
        for ws in (a, b):
            assert ws.receive_json()["payload"]["presentes"] == []


def test_quem_chega_depois_recebe_o_estado_atual(cliente):
    cliente.post("/api/sessao")
    j = cliente.post("/api/jogadores", json={"nome": "Ana Souza", "genero": "M"}).json()
    cliente.put(f"/api/sessao/presencas/{j['id']}")
    with conectar(cliente) as ws:
        msg = ws.receive_json()
    assert msg["tipo"] == "ESTADO_INICIAL"
    assert [x["nome"] for x in msg["payload"]["presentes"]] == ["Ana Souza"]


def test_desconectar_nao_atrapalha_as_mudancas_seguintes(cliente):
    cliente.post("/api/sessao")
    with conectar(cliente) as ws:
        ws.receive_json()
    assert (
        cliente.post(
            "/api/jogadores", json={"nome": "Bia Lima", "genero": "M"}
        ).status_code
        == 201
    )
