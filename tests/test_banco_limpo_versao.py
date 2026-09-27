from pathlib import Path

import httpx
import pytest
from httpx import ASGITransport

from app import db as db_module
from app.config import settings
from app.db import get_db, init_db, init_db_sync
from app.main import app
from app.quadras import criar_quadra_sync, listar_quadras_sync


def test_banco_novo_inicia_sem_nenhuma_quadra(tmp_path: Path):
    """
    Garante que o banco recém-criado inicie 100% vazio (zero quadras).
    Nenhuma quadra prévia de fixture ou arena deve existir.
    """
    db_file = str(tmp_path / "banco_limpo.db")
    settings.db_path = db_file

    init_db_sync(db_file)

    quadras = listar_quadras_sync(db_file)
    assert quadras == []

    with get_db(db_file) as conn:
        (total_quadras,) = conn.execute("SELECT COUNT(*) FROM quadras").fetchone()
        assert total_quadras == 0
        (total_partidas,) = conn.execute("SELECT COUNT(*) FROM partidas").fetchone()
        assert total_partidas == 0
        (total_participantes,) = conn.execute(
            "SELECT COUNT(*) FROM participantes"
        ).fetchone()
        assert total_participantes == 0

        # Confere versão gravada em app_meta
        row_versao = conn.execute(
            "SELECT valor FROM app_meta WHERE chave = 'versao'"
        ).fetchone()
        assert row_versao is not None
        assert row_versao["valor"] == settings.version


def test_versao_nova_sem_mudar_schema_preserva_banco(tmp_path: Path):
    """CV5.DS1.TS3: release sem mudança de tabela mantém salas e recibos."""
    db_file = str(tmp_path / "placar_versao.db")
    settings.db_path = db_file
    settings.version = "0.4.1"
    init_db_sync(db_file)
    criar_quadra_sync(db_file, apelido="Admin", session_id="sessao-1", nome="Quadra")

    settings.version = "0.4.2"
    init_db_sync(db_file)

    assert len(listar_quadras_sync(db_file)) == 1
    with get_db(db_file) as conn:
        row = conn.execute(
            "SELECT valor FROM app_meta WHERE chave = 'versao'"
        ).fetchone()
        assert row["valor"] == "0.4.2"


def test_mudanca_de_schema_limpa_banco_completamente(tmp_path: Path, monkeypatch):
    """
    Dado um banco com quadras gravado por outro schema,
    quando o servidor inicializa com o schema novo,
    então o banco é apagado e recriado limpo.
    """
    db_file = str(tmp_path / "placar_migracao.db")
    settings.db_path = db_file
    init_db_sync(db_file)
    criar_quadra_sync(db_file, apelido="Admin", session_id="sessao-1", nome="Velha")
    assert len(listar_quadras_sync(db_file)) == 1

    monkeypatch.setattr(db_module, "SCHEMA_VERSAO", "schema-novo")
    init_db_sync(db_file)

    assert listar_quadras_sync(db_file) == []
    with get_db(db_file) as conn:
        (total,) = conn.execute("SELECT COUNT(*) FROM participantes").fetchone()
        assert total == 0
        row = conn.execute(
            "SELECT valor FROM app_meta WHERE chave = 'schema'"
        ).fetchone()
        assert row["valor"] == "schema-novo"


@pytest.mark.asyncio
async def test_rotas_legadas_de_arenas_retornam_404(tmp_path: Path):
    """
    Garante que todos os endpoints legados de arenas foram removidos e respondem 404.
    """
    db_file = str(tmp_path / "teste_rotas_arenas.db")
    settings.db_path = db_file
    await init_db(db_file)

    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        r_get = await client.get("/api/arenas")
        assert r_get.status_code == 404

        r_post = await client.post("/api/arenas", json={"nome": "Arena Inexistente"})
        assert r_post.status_code in (404, 405)

        r_quadras = await client.get("/api/arenas/qualquer-id/quadras")
        assert r_quadras.status_code == 404
