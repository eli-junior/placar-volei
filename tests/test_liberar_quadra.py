"""Admin libera a quadra na hora (CV6.DS1.US8)."""

from pathlib import Path

import pytest
from starlette.testclient import TestClient

from app.config import settings
from app.db import init_db
from app.identidade import SESSION_COOKIE
from app.main import app


@pytest.fixture(autouse=True)
async def setup_test_db(tmp_path: Path):
    db_file = str(tmp_path / "test_liberar.db")
    settings.db_path = db_file
    await init_db(db_file)
    yield


def _quadra_com_admin_e_espectador(client):
    quadra_id = client.post("/api/quadras", json={"nome": "Quadra Liberar"}).json()[
        "id"
    ]
    client.post(
        f"/api/quadras/{quadra_id}/entrar",
        json={"apelido": "Admin"},
        headers={"x-session-id": "sessao-admin"},
    )
    client.post(
        f"/api/quadras/{quadra_id}/entrar",
        json={"apelido": "Visita"},
        headers={"x-session-id": "sessao-espectador"},
    )
    return quadra_id


def test_quadra_nova_vale_10_pontos():
    with TestClient(app) as client:
        quadra_id = client.post("/api/quadras", json={"nome": "Padrão"}).json()["id"]
        estado = client.get(f"/api/quadras/{quadra_id}/partida").json()
        assert estado["estado_partida"]["alvo"] == 10


def test_so_o_admin_libera_a_quadra():
    with TestClient(app) as client:
        quadra_id = _quadra_com_admin_e_espectador(client)
        resp = client.post(
            f"/api/quadras/{quadra_id}/liberar",
            headers={"x-session-id": "sessao-espectador"},
        )
        assert resp.status_code == 403
        sem_sessao = client.post(
            f"/api/quadras/{quadra_id}/liberar", headers={"x-session-id": "outra"}
        )
        assert sem_sessao.status_code == 403
        assert client.get(f"/api/quadras/{quadra_id}").status_code == 200


def test_liberar_apaga_a_quadra_e_derruba_quem_esta_conectado():
    with TestClient(app) as client:
        quadra_id = _quadra_com_admin_e_espectador(client)
        with client.websocket_connect(
            f"/ws/{quadra_id}",
            headers={"cookie": f"{SESSION_COOKIE}=sessao-espectador"},
        ) as ws:
            assert ws.receive_json()["tipo"] == "ESTADO_INICIAL"
            assert ws.receive_json()["tipo"] == "PRESENCA_ATUALIZADA"

            resp = client.post(
                f"/api/quadras/{quadra_id}/liberar",
                headers={"x-session-id": "sessao-admin"},
            )
            assert resp.status_code == 204

            aviso = ws.receive_json()
            assert aviso == {"tipo": "SALA_EXPIRADA", "payload": {"motivo": "liberada"}}
            fechamento = ws.receive()
            assert fechamento["type"] == "websocket.close"
            assert fechamento["code"] == 4404

        assert client.get(f"/api/quadras/{quadra_id}").status_code == 404
        de_novo = client.post(
            f"/api/quadras/{quadra_id}/liberar",
            headers={"x-session-id": "sessao-admin"},
        )
        assert de_novo.status_code == 404
