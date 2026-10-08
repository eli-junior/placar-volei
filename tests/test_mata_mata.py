# ruff: noqa: F811
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from tests.test_encerramento import Jogo, ac, base, filas, placar  # noqa: F401


async def iniciar(ac):
    return await ac.post("/api/rodada/iniciar-mata-mata")


@pytest.mark.asyncio
async def test_sem_segredo_retorna_404():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        assert (await c.post("/api/rodada/iniciar-mata-mata")).status_code == 404


@pytest.mark.asyncio
async def test_so_inicia_no_fim_da_fila(ac, placar):
    await Jogo(ac, placar).preparar(quantos=10)  # 5 times
    r = await iniciar(ac)
    assert r.status_code == 409
    assert r.json()["erros"][0]["tipo"] == "fora_do_fim_da_fila"


@pytest.mark.asyncio
async def test_fluxo_completo_ate_o_campeao(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=10)  # times 1..5
    await jogo.jogar("A")  # t1 vence t2
    await jogo.jogar("A")  # t1 vence t3 → rei
    c = await jogo.jogar("A")  # t4 vence t5 → sozinho
    assert c["conducao"]["fase"] == "fim_da_fila"
    c = c["conducao"]
    assert c["pode_iniciar_mata_mata"] is True and c["pode_chamar"] is False
    assert c["finalista"]["fila"] == 4
    assert (await ac.post("/api/rodada/chamar-partida")).status_code == 409

    est = (await iniciar(ac)).json()
    c = est["conducao"]
    assert c["fase"] == "mata_mata" and filas(c["em_quadra"]) == [4, 1]
    assert est["rodada"]["mata_mata_iniciado"] is True
    assert c["mata_mata"]["desafiante"]["fila"] == 4
    assert [t["fila"] for t in c["mata_mata"]["rivais"]] == [1]
    assert c["pode_chamar"] is True and c["pode_iniciar_mata_mata"] is False
    assert (await iniciar(ac)).status_code == 409  # não reinicia

    est = await jogo.jogar("B")  # o rei (t1) vence o desafiante
    assert est["rodada"] is None and est["conducao"] is None
    assert est["ultimo_campeao"]["time"] == 1 and est["ultimo_campeao"]["rodada"] == 1
    assert len(est["ultimo_campeao"]["jogadores"]) == 2
    # libera o próximo sorteio (presença destravada)
    r = await ac.post("/api/rodada/sorteio", json={"alvo": 10})
    assert r.status_code in (200, 201), r.text
    assert r.json()["rodada"]["estado"] == "proposta"


@pytest.mark.asyncio
async def test_sem_reis_o_vencedor_da_ultima_partida_e_campeao_direto(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=4)  # 2 times
    c = (await jogo.jogar("A"))["conducao"]  # t1 vence → sozinho
    assert c["fase"] == "fim_da_fila" and c["mata_mata"]["rivais"] == []
    est = (await iniciar(ac)).json()
    assert est["rodada"] is None and est["ultimo_campeao"]["time"] == 1


@pytest.mark.asyncio
async def test_ultimo_vencedor_que_virou_rei_com_a_fila_vazia_e_o_desafiante(
    ac, placar
):
    jogo = await Jogo(ac, placar).preparar(quantos=6)  # 3 times
    await jogo.jogar("A")  # t1 vence t2
    c = (await jogo.jogar("A"))["conducao"]  # t1 vence t3 → rei, quadra vazia
    assert c["em_quadra"] == [] and c["fase"] == "fim_da_fila"
    assert c["finalista"]["fila"] == 1 and c["mata_mata"]["rivais"] == []
    est = (await iniciar(ac)).json()
    assert est["ultimo_campeao"]["time"] == 1


@pytest.mark.asyncio
async def test_mata_mata_com_dois_reis_ganhou_ficou(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=14)  # 7 times
    for _ in range(2):
        await jogo.jogar("A")  # t1 rei (vence t2 e t3)
    await jogo.jogar("A")  # t4 vence t5
    c = (await jogo.jogar("A"))["conducao"]  # t4 vence t6 → rei 2; t7 sozinho
    assert c["fase"] == "fim_da_fila"
    assert [t["fila"] for t in c["mata_mata"]["rivais"]] == [1, 4]
    c = (await iniciar(ac)).json()["conducao"]
    assert filas(c["em_quadra"]) == [7, 1]
    c = (await jogo.jogar("A"))["conducao"]  # t7 vence t1 e fica
    assert c["fase"] == "mata_mata" and filas(c["em_quadra"]) == [7, 4]
    assert [h["fase"] for h in c["historico"]][-1] == "mata_mata"
    est = await jogo.jogar("B")  # t4 vence t7 → campeão
    assert est["ultimo_campeao"]["time"] == 4
    assert est["rodada"] is None


def test_migra_do_schema_6(tmp_path):
    import sqlite3

    from app.gerenciador_db import init_gerenciador_sync

    antigo = str(tmp_path / "v6.db")
    conn = sqlite3.connect(antigo)
    conn.executescript(
        """
        CREATE TABLE rodadas (id TEXT PRIMARY KEY, sessao_id TEXT NOT NULL, numero INTEGER NOT NULL,
            alvo INTEGER NOT NULL, estado TEXT NOT NULL, tentativa INTEGER NOT NULL DEFAULT 0,
            distintas INTEGER NOT NULL DEFAULT 1, criado_em TEXT NOT NULL, confirmado_em TEXT);
        CREATE TABLE partidas_rodada (id TEXT PRIMARY KEY, rodada_id TEXT NOT NULL, ordem INTEGER NOT NULL,
            time_a_id TEXT NOT NULL, time_b_id TEXT NOT NULL, estado TEXT NOT NULL, quadra_id TEXT NOT NULL,
            partida_quadra_id TEXT, chamada_em TEXT NOT NULL, placar_a INTEGER, placar_b INTEGER,
            vencedor_time_id TEXT, encerrada_em TEXT);
        INSERT INTO partidas_rodada VALUES ('p1', 'r1', 1, 'a', 'b', 'encerrada', 'q', NULL, 'x', 10, 3, 'a', 'y');
        PRAGMA user_version = 6;
        """
    )
    conn.commit()
    conn.close()
    init_gerenciador_sync(antigo)
    init_gerenciador_sync(antigo)  # idempotente
    conn = sqlite3.connect(antigo)
    assert conn.execute("SELECT fase FROM partidas_rodada").fetchone() == ("fila",)
    colunas = [r[1] for r in conn.execute("PRAGMA table_info(rodadas)")]
    assert "mata_mata_em" in colunas and "campeao_time_id" in colunas
    assert conn.execute("PRAGMA user_version").fetchone() == (9,)
