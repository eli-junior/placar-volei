# ruff: noqa: F811
import sqlite3

import pytest

from app.config import settings
from app.gerenciador_db import init_gerenciador_sync
from tests.test_encerramento import Jogo, ac, base, placar  # noqa: F401


def resumo(estado):
    c = estado["conducao"]
    return {
        "em_quadra": [t["fila"] for t in c["em_quadra"]],
        "fila": [t["fila"] for t in c["fila"]],
        "reis": [t["fila"] for t in c["reis"]],
        "eliminados": sorted(j["id"] for j in c["eliminados"]),
        "vitorias": {t["fila"]: t["vitorias"] for t in c["em_quadra"]},
        "encerradas": c["partidas_encerradas"],
    }


async def desfazer(ac):
    return await ac.post("/api/rodada/desfazer-partida")


@pytest.mark.asyncio
async def test_desfazer_restaura_o_estado_anterior(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=10)
    await jogo.jogar("A")
    antes = resumo(await jogo.estado())
    await jogo.jogar("A")  # Time 1 vira rei
    assert resumo(await jogo.estado())["reis"] == [1]
    r = await desfazer(ac)
    assert r.status_code == 200, r.text
    depois = r.json()
    assert resumo(depois) == antes
    assert depois["pode_desfazer"] is False  # um nível só


@pytest.mark.asyncio
async def test_so_um_nivel_e_volta_a_valer_apos_nova_partida(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    await jogo.jogar("A")
    await jogo.jogar("A")
    assert (await desfazer(ac)).status_code == 200
    r = await desfazer(ac)
    assert r.status_code == 409 and "desfeita" in r.json()["detail"]
    await jogo.jogar("B")
    assert (await jogo.estado())["pode_desfazer"] is True
    assert (await desfazer(ac)).status_code == 200


@pytest.mark.asyncio
async def test_sem_partida_encerrada_e_recusado(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    assert (await jogo.estado())["pode_desfazer"] is False
    assert (await desfazer(ac)).status_code == 409


@pytest.mark.asyncio
async def test_descarta_a_partida_chamada_depois_da_ultima(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    await jogo.jogar("A")
    await jogo.chamar()
    r = await desfazer(ac)
    assert r.status_code == 200
    c = r.json()["conducao"]
    assert c["partida"] is None and c["partidas_encerradas"] == 0


@pytest.mark.asyncio
async def test_desfaz_o_campeao_e_reabre_a_rodada(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=10)
    for v in ("A", "A", "A"):
        await jogo.jogar(v)
    await ac.post("/api/rodada/iniciar-mata-mata")
    await jogo.jogar("B")
    estado = await jogo.estado()
    assert estado["ultimo_campeao"] and estado["rodada"] is None
    assert estado["pode_desfazer"] is True
    r = await desfazer(ac)
    assert r.status_code == 200, r.text
    novo = r.json()
    assert novo["ultimo_campeao"] is None
    assert novo["rodada"]["estado"] == "em_andamento"
    assert novo["conducao"]["fase"] == "mata_mata"
    # e dá para terminar de novo
    await jogo.jogar("A")
    assert (await jogo.estado())["ultimo_campeao"]


@pytest.mark.asyncio
async def test_desfazer_ultima_da_fila_cancela_o_inicio_do_mata_mata(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    await jogo.jogar("A")
    await jogo.jogar("A")  # Time 1 rei; Time 4 sozinho: fim da fila
    await ac.post("/api/rodada/iniciar-mata-mata")
    r = await desfazer(ac)  # a última encerrada é da fila
    assert r.status_code == 200, r.text
    assert r.json()["rodada"]["mata_mata_iniciado"] is False
    assert r.json()["conducao"]["fase"] == "fila"


@pytest.mark.asyncio
async def test_migra_do_schema_7(ac, tmp_path):
    conn = sqlite3.connect(settings.gerenciador_db_path)
    conn.executescript(
        "ALTER TABLE rodadas DROP COLUMN desfeito; PRAGMA user_version = 7;"
    )
    conn.close()
    init_gerenciador_sync()
    conn = sqlite3.connect(settings.gerenciador_db_path)
    assert conn.execute("PRAGMA user_version").fetchone()[0] == 8
    assert "desfeito" in [r[1] for r in conn.execute("PRAGMA table_info(rodadas)")]
    conn.close()
