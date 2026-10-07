# ruff: noqa: F811
import sqlite3

import pytest

from app.config import settings
from app.gerenciador_db import conectar, init_gerenciador_sync
from tests.test_encerramento import Jogo, ac, base, placar  # noqa: F401


def sem_volatil(estado: dict) -> dict:
    """O estado sem o que muda a cada leitura (carimbo de revisão)."""
    return {k: v for k, v in estado.items() if k != "revisao"}


def linhas(sql, *args):
    conn = sqlite3.connect(settings.gerenciador_db_path)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in conn.execute(sql, args)]
    finally:
        conn.close()


def test_conexao_grava_com_synchronous_full(tmp_path):
    conn = conectar(str(tmp_path / "x.db"))
    try:
        assert conn.execute("PRAGMA synchronous").fetchone()[0] == 2  # FULL
    finally:
        conn.close()


@pytest.mark.asyncio
async def test_reinicio_apos_cada_partida_devolve_o_mesmo_estado(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=10)  # 5 times, com mata-mata
    for vence in ("A", "A", "A"):
        await jogo.jogar(vence)
        antes = sem_volatil(await jogo.estado())
        init_gerenciador_sync()  # o restart reabre o mesmo arquivo
        assert sem_volatil(await jogo.estado()) == antes
        assert antes["conducao"]["historico"][-1]["placar_a"] is not None
    await ac.post("/api/rodada/iniciar-mata-mata")
    antes = sem_volatil(await jogo.estado())
    init_gerenciador_sync()
    assert sem_volatil(await jogo.estado()) == antes
    await jogo.jogar("B")  # o rei vence o desafiante: campeão
    antes = sem_volatil(await jogo.estado())
    init_gerenciador_sync()
    depois = sem_volatil(await jogo.estado())
    assert depois == antes and depois["ultimo_campeao"]["time"] == 1


@pytest.mark.asyncio
async def test_registro_completo_da_rodada_para_ranking(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=10)
    for vence in ("A", "A", "A"):
        await jogo.jogar(vence)
    await ac.post("/api/rodada/iniciar-mata-mata")
    await jogo.jogar("B")

    rodada = linhas("SELECT * FROM rodadas")[0]
    assert rodada["estado"] == "encerrada" and rodada["campeao_time_id"]
    assert rodada["mata_mata_em"] and rodada["confirmado_em"]
    partidas = linhas("SELECT * FROM partidas_rodada ORDER BY ordem")
    assert [p["fase"] for p in partidas] == ["fila"] * 3 + ["mata_mata"]
    for p in partidas:  # tudo que o ranking precisa, em cada partida
        assert p["estado"] == "encerrada" and p["vencedor_time_id"]
        assert p["placar_a"] is not None and p["placar_b"] is not None
        assert p["vencedor_time_id"] in (p["time_a_id"], p["time_b_id"])
        assert p["encerrada_em"] and p["chamada_em"]
    assert len(linhas("SELECT * FROM times")) == 5
    membros = linhas("SELECT * FROM time_jogadores")
    assert len(membros) == 10 and all(m["nota"] and m["ordem_chegada"] for m in membros)


@pytest.mark.asyncio
async def test_cancelar_rodada_e_encerrar_sessao_mantem_as_partidas(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=10)
    await jogo.jogar("A")
    assert len(linhas("SELECT * FROM partidas_rodada")) == 1
    assert (await ac.post("/api/rodada/cancelar")).status_code == 200
    assert linhas("SELECT estado FROM rodadas") == [{"estado": "cancelada"}]
    assert len(linhas("SELECT * FROM partidas_rodada WHERE estado = 'encerrada'")) == 1
    assert (await ac.post("/api/sessao/encerrar")).status_code == 200
    assert len(linhas("SELECT * FROM partidas_rodada WHERE estado = 'encerrada'")) == 1
    assert len(linhas("SELECT * FROM times")) == 5
    assert linhas("SELECT encerrada_em FROM sessoes")[0]["encerrada_em"]
