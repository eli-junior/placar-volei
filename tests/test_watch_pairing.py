"""Vínculo nativo, escopo de credencial e presença de múltiplos dispositivos."""

import secrets
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.config import settings
from app.db import get_db
from app.hub import hub
from app.identidade import SESSION_COOKIE, hash_sessao
from app.main import app
from app.rate_limit import owner_rate_limiter
from app.watch import approval_limit, creation_limit


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "db_path", str(tmp_path / "watch.db"))
    monkeypatch.setattr(settings, "owner_secret", "test-owner-only")
    creation_limit.resetar()
    approval_limit.resetar()
    owner_rate_limiter.resetar()
    with TestClient(app) as client:
        yield client


def prepare(client):
    court = client.post("/api/quadras", json={"apelido": "eli"}).json()
    response = client.post(
        "/api/owner/watch-access",
        json={"participant_id": court["participante"]["id"]},
        headers={"x-owner-secret": settings.owner_secret},
    )
    assert response.status_code == 200
    return court


def pairing(client):
    token = secrets.token_urlsafe(32)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/watch/pairing", headers=headers)
    assert response.status_code == 201
    assert response.headers["Cache-Control"] == "no-store"
    return token, headers, response.json()["code"]


def link(client, court):
    token, headers, code = pairing(client)
    assert (
        client.post(
            f"/api/quadras/{court['id']}/watch/approve", json={"code": code}
        ).status_code
        == 200
    )
    return token, headers


def test_link_uses_same_participant_without_exposing_credentials(client):
    court = prepare(client)
    token, headers, code = pairing(client)
    assert client.get("/api/watch/session", headers=headers).json() == {
        "status": "pending"
    }
    assert (
        client.post(
            f"/api/quadras/{court['id']}/watch/approve", json={"code": code}
        ).status_code
        == 200
    )
    assert client.get("/api/watch/session", headers=headers).json() == {
        "status": "linked",
        "court_id": court["id"],
        "participant_id": court["participante"]["id"],
        "display_name": "eli",
    }
    state = client.get("/api/watch/state", headers=headers)
    assert state.status_code == 200
    assert len(state.json()["participantes"]) == 1
    assert state.json()["participantes"][0]["id"] == court["participante"]["id"]
    for secret in (
        token,
        code,
        settings.owner_secret,
        "eli-smartwatch",
        "token_hash",
        "session_hash",
    ):
        assert secret not in state.text
    with get_db() as conn:
        device = dict(conn.execute("SELECT * FROM watch_devices").fetchone())
    assert device["token_hash"] == hash_sessao(token)
    assert token not in str(device)
    assert device["code_hash"] is None


def test_owner_grant_required_even_with_correct_name(client):
    court = client.post("/api/quadras", json={"apelido": "eli"}).json()
    _, _, code = pairing(client)
    assert (
        client.post(
            "/api/owner/watch-access",
            json={"participant_id": court["participante"]["id"]},
        ).status_code
        == 404
    )
    assert client.get(f"/api/quadras/{court['id']}/watch").json()["enabled"] is False
    assert (
        client.post(
            f"/api/quadras/{court['id']}/watch/approve", json={"code": code}
        ).status_code
        == 403
    )


def test_watch_nickname_enables_watch_and_shows_only_public_name(client, monkeypatch):
    monkeypatch.setattr(settings, "watch_auto_grant", "eli.relogio")
    court = client.post("/api/quadras", json={"apelido": "Eli.Relogio"}).json()
    assert court["participante"]["apelido"] == "eli"
    assert client.get(f"/api/quadras/{court['id']}/watch").json()["enabled"] is True
    _, _, code = pairing(client)
    approved = client.post(
        f"/api/quadras/{court['id']}/watch/approve", json={"code": code}
    )
    assert approved.json()["display_name"] == "eli"
    state = client.get(f"/api/quadras/{court['id']}").text
    # O apelido-senha não vaza; campos como `controle_relogio` são esperados.
    assert ".relogio" not in state.lower()


def test_watch_nickname_grants_on_join_and_blocks_copy(client, monkeypatch):
    monkeypatch.setattr(settings, "watch_auto_grant", "eli.relogio")
    court = client.post("/api/quadras", json={"apelido": "ana"}).json()
    joined = client.post(
        f"/api/quadras/{court['id']}/entrar",
        json={"apelido": "eli.relogio"},
        headers={"x-session-id": "eli-phone"},
    )
    assert joined.status_code == 200
    assert joined.json()["participante"]["apelido"] == "eli"
    with get_db() as conn:
        assert conn.execute(
            "SELECT 1 FROM watch_grants WHERE participant_id = ?",
            (joined.json()["participante"]["id"],),
        ).fetchone()
    copycat = client.post(
        f"/api/quadras/{court['id']}/entrar",
        json={"apelido": "eli"},
        headers={"x-session-id": "copycat"},
    )
    assert copycat.status_code == 409


def test_plain_public_name_does_not_enable_watch(client, monkeypatch):
    monkeypatch.setattr(settings, "watch_auto_grant", "eli.relogio")
    court = client.post("/api/quadras", json={"apelido": "eli"}).json()
    _, _, code = pairing(client)
    assert client.get(f"/api/quadras/{court['id']}/watch").json()["enabled"] is False
    assert (
        client.post(
            f"/api/quadras/{court['id']}/watch/approve", json={"code": code}
        ).status_code
        == 403
    )


def test_spectator_cannot_approve_even_with_grant(client):
    court = prepare(client)
    viewer = {"x-session-id": "viewer"}
    p = client.post(
        f"/api/quadras/{court['id']}/entrar",
        headers=viewer,
        json={"apelido": "torcida"},
    ).json()["participante"]
    _, _, code = pairing(client)
    with get_db() as conn:
        conn.execute("INSERT INTO watch_grants VALUES (?)", (p["id"],))
    assert (
        client.post(
            f"/api/quadras/{court['id']}/watch/approve",
            headers=viewer,
            json={"code": code},
        ).status_code
        == 403
    )


def test_code_expires_and_cannot_be_reused(client):
    court = prepare(client)
    _, headers, code = pairing(client)
    with get_db() as conn:
        conn.execute(
            "UPDATE watch_devices SET expires_at = ?",
            ((datetime.now(UTC) - timedelta(seconds=1)).isoformat(),),
        )
    assert client.get("/api/watch/session", headers=headers).status_code == 410
    assert (
        client.post(
            f"/api/quadras/{court['id']}/watch/approve", json={"code": code}
        ).status_code
        == 400
    )
    _, _, code = pairing(client)
    url = f"/api/quadras/{court['id']}/watch/approve"
    assert client.post(url, json={"code": code}).status_code == 200
    assert client.post(url, json={"code": code}).status_code == 400


def test_approval_attempts_limited_by_participant_not_forwarded_ip(client):
    court = prepare(client)
    for n in range(5):
        response = client.post(
            f"/api/quadras/{court['id']}/watch/approve",
            json={"code": "00000000"},
            headers={"x-forwarded-for": f"10.0.0.{n}"},
        )
        assert response.status_code == 400
    response = client.post(
        f"/api/quadras/{court['id']}/watch/approve", json={"code": "00000000"}
    )
    assert response.status_code == 429
    assert int(response.headers["Retry-After"]) > 0


def test_creation_limit(client):
    for _ in range(5):
        pairing(client)
    assert (
        client.post(
            "/api/watch/pairing",
            headers={"Authorization": f"Bearer {secrets.token_urlsafe(32)}"},
        ).status_code
        == 429
    )


def test_revoke_disconnects_watch_but_not_phone(client):
    court = prepare(client)
    _, headers = link(client, court)
    with client.websocket_connect(f"/ws/{court['id']}") as phone:
        phone.receive_json()
        with client.websocket_connect(f"/ws/{court['id']}", headers=headers) as watch:
            assert watch.receive_json()["tipo"] == "ESTADO_INICIAL"
            devices = client.get(f"/api/quadras/{court['id']}/watch").json()["devices"]
            assert (
                client.delete(
                    f"/api/quadras/{court['id']}/watch/{devices[0]['id']}"
                ).status_code
                == 200
            )
            assert client.get("/api/watch/state", headers=headers).status_code == 401
            with pytest.raises(WebSocketDisconnect):
                while True:
                    watch.receive_json()
        # O telefone continua apto a marcar e receber atualizações.
        assert (
            client.post(
                f"/api/quadras/{court['id']}/pontos",
                json={"equipe": "A"},
                headers={"x-control-version": "1"},
            ).status_code
            == 201
        )
        while phone.receive_json()["tipo"] != "PLACAR_ATUALIZADO":
            pass


def test_relink_and_owner_disable_revoke_old_credentials(client):
    court = prepare(client)
    _, old = link(client, court)
    _, new = link(client, court)
    assert client.get("/api/watch/session", headers=old).status_code == 401
    assert client.get("/api/watch/session", headers=new).status_code == 200
    response = client.post(
        "/api/owner/watch-access",
        json={"participant_id": court["participante"]["id"], "enabled": False},
        headers={"x-owner-secret": settings.owner_secret},
    )
    assert response.status_code == 200
    assert client.get("/api/watch/session", headers=new).status_code == 401


def test_token_cannot_be_used_as_browser_or_in_another_court(client):
    court = prepare(client)
    token, headers = link(client, court)
    other = client.post("/api/quadras", json={"apelido": "eli"}).json()
    with (
        pytest.raises(WebSocketDisconnect),
        client.websocket_connect(f"/ws/{other['id']}", headers=headers) as ws,
    ):
        ws.receive_json()
    assert (
        client.post(
            f"/api/quadras/{court['id']}/pontos",
            json={"equipe": "A"},
            headers={"x-session-id": token, "x-control-version": "1"},
        ).status_code
        == 403
    )
    assert (
        client.post(
            f"/api/quadras/{court['id']}/watch/approve",
            json={"code": "12345678"},
            headers={"x-session-id": token},
        ).status_code
        == 403
    )


def test_permission_loss_and_room_expiration_reject_device(client):
    court = prepare(client)
    _, headers = link(client, court)
    with get_db() as conn:
        conn.execute("UPDATE participantes SET papel = 'ESPECTADOR'")
    assert client.get("/api/watch/state", headers=headers).status_code == 401
    with get_db() as conn:
        conn.execute("UPDATE participantes SET papel = 'ADMIN'")
        conn.execute("UPDATE quadras SET atualizado_em = '2000-01-01T00:00:00+00:00'")
    assert client.get("/api/watch/state", headers=headers).status_code == 401


def test_concurrent_approval_only_consumes_code_once(client):
    court = prepare(client)
    _, _, code = pairing(client)
    cookie = client.cookies.get(SESSION_COOKIE)

    def approve(_):
        return client.post(
            f"/api/quadras/{court['id']}/watch/approve",
            json={"code": code},
            headers={"x-session-id": cookie},
        ).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(approve, range(2))) == [200, 400]


def test_restarting_server_preserves_link(client):
    court = prepare(client)
    _, headers = link(client, court)
    from app.db import init_db_sync

    init_db_sync()
    assert (
        client.get("/api/watch/session", headers=headers).json()["status"] == "linked"
    )


@pytest.mark.asyncio
async def test_multiple_connections_count_as_one_participant():
    class Socket:
        async def accept(self):
            pass

    one, two = Socket(), Socket()
    await hub.connect("multi-test", one, "eli")
    await hub.connect("multi-test", two, "eli", "watch")
    assert await hub.participantes_online("multi-test") == {"eli"}
    await hub.disconnect("multi-test", one)
    assert await hub.participantes_online("multi-test") == {"eli"}
    await hub.disconnect("multi-test", two)
    assert await hub.participantes_online("multi-test") == set()


def test_owner_secret_and_device_token_do_not_appear_in_logs(client, caplog):
    import logging

    caplog.set_level(logging.INFO)
    court = prepare(client)
    token, _ = link(client, court)
    assert settings.owner_secret not in caplog.text
    assert token not in caplog.text


def test_owner_cannot_enable_spectator_or_different_public_name(client):
    court = client.post("/api/quadras", json={"apelido": "Outra pessoa"}).json()
    response = client.post(
        "/api/owner/watch-access",
        json={"participant_id": court["participante"]["id"]},
        headers={"x-owner-secret": settings.owner_secret},
    )
    assert response.status_code == 409


def test_schema_upgrade_preserves_existing_events(client):
    from app.db import init_db_sync

    court = prepare(client)
    assert (
        client.post(
            f"/api/quadras/{court['id']}/pontos",
            json={"equipe": "A"},
            headers={"x-control-version": "1"},
        ).status_code
        == 201
    )
    with get_db() as conn:
        before = [
            dict(row) for row in conn.execute("SELECT * FROM eventos ORDER BY seq")
        ]
        conn.execute("DROP TABLE watch_devices")
        conn.execute("DROP TABLE watch_grants")
    init_db_sync()
    with get_db() as conn:
        after = [
            dict(row) for row in conn.execute("SELECT * FROM eventos ORDER BY seq")
        ]
    assert before == after
