"""Fixture e helpers comuns aos testes do relógio (CV3.DS1.TS1).

Registrado como plugin em `tests/conftest.py`: a fixture `client` vale
para os `test_watch_*.py`; os helpers são importados.
"""

import secrets
import uuid

import pytest
from fastapi.testclient import TestClient

from app.config import settings
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


def estado(client, headers):
    return client.get("/api/watch/state", headers=headers).json()


def relogio_id(client, headers):
    return client.get("/api/watch/session", headers=headers).json()["participant_id"]


def comando(client, headers, equipe="A", *, base=None, base_seq=None):
    base = base or estado(client, headers)
    body = {
        "id": str(uuid.uuid4()),
        "partida_id": base["partida_id"],
        "controle_versao": base["quadra"]["controle_versao"],
        "equipe": equipe,
    }
    if base_seq is not None:
        body["base_seq"] = base_seq
    return client.post("/api/watch/comandos", json=body, headers=headers), body


def delegar(client, court, headers):
    """Admin promove o relógio e passa o controle para ele (botões do site)."""
    watch = relogio_id(client, headers)
    base = f"/api/quadras/{court['id']}/participantes/{watch}"
    assert client.post(f"{base}/promover").status_code == 200
    # Passar o controle exige o relógio conectado.
    with client.websocket_connect(f"/ws/{court['id']}", headers=headers) as ws:
        ws.receive_json()
        assert client.post(f"{base}/controle").status_code == 200
    return watch
