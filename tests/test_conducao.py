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


def rm(a, b, v):
    return ResultadoEntrada(f"t{a}", f"t{b}", f"t{v}", "mata_mata")


def test_mata_mata_desafiante_enfrenta_os_reis_na_ordem_de_coroacao():
    # 9 times: t1 e t5 viram reis; t7 fica sozinho e é o desafiante
    base = [r(1, 2, 1), r(1, 3, 1), r(4, 5, 5), r(5, 6, 5), r(7, 8, 7), r(7, 9, 7)]
    s = derivar(fila(9), base)
    assert s.reis == ("t1", "t5", "t7") and s.em_quadra == ()
    # quadra vazia: o último vencedor (t7, também rei) é o desafiante
    assert s.fase == "fim_da_fila" and s.desafiante == "t7"
    assert s.rivais == ("t1", "t5")
    s = derivar(fila(9), base, True)
    assert s.fase == "mata_mata" and s.em_quadra == ("t7", "t1")
    s = derivar(fila(9), [*base, rm(7, 1, 1)], True)  # ganhou ficou
    assert s.em_quadra == ("t1", "t5") and s.rivais == ("t5",)
    s = derivar(fila(9), [*base, rm(7, 1, 1), rm(1, 5, 5)], True)
    assert s.fase == "campeao" and s.campeao == "t5" and s.em_quadra == ()


def test_mata_mata_com_time_sozinho_na_quadra_e_sem_reis_ja_tem_campeao():
    s = derivar(fila(3), [r(1, 2, 1), r(1, 3, 3)])
    assert s.fase == "fim_da_fila" and s.desafiante == "t3" and s.rivais == ()
    s = derivar(fila(3), [r(1, 2, 1), r(1, 3, 3)], True)
    assert s.fase == "campeao" and s.campeao == "t3"


def test_mata_mata_so_depois_de_iniciado_e_na_ordem():
    base = [r(1, 2, 1), r(1, 3, 1), r(4, 5, 4)]  # t1 rei; t4 sozinho
    with pytest.raises(ValueError):
        derivar(fila(5), [*base, rm(4, 1, 4)])  # sem iniciar
    with pytest.raises(ValueError):
        derivar(fila(5), [r(1, 2, 1)], True)  # a fila ainda não terminou
    with pytest.raises(ValueError):
        derivar(fila(5), [*base, rm(4, 2, 4)], True)  # t2 não é rival


# --- CV8.DS7.TS3: ajustes da fila (remover e pular time) -----------------------

from app.conducao import Ajuste


def remover(t, apos=0):
    return Ajuste(apos, "remover", t)


def pular(t, apos=0):
    return Ajuste(apos, "pular", t)


def test_sem_ajustes_a_saida_e_a_mesma():
    res = [r(1, 2, 1), r(1, 3, 1)]
    assert derivar(fila(5), res) == derivar(fila(5), res, False, ())
    assert derivar(fila(5), res, False, [pular("t9", 0)]) == derivar(fila(5), res)


def test_remover_time_da_fila_antes_de_jogar():
    s = derivar(fila(4), [], False, [remover("t3")])
    assert s.em_quadra == ("t1", "t2") and s.fila == ("t4",)


def test_remover_time_da_quadra_traz_o_proximo():
    s = derivar(fila(4), [], False, [remover("t2")])
    assert s.em_quadra == ("t1", "t3") and s.fila == ("t4",)


def test_remover_vencedor_que_ficou_na_quadra_nao_quebra_os_resultados():
    # t1 vence t2 e fica; depois seus jogadores saem (apos=1); t3 e t4 entram
    res = [r(1, 2, 1), r(3, 4, 3)]
    s = derivar(fila(5), res, False, [remover("t1", apos=1)])
    assert s.em_quadra == ("t3", "t5") or s.em_quadra == ("t3", "t4")
    # a segunda partida foi entre t3 e t4, o que só é possível se t1 saiu da quadra
    assert "t1" not in (*s.em_quadra, *s.fila, *s.reis, *s.eliminados)


def test_remover_rei_tira_da_lista_de_reis_e_do_mata_mata():
    res = [r(1, 2, 1), r(1, 3, 1)]  # t1 é rei
    s = derivar(fila(4), res, False, [remover("t1", apos=2)])
    assert s.reis == () and "t1" not in (*s.em_quadra, *s.fila)


def test_remover_desafiante_promove_o_ultimo_rei():
    # 3 times: t1 vence t2 e t3 (rei, fila vazia -> fim da fila, desafiante t1)
    res = [r(1, 2, 1), r(1, 3, 1)]
    s = derivar(fila(3), res)
    assert s.fase == "fim_da_fila" and s.desafiante == "t1"
    s = derivar(fila(3), res, False, [remover("t1", apos=2)])
    assert s.desafiante is None and s.reis == ()


def test_pular_time_da_fila_manda_para_o_fim():
    s = derivar(fila(5), [], False, [pular("t3")])
    assert s.em_quadra == ("t1", "t2") and s.fila == ("t4", "t5", "t3")


def test_pular_time_em_quadra_traz_o_proximo_e_ele_vai_para_o_fim():
    # t1 vence t2; t3 entra, mas está sem elegível e é pulado (apos=1)
    res = [r(1, 2, 1)]
    s = derivar(fila(5), res, False, [pular("t3", apos=1)])
    assert s.em_quadra == ("t1", "t4") and s.fila == ("t5", "t3")


def test_pular_com_a_fila_vazia_nao_muda_nada():
    assert derivar(fila(2), [], False, [pular("t2")]) == derivar(fila(2), [])


def test_ajuste_depois_da_ultima_partida_vale_no_fim():
    # apos=9 com uma única partida: aplicado depois dela (um desfazer a tirou)
    res = [r(1, 2, 1)]
    assert derivar(fila(5), res, False, [pular("t3", apos=9)]) == derivar(
        fila(5), res, False, [pular("t3", apos=1)]
    )


def test_mata_mata_rival_removido_e_rival_pulado():
    # 5 times: t1 e t3 viram reis; t5 sobra sozinho e abre o mata-mata
    res = [r(1, 2, 1), r(1, 3, 1), r(4, 5, 4), r(4, 6, 4)]
    base = derivar(fila(6), res)
    assert base.reis == ("t1", "t4")
    s = derivar(fila(6), res, True, [pular("t1", apos=4)])
    assert s.fase == "mata_mata" and s.rivais[-1] == "t1"
    s = derivar(fila(6), res, True, [remover("t4", apos=4)])
    assert "t4" not in (*s.em_quadra, *s.reis, *s.rivais)


def test_mata_mata_remover_o_campeao_de_entao_promove_o_proximo_rival():
    res = [r(1, 2, 1), r(1, 3, 1), r(4, 5, 4), r(4, 6, 4)]
    # t6 desafia (sobra sozinho? não: t4 virou rei), depois o desafiante perde ou sai
    s = derivar(fila(6), res, True)
    assert s.fase == "mata_mata"
    desafiante = s.desafiante
    s2 = derivar(fila(6), res, True, [remover(desafiante, apos=4)])
    assert desafiante not in (*s2.em_quadra, *s2.rivais) and s2.campeao != desafiante


def test_invariantes_em_simulacoes_aleatorias():
    import random

    for semente in range(300):
        rng = random.Random(semente)
        n = rng.randint(2, 8)
        times = fila(n)
        resultados, ajustes, removidos = [], [], set()
        iniciado = False
        for _ in range(rng.randint(0, 40)):
            s = derivar(times, resultados, iniciado, ajustes)
            ativos = {*s.em_quadra, *s.fila, *s.reis}
            sorte = rng.random()
            if sorte < 0.25 and ativos:
                alvo = rng.choice(sorted(ativos))
                tipo = rng.choice(["remover", "pular"])
                ajustes.append(Ajuste(len(resultados), tipo, alvo))
                if tipo == "remover":
                    removidos.add(alvo)
            elif s.fase in ("fila", "mata_mata") and len(s.em_quadra) == 2:
                a, b = s.em_quadra
                resultados.append(
                    ResultadoEntrada(
                        a,
                        b,
                        rng.choice([a, b]),
                        "fila" if s.fase == "fila" else "mata_mata",
                    )
                )
            elif s.fase == "fim_da_fila" and not iniciado and s.desafiante:
                iniciado = True
            else:
                break
            s = derivar(times, resultados, iniciado, ajustes)  # nunca levanta
            lugares = [*s.em_quadra, *s.fila, *s.reis]
            assert not (set(lugares) | set(s.rivais) | set(s.eliminados)) & removidos
            if s.fase in ("fila", "fim_da_fila") and not iniciado:
                todos = [*s.em_quadra, *s.fila, *s.reis, *s.eliminados]
                assert len(todos) == len(set(todos))
                assert set(todos) | removidos == {t.id for t in times}
            assert s.campeao not in removidos
