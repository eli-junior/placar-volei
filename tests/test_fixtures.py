import os
from pathlib import Path

import httpx
import pytest
from httpx import ASGITransport

from app.config import settings
from app.db import get_db, init_db, init_db_sync
from app.eventos import TipoEvento
from app.fixtures import (
    adicionar_arena_fixture_sync,
    adicionar_quadra_fixture_sync,
    carregar_fixtures_arenas,
    salvar_fixtures_arenas,
)
from app.main import app
from app.quadras import listar_arenas_sync, listar_quadras_sync


def test_carregar_e_salvar_fixtures_basico(tmp_path: Path):
    fixture_file = str(tmp_path / "fixtures.json")

    # Arquivo inexistente retorna vazio
    assert carregar_fixtures_arenas(fixture_file) == []

    # Salva fixture
    dados = [
        {"nome": "Arena T9", "quadras": ["Quadra 1", "Quadra 2"]},
        {"nome": "CT Areia", "quadras": [{"nome": "Quadra Central"}]},
    ]
    salvar_fixtures_arenas(fixture_file, dados)

    # Carrega e valida normalização
    carregados = carregar_fixtures_arenas(fixture_file)
    assert len(carregados) == 2
    assert carregados[0]["nome"] == "Arena T9"
    assert carregados[0]["quadras"] == ["Quadra 1", "Quadra 2"]
    assert carregados[1]["nome"] == "CT Areia"
    assert carregados[1]["quadras"] == ["Quadra Central"]


def test_carregar_fixtures_arquivo_invalido(tmp_path: Path):
    fixture_file = str(tmp_path / "invalid.json")

    with open(fixture_file, "w", encoding="utf-8") as f:
        f.write("{nao e um json valido")
    assert carregar_fixtures_arenas(fixture_file) == []

    with open(fixture_file, "w", encoding="utf-8") as f:
        f.write("   ")
    assert carregar_fixtures_arenas(fixture_file) == []


def test_adicionar_arena_e_quadra_fixture_sync(tmp_path: Path):
    fixture_file = str(tmp_path / "defaultArenas.json")

    adicionar_arena_fixture_sync(fixture_file, "Arena Aricanduva")
    # Tentar adicionar de novo não duplica
    adicionar_arena_fixture_sync(fixture_file, "Arena Aricanduva")

    arenas = carregar_fixtures_arenas(fixture_file)
    assert len(arenas) == 1
    assert arenas[0]["nome"] == "Arena Aricanduva"
    assert arenas[0]["quadras"] == []

    # Adiciona quadras
    adicionar_quadra_fixture_sync(fixture_file, "Arena Aricanduva", "Quadra 1")
    adicionar_quadra_fixture_sync(
        fixture_file, "Arena Aricanduva", "Quadra 1"
    )  # Idempotente
    adicionar_quadra_fixture_sync(fixture_file, "Arena Aricanduva", "Quadra 2")

    arenas = carregar_fixtures_arenas(fixture_file)
    assert len(arenas) == 1
    assert arenas[0]["quadras"] == ["Quadra 1", "Quadra 2"]


def test_sincronizar_fixtures_para_db_sync(tmp_path: Path):
    db_file = str(tmp_path / "teste_sync.db")
    fixture_file = str(tmp_path / "defaultArenas.json")

    dados = [
        {"nome": "T9 Beach Club", "quadras": ["Quadra 01", "Tio Cleo"]},
        {"nome": "Tio Cleo", "quadras": ["So tem uma"]},
    ]
    salvar_fixtures_arenas(fixture_file, dados)

    # Inicializa banco limpo apontando para a fixture
    init_db_sync(db_file, fixture_file)

    arenas = listar_arenas_sync(db_file)
    assert len(arenas) == 2
    nomes_arenas = {a["nome"] for a in arenas}
    assert "T9 Beach Club" in nomes_arenas
    assert "Tio Cleo" in nomes_arenas

    quadras = listar_quadras_sync(db_file)
    assert len(quadras) == 3
    nomes_quadras = {q["nome"] for q in quadras}
    assert "Quadra 01" in nomes_quadras
    assert "Tio Cleo" in nomes_quadras
    assert "So tem uma" in nomes_quadras

    # Cada quadra deve ter uma partida em andamento e evento PARTIDA_INICIADA
    for q in quadras:
        with get_db(db_file) as conn:
            partida = conn.execute(
                "SELECT id FROM partidas WHERE quadra_id = ?", (q["id"],)
            ).fetchone()
            assert partida is not None
            partida_id = partida["id"]
            evs = conn.execute(
                "SELECT tipo FROM eventos WHERE partida_id = ?", (partida_id,)
            ).fetchall()
            assert len(evs) == 1
            assert evs[0]["tipo"] == TipoEvento.PARTIDA_INICIADA


def test_sincronizacao_idempotente(tmp_path: Path):
    db_file = str(tmp_path / "teste_idempotente.db")
    fixture_file = str(tmp_path / "defaultArenas.json")

    salvar_fixtures_arenas(fixture_file, [{"nome": "Arena Idemp", "quadras": ["Q1"]}])

    # Executa duas vezes
    init_db_sync(db_file, fixture_file)
    init_db_sync(db_file, fixture_file)

    arenas = listar_arenas_sync(db_file)
    assert len(arenas) == 1
    quadras = listar_quadras_sync(db_file)
    assert len(quadras) == 1


@pytest.mark.asyncio
async def test_api_criar_arena_e_quadra_atualiza_fixture(tmp_path: Path):
    db_file = str(tmp_path / "teste_api.db")
    fixture_file = str(tmp_path / "defaultArenas_api.json")

    settings.db_path = db_file
    settings.default_arenas_file = fixture_file
    await init_db(db_file, fixture_file)

    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Cria arena via API
        resp_a = await client.post("/api/arenas", json={"nome": "Arena Nova API"})
        assert resp_a.status_code == 201
        arena_id = resp_a.json()["id"]

        # Confere que a fixture no disco já tem a arena
        arenas_disk = carregar_fixtures_arenas(fixture_file)
        assert len(arenas_disk) == 1
        assert arenas_disk[0]["nome"] == "Arena Nova API"
        assert arenas_disk[0]["quadras"] == []

        # Cria quadra via API
        resp_q = await client.post(
            f"/api/arenas/{arena_id}/quadras", json={"nome": "Quadra Ouro"}
        )
        assert resp_q.status_code == 201

        # Confere que a fixture no disco foi atualizada com a nova quadra
        arenas_disk = carregar_fixtures_arenas(fixture_file)
        assert len(arenas_disk) == 1
        assert arenas_disk[0]["quadras"] == ["Quadra Ouro"]


@pytest.mark.asyncio
async def test_recriar_banco_recupera_arenas_e_quadras_automaticamente(tmp_path: Path):
    """
    Cenário BDD:
    Dado que o arquivo placar.db foi apagado
    Quando a aplicação inicia e executa init_db
    Então a tabela arenas contém as arenas de defaultArenas.json
    E cada quadra configurada é criada com sua respectiva partida ativa
    """
    db_file = str(tmp_path / "placar_reinicio.db")
    fixture_file = str(tmp_path / "defaultArenas.json")

    salvar_fixtures_arenas(
        fixture_file,
        [
            {"nome": "Clube Pinheiros", "quadras": ["Areia 1", "Areia 2"]},
            {"nome": "Vila Lobos", "quadras": ["Quadra Central"]},
        ],
    )

    settings.db_path = db_file
    settings.default_arenas_file = fixture_file

    # 1. Primeiro ciclo de vida do banco
    await init_db(db_file, fixture_file)
    arenas_ini = listar_arenas_sync(db_file)
    assert len(arenas_ini) == 2

    # Insere participante e ponto para simular uso
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        quadras = listar_quadras_sync(db_file)
        q1_id = quadras[0]["id"]

        await client.post(f"/api/quadras/{q1_id}/entrar", json={"apelido": "Jogador 1"})
        await client.post(
            f"/api/quadras/{q1_id}/pontos",
            headers={"x-control-version": "1"},
            json={"equipe": "A"},
        )

    # 2. Simula apagar o banco de dados completamente (reset de banco)
    import gc

    gc.collect()
    os.remove(db_file)
    # Remove também arquivos wal/shm se existirem
    for ext in ["-wal", "-shm"]:
        if os.path.exists(db_file + ext):
            os.remove(db_file + ext)
    assert not os.path.exists(db_file)

    # 3. Reinicia a aplicação (novo init_db)
    await init_db(db_file, fixture_file)

    # Arenas e quadras foram recriadas automaticamente!
    arenas_apos = listar_arenas_sync(db_file)
    assert len(arenas_apos) == 2
    quadras_apos = listar_quadras_sync(db_file)
    assert len(quadras_apos) == 3

    # Participantes anteriores foram zerados (não existem mais no novo banco)
    with get_db(db_file) as conn:
        (total_parts,) = conn.execute("SELECT COUNT(*) FROM participantes").fetchone()
        assert total_parts == 0
