# ruff: noqa: F811
import pytest

from app.nota_viva import delta_do_time, esperado, limitar
from tests.test_encerramento import Jogo, ac, base, placar  # noqa: F401


def test_times_iguais_vitoria_apertada_e_goleada():
    assert esperado(60, 60) == 0.5
    assert delta_do_time(60, 60, True, 2, 10) == 1  # 4 × 0,5 × 0,7 = 1,4
    assert delta_do_time(60, 60, False, 2, 10) == -1
    assert delta_do_time(60, 60, True, 6, 10) == 2  # 4 × 0,5 × 1,1 = 2,2
    assert delta_do_time(60, 60, True, 10, 10) == 3  # 4 × 0,5 × 1,5
    assert delta_do_time(60, 60, True, 20, 10) == 3  # a margem pesa até o alvo


def test_azarao_ganha_mais_e_favorito_ganha_menos():
    azarao = delta_do_time(50, 80, True, 4, 10)
    favorito = delta_do_time(80, 50, True, 4, 10)
    assert azarao > favorito >= 0
    # quem perdeu sendo favorito perde mais do que o azarão que perde
    assert delta_do_time(80, 50, False, 4, 10) < delta_do_time(50, 80, False, 4, 10)


def test_metade_arredonda_para_longe_do_zero():
    # 4 × 0,5 × (0,5 + 15/20) = 2,5: vitória +3 e derrota −3, simétricas
    assert delta_do_time(60, 60, True, 15, 20) == 3
    assert delta_do_time(60, 60, False, 15, 20) == -3


@pytest.mark.parametrize(("nota", "esperada"), [(0, 1), (-5, 1), (50, 50), (101, 100)])
def test_nota_fica_entre_1_e_100(nota, esperada):
    assert limitar(nota) == esperada


async def notas(ac):
    cadastro = (await ac.get("/api/jogadores")).json()
    lista = cadastro["jogadores"] if isinstance(cadastro, dict) else cadastro
    return {x["nome"]: x["nota"] for x in lista}


@pytest.mark.asyncio
async def test_partida_encerrada_sobe_a_nota_de_quem_ganhou_e_desce_a_de_quem_perdeu(
    ac, placar
):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    antes = await notas(ac)
    await jogo.chamar()
    c = (await jogo.estado())["conducao"]["partida"]
    await jogo.pontos("B", 3)
    await jogo.pontos("A", 10)
    assert (await jogo.encerrar()).status_code == 200
    depois = await notas(ac)
    mudaram = {n: depois[n] - antes[n] for n in antes if depois[n] != antes[n]}
    assert len(mudaram) == 4 and c  # os 4 jogadores da partida, mais ninguém
    assert sorted(mudaram.values()) == [-2, -2, 2, 2]


@pytest.mark.asyncio
async def test_desfazer_a_ultima_partida_devolve_as_notas(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    antes = await notas(ac)
    await jogo.jogar("A")
    assert await notas(ac) != antes
    r = await ac.post("/api/rodada/desfazer-partida")
    assert r.status_code == 200, r.text
    assert await notas(ac) == antes


@pytest.mark.asyncio
async def test_anular_a_partida_chamada_nao_mexe_nas_notas(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    antes = await notas(ac)
    await jogo.chamar()
    await jogo.pontos("A", 4)
    assert (await ac.post("/api/rodada/anular-partida")).status_code == 200
    assert await notas(ac) == antes


@pytest.mark.asyncio
async def test_painel_mostra_a_nota_atual_e_a_do_sorteio(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    await jogo.jogar("A")
    times = (await jogo.estado())["rodada"]["times"]
    js = [j for t in times for j in t["jogadores"]]
    assert any(j["nota_base"] != j["nota"] for j in js)  # atual × a do sorteio
    assert all(60 <= j["nota"] <= 62 or j["nota"] == 60 for j in js)
