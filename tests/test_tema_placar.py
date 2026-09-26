"""CV4.DS2.US3 — tema do placar escolhido pelo administrador, por sala."""

import sqlite3
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.db import get_db, init_db, init_db_sync
from app.main import app as app_


@pytest.fixture(autouse=True)
async def setup_test_db(tmp_path: Path):
    db_file = str(tmp_path / "test_tema.db")
    settings.db_path = db_file
    await init_db(db_file)
    yield


def _cliente():
    return AsyncClient(transport=ASGITransport(app=app_), base_url="http://test")


@pytest.mark.asyncio
async def test_sala_nova_usa_esportivo_por_padrao():
    async with _cliente() as ac:
        resp = await ac.post("/api/quadras", json={"apelido": "Admin"})
        quadra_id = resp.json()["id"]
        snap = (await ac.get(f"/api/quadras/{quadra_id}")).json()
        assert snap["tema_placar"] == "esportivo"


@pytest.mark.asyncio
async def test_admin_troca_tema_isolado_sem_alterar_partida():
    async with _cliente() as ac:
        quadra_id = (await ac.post("/api/quadras", json={"apelido": "Admin"})).json()[
            "id"
        ]
        await ac.post(
            f"/api/quadras/{quadra_id}/pontos",
            headers={"x-control-version": "1"},
            json={"equipe": "A"},
        )
        resp = await ac.post(
            f"/api/quadras/{quadra_id}/configurar", json={"tema_placar": "classico"}
        )
        assert resp.status_code == 200
        snap = resp.json()
        assert snap["quadra"]["tema_placar"] == "classico"
        assert snap["estado_partida"]["pontos_a"] == 1

        releitura = (await ac.get(f"/api/quadras/{quadra_id}")).json()
        assert releitura["tema_placar"] == "classico"


@pytest.mark.asyncio
async def test_tema_persiste_em_nova_partida():
    async with _cliente() as ac:
        quadra_id = (
            await ac.post(
                "/api/quadras", json={"apelido": "Admin", "alvo": 1, "vantagem": False}
            )
        ).json()["id"]
        await ac.post(
            f"/api/quadras/{quadra_id}/configurar", json={"tema_placar": "classico"}
        )
        await ac.post(
            f"/api/quadras/{quadra_id}/pontos",
            headers={"x-control-version": "1"},
            json={"equipe": "A"},
        )
        resp = await ac.post(f"/api/quadras/{quadra_id}/reiniciar", json={})
        assert resp.status_code == 200
        assert resp.json()["quadra"]["tema_placar"] == "classico"
        assert resp.json()["estado_partida"]["pontos_a"] == 0


@pytest.mark.asyncio
async def test_tema_invalido_e_recusado():
    async with _cliente() as ac:
        quadra_id = (await ac.post("/api/quadras", json={"apelido": "Admin"})).json()[
            "id"
        ]
        resp = await ac.post(
            f"/api/quadras/{quadra_id}/configurar", json={"tema_placar": "neon"}
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_espectador_nao_troca_tema():
    async with _cliente() as admin:
        quadra_id = (
            await admin.post("/api/quadras", json={"apelido": "Admin"})
        ).json()["id"]
        async with _cliente() as outro:
            await outro.post(
                f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Espectador"}
            )
            resp = await outro.post(
                f"/api/quadras/{quadra_id}/configurar",
                json={"tema_placar": "classico"},
            )
            assert resp.status_code == 403
        snap = (await admin.get(f"/api/quadras/{quadra_id}")).json()
        assert snap["tema_placar"] == "esportivo"


def test_migracao_adiciona_coluna_em_banco_existente(tmp_path: Path):
    db_file = str(tmp_path / "legado.db")
    settings.db_path = db_file
    init_db_sync(db_file)
    conn = sqlite3.connect(db_file)
    conn.execute("ALTER TABLE quadras DROP COLUMN tema_placar")
    conn.commit()
    conn.close()

    init_db_sync(db_file)
    with get_db(db_file) as c:
        colunas = [r["name"] for r in c.execute("PRAGMA table_info(quadras)")]
    assert "tema_placar" in colunas
