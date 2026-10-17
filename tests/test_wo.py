"""CV8.DS7.US21: dar a vitória (W.O.) a uma partida que não terminou no placar."""

# ruff: noqa: F811
import pytest

from app.config import settings
from app.gerenciador_db import conectar
from app.reequilibrio import ultima_partida
from tests.test_encerramento import SEGREDO, Jogo, ac, base, placar  # noqa: F401


async def notas(ac):
    cadastro = (await ac.get("/api/jogadores", headers=SEGREDO)).json()
    lista = cadastro["jogadores"] if isinstance(cadastro, dict) else cadastro
    return {j["id"]: j["nota"] for j in lista}


async def dar_vitoria(ac, vencedor):
    return await ac.post(
        "/api/rodada/dar-vitoria", json={"vencedor": vencedor}, headers=SEGREDO
    )


@pytest.mark.asyncio
async def test_wo_encerra_com_placar_parcial_e_vencedor_escolhido(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    antes = await notas(ac)
    await jogo.chamar()
    time_b = (await jogo.estado())["conducao"]["partida"]["time_b"]
    await jogo.pontos("A", 4)
    await jogo.pontos("B", 2)
    r = await dar_vitoria(ac, "B")  # quem perdia leva a vitória
    assert r.status_code == 200, r.text
    conducao = (await jogo.estado())["conducao"]
    h = conducao["historico"][-1]
    assert (h["placar_a"], h["placar_b"], h["wo"]) == (4, 2, True)
    assert h["vencedor"] == time_b
    assert await notas(ac) == antes  # a nota não muda no W.O.
    assert conducao["saldos"] == []  # W.O. fora do saldo
    assert not conducao["pode_dar_vitoria"]


@pytest.mark.asyncio
async def test_wo_segue_a_rodada_como_vitoria(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    await jogo.chamar()
    assert (await dar_vitoria(ac, "A")).status_code == 200
    conducao = (await jogo.estado())["conducao"]
    assert len(conducao["eliminados"]) == 2  # o time 2 perdeu e saiu
    venc = conducao["historico"][-1]["vencedor"]
    assert venc in [t["fila"] for t in conducao["em_quadra"]]
    # a rodada continua: a próxima partida joga normalmente
    await jogo.jogar("A")
    assert len((await jogo.estado())["conducao"]["historico"]) == 2


@pytest.mark.asyncio
async def test_wo_pode_ser_desfeito(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    antes = await notas(ac)
    await jogo.chamar()
    assert (await dar_vitoria(ac, "A")).status_code == 200
    r = await ac.post("/api/rodada/desfazer-partida", headers=SEGREDO)
    assert r.status_code == 200, r.text
    assert (await jogo.estado())["conducao"]["historico"] == []
    assert await notas(ac) == antes


@pytest.mark.asyncio
async def test_wo_recusa_vencedor_invalido_e_sem_partida(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    r = await dar_vitoria(ac, "A")
    assert r.status_code == 409 and "não tem partida chamada" in r.json()["detail"]
    await jogo.chamar()
    r = await dar_vitoria(ac, "C")
    assert r.status_code == 422
    sem_segredo = await ac.post(
        "/api/rodada/dar-vitoria",
        json={"vencedor": "A"},
        headers={"x-owner-secret": "errado"},
    )
    assert sem_segredo.status_code in (401, 403, 404)


@pytest.mark.asyncio
async def test_wo_fica_fora_da_resenha_e_conta_no_tempo_sem_jogar(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    await jogo.jogar("A")
    await jogo.chamar()
    assert (await dar_vitoria(ac, "B")).status_code == 200
    resenha = (await ac.get("/api/sessao/estatisticas", headers=SEGREDO)).json()
    assert resenha["resumo"]["partidas"] == 1  # só a partida jogada até o fim
    conn = conectar(settings.gerenciador_db_path)
    try:
        sessao_id = conn.execute(
            "SELECT id FROM sessoes WHERE encerrada_em IS NULL"
        ).fetchone()["id"]
        descanso = ultima_partida(conn, sessao_id)
    finally:
        conn.close()
    assert sorted(descanso.values()).count(2) == 4  # os 4 do W.O. jogaram a 2ª
