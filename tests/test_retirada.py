# ruff: noqa: F811
"""Retirar jogador no meio da rodada (CV8.DS7.US19) e pular time (decisão C)."""

import sqlite3

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.main import app
from tests.test_encerramento import Jogo, ac, base, placar  # noqa: F401


async def retirar(ac, jogador_id):
    return await ac.post("/api/rodada/retirar", json={"jogador_id": jogador_id})


def times(estado, onde):
    return {t["fila"]: t for t in estado["conducao"][onde]}


def ids_do_time(time):
    return [j["id"] for j in time["jogadores"]]


def todos_os_times(estado):
    return {t["fila"]: t for t in estado["rodada"]["times"]}


@pytest.mark.asyncio
async def test_sem_segredo_retorna_404():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        assert (
            await c.post("/api/rodada/retirar", json={"jogador_id": "x"})
        ).status_code == 404
        assert (await c.post("/api/rodada/pular-time")).status_code == 404


@pytest.mark.asyncio
async def test_retirar_da_fila_deixa_a_vaga_e_o_jogador_ausente(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    estado = await jogo.estado()
    time3 = times(estado, "fila")[3]
    saiu, fica = ids_do_time(time3)
    r = await retirar(ac, saiu)
    assert r.status_code == 200, r.text
    novo = r.json()
    t3 = times(novo, "fila")[3]
    assert ids_do_time(t3) == [fica] and t3["incompleto"] is True
    assert saiu not in {p["id"] for p in novo["presentes"]}
    assert saiu in {a["id"] for a in novo["ausentes"]}
    assert [p["ordem"] for p in novo["presentes"]] == list(range(1, 8))
    # os dois primeiros times seguem chamáveis: a vaga só pesa na vez do Time 3
    assert novo["conducao"]["pode_chamar"] is True


@pytest.mark.asyncio
async def test_time_sem_ninguem_sai_da_fila(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    estado = await jogo.estado()
    for jid in ids_do_time(times(estado, "fila")[3]):
        r = await retirar(ac, jid)
        assert r.status_code == 200, r.text
    novo = r.json()
    assert list(times(novo, "fila")) == [4]
    assert novo["conducao"]["pode_chamar"] is True


@pytest.mark.asyncio
async def test_em_jogo_nao_sai_mas_quem_esta_na_fila_sai(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    await jogo.chamar()
    estado = await jogo.estado()
    em_quadra = ids_do_time(times(estado, "em_quadra")[1])[0]
    r = await retirar(ac, em_quadra)
    assert r.status_code == 409 and r.json()["erros"][0]["tipo"] == "em_jogo"
    assert "em jogo" in r.json()["detail"]
    da_fila = ids_do_time(times(estado, "fila")[3])[0]
    assert (await retirar(ac, da_fila)).status_code == 200
    # a partida chamada segue encerrável e a derivação continua coerente
    await jogo.pontos("A", 10)
    r = await jogo.encerrar()
    assert r.status_code == 200, r.text


@pytest.mark.asyncio
async def test_vencedor_que_fica_com_todos_fora_libera_a_quadra_sem_quebrar_o_historico(
    ac, placar
):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    estado = await jogo.jogar("A")  # Time 1 vence o Time 2 e fica com 1 vitória
    em_quadra = times(estado, "em_quadra")
    assert 1 in em_quadra and em_quadra[1]["vitorias"] == 1
    for jid in ids_do_time(em_quadra[1]):
        r = await retirar(ac, jid)
        assert r.status_code == 200, r.text
    novo = r.json()
    assert sorted(times(novo, "em_quadra")) == [3, 4]
    # a próxima partida acontece entre os times que entraram e a rodada segue
    estado = await jogo.jogar("B")
    assert 1 not in {*times(estado, "em_quadra"), *times(estado, "fila")}


@pytest.mark.asyncio
async def test_time_com_vaga_em_quadra_pede_parceiro_da_lista_de_escalacao(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    estado = await jogo.jogar("A")  # Time 2 eliminado; Time 1 fica com 1 vitória
    time1 = times(estado, "em_quadra")[1]
    saiu = ids_do_time(time1)[0]
    r = await retirar(ac, saiu)
    assert r.status_code == 200, r.text
    c = r.json()["conducao"]
    assert c["pode_chamar"] is False and "Time 1" in c["motivo"]
    esc = c["escalacao"]
    assert esc["time"] == 1 and esc["faltam"] == 1 and esc["ninguem"] is False
    candidatos = [j for g in esc["grupos"] for j in g["jogadores"]]
    assert candidatos  # os eliminados do Time 2
    r = await ac.post(
        "/api/rodada/escalar-parceiro", json={"jogador_id": candidatos[0]["id"]}
    )
    assert r.status_code == 200, r.text
    novo = r.json()
    t1 = times(novo, "em_quadra")[1]
    assert len(t1["jogadores"]) == 2 and t1["vitorias"] == 1 and not t1["incompleto"]
    assert novo["conducao"]["pode_chamar"] is True


@pytest.mark.asyncio
async def test_sem_elegivel_o_time_e_pulado_para_o_fim_da_fila(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    estado = await jogo.estado()
    saiu = ids_do_time(times(estado, "em_quadra")[1])[0]
    r = await retirar(ac, saiu)
    c = r.json()["conducao"]
    assert c["escalacao"]["ninguem"] is True and c["escalacao"]["pode_pular"] is True
    r = await ac.post("/api/rodada/pular-time")
    assert r.status_code == 200, r.text
    novo = r.json()
    assert sorted(times(novo, "em_quadra")) == [2, 3]
    assert [t["fila"] for t in novo["conducao"]["fila"]] == [4, 1]
    assert novo["conducao"]["pode_chamar"] is True


@pytest.mark.asyncio
async def test_pular_e_recusado_quando_ha_elegivel_ou_nada_a_pular(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    r = await ac.post("/api/rodada/pular-time")
    assert r.status_code == 409 and r.json()["erros"][0]["tipo"] == "sem_incompleto"
    estado = await jogo.jogar("A")
    saiu = ids_do_time(times(estado, "em_quadra")[1])[0]
    await retirar(ac, saiu)
    r = await ac.post("/api/rodada/pular-time")
    assert r.status_code == 409 and r.json()["erros"][0]["tipo"] == "ha_elegiveis"


@pytest.mark.asyncio
async def test_rei_com_vaga_escolhe_o_parceiro_ao_entrar_no_mata_mata(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    await jogo.jogar("A")  # 1 vence 2
    estado = await jogo.jogar("A")  # 1 vence 3 e vira rei; o Time 4 sobra sozinho
    assert [t["fila"] for t in estado["conducao"]["reis"]] == [1]
    saiu = ids_do_time(times(estado, "reis")[1])[0]
    r = await retirar(ac, saiu)
    assert r.status_code == 200, r.text
    assert ids_do_time(times(r.json(), "reis")[1])[0] != saiu
    r = await ac.post("/api/rodada/iniciar-mata-mata")
    assert r.status_code == 200, r.text
    c = r.json()["conducao"]
    assert sorted(t["fila"] for t in c["em_quadra"]) == [1, 4]
    assert c["pode_chamar"] is False and "Time 1" in c["motivo"]
    esc = c["escalacao"]
    candidato = esc["grupos"][0]["jogadores"][0]["id"]
    r = await ac.post("/api/rodada/escalar-parceiro", json={"jogador_id": candidato})
    assert r.status_code == 200, r.text
    assert r.json()["conducao"]["pode_chamar"] is True


@pytest.mark.asyncio
async def test_rei_sem_ninguem_sai_do_mata_mata(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    await jogo.jogar("A")
    estado = await jogo.jogar("A")
    for jid in ids_do_time(times(estado, "reis")[1]):
        r = await retirar(ac, jid)
        assert r.status_code == 200, r.text
    novo = r.json()
    assert novo["conducao"]["reis"] == []
    # o Time 4 é o único que sobrou: a rodada já tem desafiante sem rival
    r = await ac.post("/api/rodada/iniciar-mata-mata")
    assert r.status_code == 200, r.text


@pytest.mark.asyncio
async def test_desfazer_depois_de_retirar_continua_coerente(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    estado = await jogo.jogar("A")
    for jid in ids_do_time(times(estado, "fila")[4]):
        assert (await retirar(ac, jid)).status_code == 200
    with sqlite3.connect(settings.gerenciador_db_path) as conn:
        assert conn.execute(
            "SELECT apos_partidas, tipo FROM ajustes_fila"
        ).fetchall() == [(1, "remover")]
    r = await ac.post("/api/rodada/desfazer-partida")
    assert r.status_code == 200, r.text
    with sqlite3.connect(settings.gerenciador_db_path) as conn:
        assert conn.execute("SELECT apos_partidas FROM ajustes_fila").fetchall() == [
            (0,)
        ]
    assert [t["fila"] for t in times(r.json(), "em_quadra").values()] == [1, 2]
    estado = await jogo.jogar("B")  # a derivação segue válida
    assert 4 not in {*times(estado, "em_quadra"), *times(estado, "fila")}


@pytest.mark.asyncio
async def test_retirar_eliminado_tira_do_banco_de_candidatos(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    estado = await jogo.jogar("A")
    eliminado = estado["conducao"]["eliminados"][0]["id"]
    r = await retirar(ac, eliminado)
    assert r.status_code == 200, r.text
    assert eliminado not in {j["id"] for j in r.json()["conducao"]["eliminados"]}
    assert eliminado in {a["id"] for a in r.json()["ausentes"]}


@pytest.mark.asyncio
async def test_retirado_volta_como_atrasado(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    estado = await jogo.estado()
    saiu = ids_do_time(times(estado, "fila")[3])[0]
    await retirar(ac, saiu)
    r = await ac.post("/api/rodada/atrasado", json={"jogador_id": saiu})
    assert r.status_code == 200, r.text
    assert saiu in {p["id"] for p in r.json()["presentes"]}


@pytest.mark.asyncio
async def test_recusas(ac, placar):
    r = await retirar(ac, "x")
    assert r.status_code == 409  # sem sessão
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    assert (await retirar(ac, "ninguem")).status_code == 409
    assert (await ac.post("/api/rodada/retirar", json={})).status_code == 422
    assert (await retirar(ac, 123)).status_code == 422
    estado = await jogo.estado()
    saiu = ids_do_time(times(estado, "fila")[3])[0]
    assert (await retirar(ac, saiu)).status_code == 200
    assert (await retirar(ac, saiu)).status_code == 409  # já saiu
