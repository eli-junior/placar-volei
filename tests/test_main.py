import sqlite3
from pathlib import Path

import httpx
import pytest
from httpx import ASGITransport

from app.config import settings
from app.db import init_db_sync
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == settings.version


def test_nova_versao_apaga_e_recria_banco(tmp_path: Path):
    """Quando o app detecta banco de versão anterior, ele apaga e cria um novo."""
    db_file = str(tmp_path / "test_version_wipe.db")
    settings.version = "0.1.0"
    init_db_sync(db_file)

    # Insere dados que devem sumir na troca de versão
    with sqlite3.connect(db_file) as conn:
        conn.execute(
            "INSERT INTO quadras (id, nome, criado_em, atualizado_em) VALUES ('99999', 'Quadra Antiga', '2026-01-01', '2026-01-01')"
        )
        conn.commit()

    # Sobe nova versão "0.2.0"
    settings.version = "0.2.0"
    init_db_sync(db_file)

    # Confere que o banco foi recriado e o dado antigo foi apagado
    with sqlite3.connect(db_file) as conn:
        conn.row_factory = sqlite3.Row
        quadras = conn.execute("SELECT * FROM quadras WHERE id = '99999'").fetchall()
        assert len(quadras) == 0

        meta = conn.execute(
            "SELECT valor FROM app_meta WHERE chave = 'versao'"
        ).fetchone()
        assert meta["valor"] == "0.2.0"


@pytest.mark.asyncio
async def test_serve_spa_root():
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert "Placar Vôlei" in response.text
        assert '<div id="app"></div>' in response.text


@pytest.mark.asyncio
async def test_serve_spa_quadra_route():
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/quadra/qualquer-id-de-quadra")
        assert response.status_code == 200
        assert "Placar Vôlei" in response.text
