import asyncio
import inspect
from pathlib import Path

import pytest

import app.eventos as eventos_module
from app.db import get_db, init_db
from app.eventos import (
    TipoEvento,
    append_evento,
    carregar_eventos,
)


@pytest.fixture
def test_db(tmp_path: Path) -> str:
    db_file = str(tmp_path / "test_placar.db")
    init_db_sync_direct(db_file)
    return db_file


def init_db_sync_direct(db_path: str):
    from app.db import init_db_sync

    init_db_sync(db_path)


@pytest.mark.asyncio
async def test_append_incrementa_seq(test_db: str):
    """Eventos consecutivos na mesma partida recebem sequência monotônica 1, 2, 3..."""
    quadra_id = "quadra-1"
    partida_id = "partida-1"

    e1 = await append_evento(
        test_db,
        quadra_id,
        partida_id,
        TipoEvento.PARTIDA_INICIADA,
        {"alvo": 12},
    )
    e2 = await append_evento(
        test_db,
        quadra_id,
        partida_id,
        TipoEvento.PONTO_MARCADO,
        {"equipe": "A"},
    )
    e3 = await append_evento(
        test_db,
        quadra_id,
        partida_id,
        TipoEvento.PONTO_MARCADO,
        {"equipe": "B"},
    )

    assert e1.seq == 1
    assert e2.seq == 2
    assert e3.seq == 3

    eventos = await carregar_eventos(test_db, partida_id)
    assert [e.seq for e in eventos] == [1, 2, 3]


@pytest.mark.asyncio
async def test_append_concorrente(test_db: str):
    """Appends simultâneos na mesma partida não colidem nem pulam sequência."""
    quadra_id = "quadra-concorrente"
    partida_id = "partida-concorrente"
    total_pontos = 20

    async def marcar(i: int):
        equipe = "A" if i % 2 == 0 else "B"
        return await append_evento(
            test_db,
            quadra_id,
            partida_id,
            TipoEvento.PONTO_MARCADO,
            {"equipe": equipe, "indice": i},
        )

    # Dispara 20 appends simultâneos
    resultados = await asyncio.gather(*[marcar(i) for i in range(total_pontos)])

    seqs = [r.seq for r in resultados]
    assert len(seqs) == total_pontos
    # Sem repetições
    assert len(set(seqs)) == total_pontos
    # Sequência de 1 até total_pontos sem buracos
    assert sorted(seqs) == list(range(1, total_pontos + 1))

    # Confere no banco
    no_banco = await carregar_eventos(test_db, partida_id)
    assert [e.seq for e in no_banco] == list(range(1, total_pontos + 1))


@pytest.mark.asyncio
async def test_seq_apos_restart(tmp_path: Path):
    """Reabrir a conexão e appendar continua do último seq gravado, não de zero."""
    db_file = str(tmp_path / "restart_test.db")
    await init_db(db_file)

    quadra_id = "quadra-restart"
    partida_id = "partida-restart"

    # Grava 3 eventos antes do 'restart'
    await append_evento(
        db_file,
        quadra_id,
        partida_id,
        TipoEvento.PARTIDA_INICIADA,
        {"alvo": 12},
    )
    await append_evento(
        db_file,
        quadra_id,
        partida_id,
        TipoEvento.PONTO_MARCADO,
        {"equipe": "A"},
    )
    e3 = await append_evento(
        db_file,
        quadra_id,
        partida_id,
        TipoEvento.PONTO_MARCADO,
        {"equipe": "B"},
    )
    assert e3.seq == 3

    # Simula 'restart': limpa locks em memória e abre nova conexão
    eventos_module._quadra_locks.clear()

    # Próximo evento deve ser seq 4
    e4 = await append_evento(
        db_file,
        quadra_id,
        partida_id,
        TipoEvento.PONTO_MARCADO,
        {"equipe": "A"},
    )
    assert e4.seq == 4

    eventos = await carregar_eventos(db_file, partida_id)
    assert [e.seq for e in eventos] == [1, 2, 3, 4]


def test_imutabilidade_sem_update_ou_delete():
    """Nenhum caminho de código em eventos.py faz UPDATE ou DELETE na tabela eventos."""
    source_code = inspect.getsource(eventos_module)
    upper_source = source_code.upper()

    # Garante que não existem queries com UPDATE ou DELETE na tabela eventos
    assert "UPDATE EVENTOS" not in upper_source
    assert "DELETE FROM EVENTOS" not in upper_source
    assert "DELETE EVENTOS" not in upper_source


def test_wal_e_foreign_keys(test_db: str):
    """Banco inicializado com WAL e Foreign Keys ativados."""
    with get_db(test_db) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode;")
        journal_mode = cursor.fetchone()[0].upper()
        assert journal_mode == "WAL"

        cursor.execute("PRAGMA foreign_keys;")
        foreign_keys = cursor.fetchone()[0]
        assert foreign_keys == 1
