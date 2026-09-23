"""Pontuação pelo relógio: participante próprio, delegação, recibo e idempotência.

CV3.DS1.US2, revisão 3: o relógio é o participante "Eli (Relógio)" e pontua
quando o admin passa o controle para ele, pelas mesmas regras do site.
"""

import json
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.db import get_db
from app.main import app
from app.rate_limit import owner_rate_limiter
from app.sucessao import verificar_controle_ocioso_sync, verificar_sucessao_quadra_sync
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


def estado(client, headers):
    return client.get("/api/watch/state", headers=headers).json()


def relogio_id(client, headers):
    return client.get("/api/watch/session", headers=headers).json()["participant_id"]


def comando(client, headers, equipe="A", *, base=None):
    base = base or estado(client, headers)
    body = {
        "id": str(uuid.uuid4()),
        "partida_id": base["partida_id"],
        "controle_versao": base["quadra"]["controle_versao"],
        "equipe": equipe,
    }
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


@pytest.fixture
def sala(client):
    """Sala com Eli ADMIN, relógio vinculado e controle delegado ao relógio."""
    court = prepare(client)
    _, headers = link(client, court)
    delegar(client, court, headers)
    return court, headers


def eventos(court_id, tipo):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM eventos WHERE quadra_id = ? AND tipo = ? ORDER BY seq",
            (court_id, tipo),
        ).fetchall()


def envelhecer(participante_id, minutos=10):
    passado = (datetime.now(UTC) - timedelta(minutes=minutos)).isoformat()
    with get_db() as conn:
        conn.execute(
            "UPDATE participantes SET ultimo_visto_em = ? WHERE id = ?",
            (passado, participante_id),
        )


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
            "SELECT status, evento_seq FROM watch_recibos ORDER BY criado_em"
        ).fetchall()
    assert [r["status"] for r in recibos] == ["APLICADO"] * 3
    # Cada recibo aponta para o seu evento: o lance é auditável.
    assert [r["evento_seq"] for r in recibos] == [
        e["seq"] for e in eventos(court["id"], "PONTO_MARCADO")
    ]
    # O autor dos pontos é o participante do relógio.
    autores = {e["autor_id"] for e in eventos(court["id"], "PONTO_MARCADO")}
    assert autores == {relogio_id(client, headers)}


def test_watch_without_control_only_follows(client):
    court = prepare(client)
    _, headers = link(client, court)
    response, body = comando(client, headers, "A")
    assert response.status_code == 200
    assert response.json()["recibo"]["status"] == "RECUSADO"
    assert not eventos(court["id"], "PONTO_MARCADO")
    # Delegar depois não transforma a recusa em ponto no reenvio.
    delegar(client, court, headers)
    again = client.post("/api/watch/comandos", json=body, headers=headers)
    assert again.json()["recibo"]["status"] == "RECUSADO"
    assert not eventos(court["id"], "PONTO_MARCADO")


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
        "controle_versao": base["quadra"]["controle_versao"],
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


def test_site_cannot_score_while_watch_holds_control(client, sala):
    court, _ = sala
    versao = str(client.get(f"/api/quadras/{court['id']}").json()["controle_versao"])
    response = client.post(
        f"/api/quadras/{court['id']}/pontos",
        json={"equipe": "A"},
        headers={"x-control-version": versao},
    )
    assert response.status_code == 403
    assert not eventos(court["id"], "PONTO_MARCADO")


def test_admin_takes_control_back_and_pending_is_rejected(client, sala):
    court, headers = sala
    base = estado(client, headers)
    assumir = client.post(f"/api/quadras/{court['id']}/controle/assumir")
    assert assumir.status_code == 200
    response, _ = comando(client, headers, "A", base=base)
    assert response.json()["recibo"]["status"] == "RECUSADO"
    assert not eventos(court["id"], "PONTO_MARCADO")


def test_command_for_previous_match_is_not_applied_to_new_one(client, sala):
    court, headers = sala
    old = estado(client, headers)
    for _ in range(12):
        comando(client, headers, "A", base=old)
    assert client.post(f"/api/quadras/{court['id']}/reiniciar").status_code == 200
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


def test_watch_control_is_not_returned_for_absence(client, sala):
    court, headers = sala
    watch = relogio_id(client, headers)
    envelhecer(watch)
    # Admin online, relógio ausente há 10 minutos: o controle fica com o relógio.
    admin = court["participante"]["id"]
    assert (
        verificar_controle_ocioso_sync(settings.db_path, court["id"], {admin}, 0)
        is None
    )
    assert client.get(f"/api/quadras/{court['id']}").json()["controle_id"] == watch


def test_connected_watch_keeps_owner_as_admin(client, sala):
    court, headers = sala
    watch = relogio_id(client, headers)
    envelhecer(court["participante"]["id"])
    # Telefone sumido há 10 min, mas o relógio do Eli está conectado.
    assert (
        verificar_sucessao_quadra_sync(settings.db_path, court["id"], {watch}, 60)
        is None
    )
    # Relógio visto há pouco também segura; sumido também, a regra de sempre vale.
    assert (
        verificar_sucessao_quadra_sync(settings.db_path, court["id"], set(), 60) is None
    )
    envelhecer(watch)
    assert (
        verificar_sucessao_quadra_sync(settings.db_path, court["id"], set(), 60)
        is not None
    )


def test_revoking_watch_removes_it_and_returns_control_to_owner(client, sala):
    court, headers = sala
    devices = client.get(f"/api/quadras/{court['id']}/watch").json()["devices"]
    revoked = client.delete(f"/api/quadras/{court['id']}/watch/{devices[0]['id']}")
    assert revoked.status_code == 200
    sala_atual = client.get(f"/api/quadras/{court['id']}").json()
    assert sala_atual["controle_id"] == court["participante"]["id"]
    participantes = client.get(f"/api/quadras/{court['id']}/participantes").json()
    assert [p["apelido"] for p in participantes["participantes"]] == ["Eli"]
    itens = client.get(f"/api/quadras/{court['id']}/linha-do-tempo").json()
    descricoes = [i["descricao"] for i in itens.get("itens", itens)]
    assert "Controle devolvido para Eli: relógio desvinculado" in descricoes
    # O site volta a pontuar; o relógio revogado não.
    assert (
        client.post(
            f"/api/quadras/{court['id']}/pontos",
            json={"equipe": "A"},
            headers={"x-control-version": str(sala_atual["controle_versao"])},
        ).status_code
        == 201
    )
    base = {"partida_id": sala_atual["partida_id"], "quadra": sala_atual}
    assert comando(client, headers, "A", base=base)[0].status_code == 401


def test_relink_keeps_watch_participant_and_delegation(client, sala):
    court, headers = sala
    watch = relogio_id(client, headers)
    _, new_headers = link(client, court)
    assert relogio_id(client, new_headers) == watch
    assert client.get(f"/api/quadras/{court['id']}").json()["controle_id"] == watch
    assert comando(client, new_headers, "B")[0].status_code == 201


def test_watch_point_reaches_browser_by_broadcast(client, sala):
    court, headers = sala
    with client.websocket_connect(f"/ws/{court['id']}") as phone:
        assert phone.receive_json()["tipo"] == "ESTADO_INICIAL"
        comando(client, headers, "B")
        while (msg := phone.receive_json())["tipo"] != "PLACAR_ATUALIZADO":
            pass
        assert msg["payload"]["estado_partida"]["pontos_b"] == 1
        assert msg["payload"]["comando_id"]


def test_receipt_survives_restart(client, sala):
    court, headers = sala
    _, body = comando(client, headers, "A")
    with TestClient(app) as restarted:
        again = restarted.post("/api/watch/comandos", json=body, headers=headers)
    assert again.status_code == 200
    assert again.json()["recibo"]["status"] == "APLICADO"
    assert len(eventos(court["id"], "PONTO_MARCADO")) == 1
