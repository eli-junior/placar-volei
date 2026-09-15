from pathlib import Path

import httpx
import pytest
from httpx import ASGITransport

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


def test_atualizacao_de_versao_limpa_banco_completamente(tmp_path: Path):
    """
    Cenário BDD:
    Dado que existe um banco com quadras e participantes em versão anterior (ex: 0.4.1)
    Quando o servidor inicializa com uma nova versão (ex: 0.4.2)
    Então o banco anterior é totalmente apagado e recriado limpo (0 quadras).
    """
    db_file = str(tmp_path / "placar_migracao.db")
    settings.db_path = db_file
    settings.version = "0.4.1"

    # 1. Cria banco na versão 0.4.1 com quadras ativas
    init_db_sync(db_file)
    criar_quadra_sync(
        db_file, apelido="Admin", session_id="sessao-1", nome="Quadra Velha"
    )
    quadras_antigas = listar_quadras_sync(db_file)
    assert len(quadras_antigas) == 1

    # 2. Atualiza versão da aplicação para 0.4.2
    settings.version = "0.4.2"

    # 3. Inicializa o banco na nova versão
    init_db_sync(db_file)

    # 4. O banco deve estar 100% limpo, sem nenhuma quadra ativa!
    quadras_novas = listar_quadras_sync(db_file)
    assert quadras_novas == []

    with get_db(db_file) as conn:
        (total_quadras,) = conn.execute("SELECT COUNT(*) FROM quadras").fetchone()
        assert total_quadras == 0
        (total_participantes,) = conn.execute(
            "SELECT COUNT(*) FROM participantes"
        ).fetchone()
        assert total_participantes == 0
        row_versao = conn.execute(
            "SELECT valor FROM app_meta WHERE chave = 'versao'"
        ).fetchone()
        assert row_versao["valor"] == "0.4.2"


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
