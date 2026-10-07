import pytest

from app.conducao import (
    ResultadoEntrada,
    TimeEntrada,
    derivar,
    nome_da_equipe,
    nomes_curtos,
)


def fila(n, incompleto_ultimo=False):
    return [
        TimeEntrada(f"t{i}", i, incompleto_ultimo and i == n) for i in range(1, n + 1)
    ]


def r(a, b, v):
    return ResultadoEntrada(f"t{a}", f"t{b}", f"t{v}")


def test_situacao_inicial():
    s = derivar(fila(5), [])
    assert s.fase == "fila"
    assert s.em_quadra == ("t1", "t2")
    assert s.fila == ("t3", "t4", "t5")
    assert s.reis == () and s.eliminados == ()
    assert all(v == 0 for v in s.vitorias.values())


def test_ordem_da_fila_vem_da_posicao_nao_da_ordem_da_lista():
    embaralhada = [
        TimeEntrada("t3", 3, False),
        TimeEntrada("t1", 1, False),
        TimeEntrada("t2", 2, False),
    ]
    s = derivar(embaralhada, [])
    assert s.em_quadra == ("t1", "t2") and s.fila == ("t3",)


def test_vencedor_fica_e_enfrenta_o_proximo_perdedor_sai():
    s = derivar(fila(5), [r(1, 2, 1)])
    assert s.em_quadra == ("t1", "t3")
    assert s.fila == ("t4", "t5")
    assert s.eliminados == ("t2",)
    assert s.vitorias["t1"] == 1 and s.reis == ()
    # o vencedor pode ser o time B da partida
    s = derivar(fila(5), [r(1, 2, 2)])
    assert s.em_quadra == ("t2", "t3") and s.eliminados == ("t1",)


def test_duas_vitorias_seguidas_viram_rei_e_entram_os_dois_proximos():
    s = derivar(fila(7), [r(1, 2, 1), r(1, 3, 1)])
    assert s.reis == ("t1",)
    assert s.em_quadra == ("t4", "t5")
    assert s.fila == ("t6", "t7")
    assert s.eliminados == ("t2", "t3")
    assert s.fase == "fila"


def test_reis_na_ordem_em_que_viraram():
    # t1 vira rei; depois t5 vence duas seguidas e vira o segundo
    s = derivar(
        fila(9),
        [r(1, 2, 1), r(1, 3, 1), r(4, 5, 5), r(5, 6, 5)],
    )
    assert s.reis == ("t1", "t5")
    assert s.eliminados == ("t2", "t3", "t4", "t6")
    assert s.em_quadra == ("t7", "t8") and s.fila == ("t9",)


def test_nao_ha_vitoria_seguida_depois_de_perder_a_quadra():
    # o vencedor que fica soma 1; quem entra começa do zero
    s = derivar(fila(5), [r(1, 2, 2), r(2, 3, 3)])
    assert s.vitorias["t2"] == 1 and s.vitorias["t3"] == 1
    assert s.em_quadra == ("t3", "t4")


def test_fila_esvazia_com_um_time_sozinho_encerra_a_fase():
    # 3 times: t1 vence t2, enfrenta t3, vence → rei (2 vitórias); quadra vazia
    s = derivar(fila(3), [r(1, 2, 1), r(1, 3, 1)])
    assert s.reis == ("t1",) and s.em_quadra == () and s.fila == ()
    assert s.fase == "fim_da_fila" and s.ultimo_vencedor == "t1"
    # 3 times: t1 vence t2 e perde para t3 → t3 sozinho na quadra
    s = derivar(fila(3), [r(1, 2, 1), r(1, 3, 3)])
    assert s.em_quadra == ("t3",) and s.fase == "fim_da_fila"
    assert s.ultimo_vencedor == "t3" and s.eliminados == ("t2", "t1")


def test_resultado_invalido_e_recusado():
    with pytest.raises(ValueError):
        derivar(fila(4), [r(3, 4, 3)])  # t3 e t4 ainda não estavam em quadra
    with pytest.raises(ValueError):
        derivar(fila(4), [ResultadoEntrada("t1", "t2", "t9")])
    with pytest.raises(ValueError):
        derivar(fila(4), [r(1, 2, 1), r(1, 2, 1)])  # t2 já foi eliminado


def test_todo_time_esta_em_exatamente_um_lugar():
    import random

    rng = random.Random(4)
    for _ in range(200):
        n = rng.randint(2, 12)
        times = fila(n)
        resultados = []
        for _ in range(rng.randint(0, 2 * n)):
            s = derivar(times, resultados)
            if s.fase != "fila":
                break
            a, b = s.em_quadra
            resultados.append(ResultadoEntrada(a, b, rng.choice([a, b])))
        s = derivar(times, resultados)
        lugares = [*s.em_quadra, *s.fila, *s.reis, *s.eliminados]
        assert sorted(lugares) == sorted(t.id for t in times)
        assert len(set(lugares)) == len(lugares)


def test_nomes_curtos_e_homonimos():
    js = [
        {"id": "1", "nome": "Ana Souza"},
        {"id": "2", "nome": "Gil Sete"},
        {"id": "3", "nome": "ana lima"},
        {"id": "4", "nome": "Davi Quatro"},
    ]
    c = nomes_curtos(js)
    assert c == {"1": "Ana S.", "2": "Gil", "3": "ana L.", "4": "Davi"}
    assert nome_da_equipe([c["1"], c["2"]]) == "Ana S. + Gil"
    assert nome_da_equipe([c["4"]]) == "Davi"
