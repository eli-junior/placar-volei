"""CV5.DS1.TS3: sala expirada não deixa rastro; id inválido não cria estado."""

from datetime import UTC, datetime, timedelta

import pytest
from starlette.websockets import WebSocketDisconnect

from app import eventos
from app.config import settings
from app.db import get_db
from app.quadras import limpar_quadras_expiradas_sync, listar_quadras_sync
from tests.watch_support import link, prepare


def _envelhecer(quadra_id):
    velho = (datetime.now(UTC) - timedelta(hours=2)).isoformat()
    with get_db() as conn:
        conn.execute(
            "UPDATE quadras SET atualizado_em = ? WHERE id = ?", (velho, quadra_id)
        )


def test_ws_com_id_invalido_fecha_sem_criar_lock(client):
    antes = set(eventos._quadra_locks)
    with (
        pytest.raises(WebSocketDisconnect) as fechado,
        client.websocket_connect("/ws/abc") as ws,
    ):
        ws.receive_json()
    assert fechado.value.code == 4404
    assert set(eventos._quadra_locks) == antes


def test_sala_expirada_nao_deixa_linha_em_nenhuma_tabela(client):
    court = prepare(client)
    _, headers = link(client, court)
    client.post(
        "/api/watch/comandos",
        headers=headers,
        json={"id": "cmd-1", "partida_id": "x", "equipe": "A", "controle_versao": 0},
    )
    eventos.get_quadra_lock(court["id"])
    _envelhecer(court["id"])

    assert limpar_quadras_expiradas_sync(settings.db_path) == 1

    with get_db() as conn:
        tabelas = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name != 'app_meta'"
            )
        ]
        for tabela in tabelas:
            colunas = [c[1] for c in conn.execute(f"PRAGMA table_info({tabela})")]
            coluna = (
                "quadra_id"
                if "quadra_id" in colunas
                else "id"
                if tabela == "quadras"
                else None
            )
            if coluna:
                (n,) = conn.execute(
                    f"SELECT COUNT(*) FROM {tabela} WHERE {coluna} = ?", (court["id"],)
                ).fetchone()
                assert n == 0, tabela
    assert court["id"] not in eventos._quadra_locks


def test_listagem_esconde_vencidas_sem_apagar(client):
    court = prepare(client)
    _envelhecer(court["id"])
    assert listar_quadras_sync(settings.db_path) == []
    with get_db() as conn:
        (n,) = conn.execute("SELECT COUNT(*) FROM quadras").fetchone()
    assert n == 1


def test_listagem_acompanha_o_placar(client):
    court = prepare(client)
    antes = listar_quadras_sync(settings.db_path)[0]["partida"]
    r = client.post(
        f"/api/quadras/{court['id']}/pontos",
        json={"equipe": "A"},
        headers={"x-control-version": "1"},
    )
    assert r.status_code == 201
    depois = listar_quadras_sync(settings.db_path)[0]["partida"]
    assert depois["pontos_a"] == antes["pontos_a"] + 1
