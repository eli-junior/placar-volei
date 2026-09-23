"""Um vínculo por vez (CV3.DS1.US5): trocar de quadra pelo relógio.

O código novo informa o vínculo que substitui. O antigo só cai quando o código
novo é aprovado; desistir cancela o código e mantém o vínculo atual.
"""

import secrets

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.config import settings
from app.db import get_db, init_db_sync
from app.main import app
from app.rate_limit import owner_rate_limiter
from app.watch import approval_limit, creation_limit
from tests.test_watch_comandos import comando, delegar, relogio_id
from tests.test_watch_pairing import link, prepare


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "db_path", str(tmp_path / "watch.db"))
    monkeypatch.setattr(settings, "owner_secret", "test-owner-only")
    creation_limit.resetar()
    approval_limit.resetar()
    owner_rate_limiter.resetar()
    with TestClient(app) as client:
        yield client


def replacing(client, old_token):
    """Código novo, com token novo, que substitui o vínculo de `old_token`."""
    token = secrets.token_urlsafe(32)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/watch/pairing", json={"substitui": old_token}, headers=headers
    )
    assert response.status_code == 201
    return token, headers, response.json()["code"]


def approve(client, court, code):
    return client.post(f"/api/quadras/{court['id']}/watch/approve", json={"code": code})


def apelidos(client, court):
    data = client.get(f"/api/quadras/{court['id']}/participantes").json()
    return [p["apelido"] for p in data["participantes"]]


def descricoes(client, court):
    itens = client.get(f"/api/quadras/{court['id']}/linha-do-tempo").json()
    return [i["descricao"] for i in itens.get("itens", itens)]


def test_approving_in_another_court_moves_watch_and_returns_control(client):
    a = prepare(client)
    old_token, old = link(client, a)
    delegar(client, a, old)
    b = prepare(client)
    with client.websocket_connect(f"/ws/{a['id']}", headers=old) as watch_a:
        assert watch_a.receive_json()["tipo"] == "ESTADO_INICIAL"
        _, new, code = replacing(client, old_token)
        # Antes da aprovação, o vínculo com A continua valendo.
        assert client.get("/api/watch/session", headers=old).status_code == 200
        assert approve(client, b, code).status_code == 200
        with pytest.raises(WebSocketDisconnect):
            while True:
                watch_a.receive_json()
    assert client.get("/api/watch/session", headers=old).status_code == 401
    assert client.get("/api/watch/state", headers=old).status_code == 401
    session = client.get("/api/watch/session", headers=new).json()
    assert session["court_id"] == b["id"]
    assert session["court_name"] == b["nome"]
    assert apelidos(client, a) == ["Eli"]
    assert apelidos(client, b) == ["Eli", "Eli (Relógio)"]
    sala_a = client.get(f"/api/quadras/{a['id']}").json()
    assert sala_a["controle_id"] == a["participante"]["id"]
    assert "Controle devolvido para Eli: relógio foi para outra quadra" in descricoes(
        client, a
    )


def test_old_court_sees_watch_leave_by_broadcast(client):
    a = prepare(client)
    old_token, _ = link(client, a)
    b = prepare(client)
    with client.websocket_connect(f"/ws/{a['id']}") as phone_a:
        phone_a.receive_json()
        _, _, code = replacing(client, old_token)
        assert approve(client, b, code).status_code == 200
        while True:
            message = phone_a.receive_json()
            if message["tipo"] == "PLACAR_ATUALIZADO":
                break
    nomes = [p["apelido"] for p in message["payload"]["participantes"]]
    assert "Eli (Relógio)" not in nomes


def test_watch_without_control_leaves_without_control_event(client):
    a = prepare(client)
    old_token, _ = link(client, a)
    b = prepare(client)
    _, _, code = replacing(client, old_token)
    assert approve(client, b, code).status_code == 200
    assert apelidos(client, a) == ["Eli"]
    assert not any("outra quadra" in d for d in descricoes(client, a))


def test_pending_code_keeps_current_link_until_approved(client):
    a = prepare(client)
    old_token, old = link(client, a)
    delegar(client, a, old)
    replacing(client, old_token)
    assert client.get("/api/watch/session", headers=old).status_code == 200
    assert comando(client, old, "A")[0].status_code == 201
    assert apelidos(client, a) == ["Eli", "Eli (Relógio)"]


def test_cancelled_code_cannot_be_approved_and_link_stays(client):
    a = prepare(client)
    old_token, old = link(client, a)
    b = prepare(client)
    _, new, code = replacing(client, old_token)
    assert client.delete("/api/watch/pairing", headers=new).status_code == 204
    # Idempotente: o relógio pode repetir o cancelamento ao reconectar.
    assert client.delete("/api/watch/pairing", headers=new).status_code == 204
    assert approve(client, b, code).status_code == 400
    assert client.get("/api/watch/session", headers=new).status_code == 401
    assert client.get("/api/watch/session", headers=old).status_code == 200
    assert apelidos(client, a) == ["Eli", "Eli (Relógio)"]


def test_cancel_after_approval_is_refused_and_keeps_new_link(client):
    a = prepare(client)
    old_token, old = link(client, a)
    b = prepare(client)
    _, new, code = replacing(client, old_token)
    assert approve(client, b, code).status_code == 200
    assert client.delete("/api/watch/pairing", headers=new).status_code == 409
    assert client.get("/api/watch/session", headers=new).status_code == 200
    assert client.get("/api/watch/session", headers=old).status_code == 401


def test_cancel_does_not_touch_an_active_link(client):
    a = prepare(client)
    _, old = link(client, a)
    assert client.delete("/api/watch/pairing", headers=old).status_code == 409
    assert client.get("/api/watch/session", headers=old).status_code == 200


def test_relink_in_same_court_keeps_participant_and_control(client):
    a = prepare(client)
    old_token, old = link(client, a)
    watch = delegar(client, a, old)
    _, new, code = replacing(client, old_token)
    assert approve(client, a, code).status_code == 200
    assert relogio_id(client, new) == watch
    assert client.get(f"/api/quadras/{a['id']}").json()["controle_id"] == watch
    assert client.get("/api/watch/session", headers=old).status_code == 401
    assert comando(client, new, "B")[0].status_code == 201


def test_unknown_replacement_changes_nothing(client):
    a = prepare(client)
    old_token, old = link(client, a)
    b = prepare(client)
    # Token forjado: ninguém é revogado.
    _, _, code = replacing(client, secrets.token_urlsafe(32))
    assert approve(client, b, code).status_code == 200
    assert client.get("/api/watch/session", headers=old).json()["court_id"] == a["id"]
    with get_db() as conn:
        assert (
            conn.execute(
                "SELECT COUNT(*) FROM watch_devices WHERE substitui_id IS NOT NULL"
            ).fetchone()[0]
            == 0
        )
    # O próprio token não pede código novo: o vínculo já existe.
    old_again = {"Authorization": f"Bearer {old_token}"}
    assert (
        client.post(
            "/api/watch/pairing", json={"substitui": old_token}, headers=old_again
        ).status_code
        == 409
    )
    assert apelidos(client, a) == ["Eli", "Eli (Relógio)"]


def test_invalid_replacement_token_is_rejected_by_shape(client):
    token = secrets.token_urlsafe(32)
    response = client.post(
        "/api/watch/pairing",
        json={"substitui": "curto"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_pairing_without_body_still_works(client):
    token = secrets.token_urlsafe(32)
    response = client.post(
        "/api/watch/pairing", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201


def test_schema_upgrade_adds_replacement_column(client):
    with get_db() as conn:
        conn.execute("ALTER TABLE watch_devices DROP COLUMN substitui_id")
    init_db_sync(settings.db_path)
    with get_db() as conn:
        colunas = [r["name"] for r in conn.execute("PRAGMA table_info(watch_devices)")]
    assert "substitui_id" in colunas
