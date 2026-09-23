"""Pontuação pelo relógio: chave da sala, recibo durável e idempotência (CV3.DS1.US2)."""

import json
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.db import get_db
from app.main import app
from app.rate_limit import owner_rate_limiter
from app.watch import approval_limit, creation_limit
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


def ligar(client, court, ativo=True):
    return client.post(
        f"/api/quadras/{court['id']}/controle/relogio", json={"ativo": ativo}
    )


def estado(client, headers):
    return client.get("/api/watch/state", headers=headers).json()


def comando(client, headers, equipe="A", *, id=None, base=None):
    base = base or estado(client, headers)
    body = {
        "id": id or str(uuid.uuid4()),
        "partida_id": base["partida_id"],
        "relogio_versao": base["quadra"]["relogio_versao"],
        "equipe": equipe,
    }
    return client.post("/api/watch/comandos", json=body, headers=headers), body


@pytest.fixture
def sala(client):
    """Sala com eli ADMIN, relógio vinculado e chave ligada."""
    court = prepare(client)
    _, headers = link(client, court)
    assert ligar(client, court).status_code == 200
    return court, headers


def eventos(court_id, tipo):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM eventos WHERE quadra_id = ? AND tipo = ? ORDER BY seq",
            (court_id, tipo),
        ).fetchall()


def test_sequence_a_a_b_applies_three_points_with_receipts(client, sala):
    court, headers = sala
    for equipe in "AAB":
        response, _ = comando(client, headers, equipe)
        assert response.status_code == 201
        assert response.json()["recibo"]["status"] == "APLICADO"
    final = response.json()["estado"]["estado_partida"]
    assert (final["pontos_a"], final["pontos_b"]) == (2, 1)
    assert len(eventos(court["id"], "PONTO_MARCADO")) == 3
    with get_db() as conn:
        recibos = conn.execute(
            "SELECT status, evento_seq FROM watch_comandos ORDER BY criado_em"
        ).fetchall()
    assert [r["status"] for r in recibos] == ["APLICADO"] * 3
    # Cada recibo aponta para o seu evento: o lance é auditável.
    assert [r["evento_seq"] for r in recibos] == [
        e["seq"] for e in eventos(court["id"], "PONTO_MARCADO")
    ]
    # O ponto do relógio é do participante eli, único na sala.
    autores = {e["autor_id"] for e in eventos(court["id"], "PONTO_MARCADO")}
    assert autores == {court["participante"]["id"]}


def test_resend_returns_original_receipt_without_new_event(client, sala):
    court, headers = sala
    first, body = comando(client, headers, "B")
    again = client.post("/api/watch/comandos", json=body, headers=headers)
    assert again.status_code == 200
    assert again.json()["recibo"] == first.json()["recibo"]
    assert again.json()["estado"]["estado_partida"]["pontos_b"] == 1
    assert len(eventos(court["id"], "PONTO_MARCADO")) == 1


def test_same_id_with_different_content_is_rejected(client, sala):
    court, headers = sala
    _, body = comando(client, headers, "A")
    response = client.post(
        "/api/watch/comandos", json={**body, "equipe": "B"}, headers=headers
    )
    assert response.status_code == 409
    assert len(eventos(court["id"], "PONTO_MARCADO")) == 1


def test_concurrent_resend_applies_once(client, sala):
    court, headers = sala
    base = estado(client, headers)
    body = {
        "id": str(uuid.uuid4()),
        "partida_id": base["partida_id"],
        "relogio_versao": base["quadra"]["relogio_versao"],
        "equipe": "A",
    }
    with ThreadPoolExecutor(4) as pool:
        codes = list(
            pool.map(
                lambda _: (
                    client.post(
                        "/api/watch/comandos", json=body, headers=headers
                    ).status_code
                ),
                range(4),
            )
        )
    assert sorted(codes) == [200, 200, 200, 201]
    assert len(eventos(court["id"], "PONTO_MARCADO")) == 1


def test_rapid_taps_keep_order_and_count(client, sala):
    court, headers = sala
    base = estado(client, headers)
    for equipe in "ABBAB":
        assert comando(client, headers, equipe, base=base)[0].status_code == 201
    assert [
        json.loads(e["payload"])["equipe"]
        for e in eventos(court["id"], "PONTO_MARCADO")
    ] == list("ABBAB")


def test_browser_cannot_score_or_undo_while_watch_controls(client, sala):
    court, headers = sala
    comando(client, headers, "A")
    versao = str(client.get(f"/api/quadras/{court['id']}").json()["controle_versao"])
    for rota, body in (("pontos", {"equipe": "A"}), ("desfazer", None)):
        response = client.post(
            f"/api/quadras/{court['id']}/{rota}",
            json=body,
            headers={"x-control-version": versao},
        )
        assert response.status_code == 409
        assert "relógio" in response.json()["detail"]
    # Configurar continua liberado para o admin.
    assert (
        client.post(
            f"/api/quadras/{court['id']}/configurar", json={"alvo": 15}
        ).status_code
        == 200
    )
    assert len(eventos(court["id"], "PONTO_MARCADO")) == 1


def test_watch_command_rejected_with_receipt_when_switch_off(client):
    court = prepare(client)
    _, headers = link(client, court)
    response, body = comando(client, headers, "A")
    assert response.status_code == 200
    assert response.json()["recibo"]["status"] == "RECUSADO"
    assert "telefone" in response.json()["recibo"]["detalhe"]
    assert not eventos(court["id"], "PONTO_MARCADO")
    # Ligar depois não transforma a recusa em ponto no reenvio.
    assert ligar(client, court).status_code == 200
    again = client.post("/api/watch/comandos", json=body, headers=headers)
    assert again.json()["recibo"]["status"] == "RECUSADO"
    assert not eventos(court["id"], "PONTO_MARCADO")


def test_toggle_invalidates_pending_commands(client, sala):
    court, headers = sala
    base = estado(client, headers)
    assert ligar(client, court, False).status_code == 200
    assert ligar(client, court, True).status_code == 200
    response, _ = comando(client, headers, "A", base=base)
    assert response.json()["recibo"]["status"] == "RECUSADO"
    assert not eventos(court["id"], "PONTO_MARCADO")


def test_control_transfer_on_site_does_not_affect_watch(client, sala):
    court, headers = sala
    base = estado(client, headers)
    with get_db() as conn:
        conn.execute(
            "UPDATE quadras SET controle_versao = controle_versao + 5 WHERE id = ?",
            (court["id"],),
        )
    response, _ = comando(client, headers, "A", base=base)
    assert response.json()["recibo"]["status"] == "APLICADO"


def test_command_for_previous_match_is_not_applied_to_new_one(client, sala):
    court, headers = sala
    old = estado(client, headers)
    ligar(client, court, False)
    versao = client.get(f"/api/quadras/{court['id']}").json()["controle_versao"]
    for _ in range(12):
        client.post(
            f"/api/quadras/{court['id']}/pontos",
            json={"equipe": "A"},
            headers={"x-control-version": str(versao)},
        )
    assert client.post(f"/api/quadras/{court['id']}/reiniciar").status_code == 200
    ligar(client, court, True)
    old["quadra"]["relogio_versao"] = estado(client, headers)["quadra"][
        "relogio_versao"
    ]
    response, _ = comando(client, headers, "A", base=old)
    assert response.json()["recibo"]["status"] == "RECUSADO"
    assert "nova partida" in response.json()["recibo"]["detalhe"].lower()
    assert response.json()["estado"]["estado_partida"]["pontos_a"] == 0


def test_finished_match_rejects_watch_point(client, sala):
    court, headers = sala
    base = estado(client, headers)
    for _ in range(12):
        comando(client, headers, "A", base=base)
    assert estado(client, headers)["estado_partida"]["encerrada"] is True
    response, _ = comando(client, headers, "A", base=base)
    assert response.json()["recibo"]["status"] == "RECUSADO"
    assert "encerrada" in response.json()["recibo"]["detalhe"]
    assert len(eventos(court["id"], "PONTO_MARCADO")) == 12


def test_switch_on_requires_linked_watch(client):
    court = prepare(client)
    response = ligar(client, court)
    assert response.status_code == 403
    assert client.get(f"/api/quadras/{court['id']}").json()["controle_relogio"] is None


def test_spectator_cannot_toggle_and_admin_can_turn_off(client, sala):
    court, _ = sala
    other = TestClient(app)
    other.post(f"/api/quadras/{court['id']}/entrar", json={"apelido": "rafa"})
    assert (
        other.post(
            f"/api/quadras/{court['id']}/controle/relogio", json={"ativo": False}
        ).status_code
        == 403
    )
    assert ligar(client, court, False).status_code == 200
    sala_atual = client.get(f"/api/quadras/{court['id']}").json()
    assert sala_atual["controle_relogio"] is None
    itens = client.get(f"/api/quadras/{court['id']}/linha-do-tempo").json()
    descricoes = [i["descricao"] for i in itens.get("itens", itens)]
    assert "Placar passou a ser controlado pelo relógio de eli" in descricoes
    assert "Placar voltou a ser controlado pelo telefone" in descricoes


def test_revoking_watch_turns_switch_off_and_site_scores_again(client, sala):
    court, headers = sala
    devices = client.get(f"/api/quadras/{court['id']}/watch").json()["devices"]
    client.delete(f"/api/quadras/{court['id']}/watch/{devices[0]['id']}")
    sala_atual = client.get(f"/api/quadras/{court['id']}").json()
    assert sala_atual["controle_relogio"] is None
    assert (
        client.post(
            f"/api/quadras/{court['id']}/pontos",
            json={"equipe": "A"},
            headers={"x-control-version": str(sala_atual["controle_versao"])},
        ).status_code
        == 201
    )
    assert (
        client.post(
            "/api/watch/comandos",
            json={
                "id": str(uuid.uuid4()),
                "partida_id": sala_atual["partida_id"],
                "relogio_versao": 0,
                "equipe": "A",
            },
            headers=headers,
        ).status_code
        == 401
    )


def test_watch_point_reaches_browser_by_broadcast(client, sala):
    court, headers = sala
    with client.websocket_connect(f"/ws/{court['id']}") as phone:
        assert phone.receive_json()["tipo"] == "ESTADO_INICIAL"
        comando(client, headers, "B")
        while (msg := phone.receive_json())["tipo"] != "PLACAR_ATUALIZADO":
            pass
        assert msg["payload"]["estado_partida"]["pontos_b"] == 1
        assert msg["payload"]["comando_id"]
        assert (
            msg["payload"]["quadra"]["controle_relogio"] == court["participante"]["id"]
        )


def test_receipt_survives_restart(client, sala):
    court, headers = sala
    _, body = comando(client, headers, "A")
    with TestClient(app) as restarted:
        again = restarted.post("/api/watch/comandos", json=body, headers=headers)
    assert again.status_code == 200
    assert again.json()["recibo"]["status"] == "APLICADO"
    assert len(eventos(court["id"], "PONTO_MARCADO")) == 1
