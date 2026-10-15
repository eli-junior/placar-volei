import random
import time
from itertools import product

import pytest

from app.sorteio import (
    TOLERANCIA,
    JogadoresInsuficientes,
    Participante,
    sortear,
)


def grupo(generos: str, notas=None, chegada=None):
    notas = notas or [60] * len(generos)
    chegada = chegada or list(range(1, len(generos) + 1))
    return [
        Participante(f"p{i}", g, n, o)
        for i, (g, n, o) in enumerate(zip(generos, notas, chegada, strict=True))
    ]


def completos(s):
    return [t for t in s.times if not t.incompleto]


def hh(s):
    return sum(all(p.genero == "H" for p in t.jogadores) for t in completos(s))


def minimo_hh(generos: str, impar_fora: str | None = None):
    h, m = generos.count("H"), generos.count("M")
    if impar_fora == "H":
        h -= 1
    elif impar_fora == "M":
        m -= 1
    return max(0, (h - m) // 2)


def test_menos_de_4_e_recusado():
    for n in range(4):
        with pytest.raises(JogadoresInsuficientes) as e:
            sortear(grupo("HM" * 2)[:n])
        assert e.value.faltam == 4 - n
    sortear(grupo("HMHM"))


def test_repetidos_sao_recusados():
    a = Participante("x", "H", 50, 1)
    with pytest.raises(ValueError):
        sortear([a, a, Participante("y", "M", 50, 2), Participante("z", "M", 50, 3)])


# Todas as composições até 12 jogadores e algumas maiores: o resto do espaço é
# o mesmo código com números maiores, e cada caso grande custa bem mais.
_COMPOSICOES = [(h, m) for h in range(13) for m in range(13) if 4 <= h + m <= 12] + [
    (12, 12),
    (20, 4),
    (4, 20),
    (11, 10),
]


@pytest.mark.parametrize(("homens", "mulheres"), _COMPOSICOES)
def test_genero_numero_minimo_de_duplas_hh(homens, mulheres):
    rng = random.Random(homens * 100 + mulheres)
    generos = list("H" * homens + "M" * mulheres)
    rng.shuffle(generos)
    notas = [rng.randint(1, 100) for _ in generos]
    ps = grupo("".join(generos), notas)
    for tentativa in range(2):
        s = sortear(ps, tentativa)
        impar = ps[-1].genero if len(ps) % 2 else None
        assert hh(s) == minimo_hh("".join(generos), impar)
        # toda dupla tem 2, todos aparecem exatamente uma vez
        ids = [p.id for t in s.times for p in t.jogadores]
        assert sorted(ids) == sorted(p.id for p in ps)


def test_mulheres_em_excesso_podem_formar_mm_sem_h_h():
    s = sortear(grupo("MMMMHH", [90, 80, 70, 60, 50, 40]))
    assert hh(s) == 0
    assert sum(all(p.genero == "M" for p in t.jogadores) for t in completos(s)) == 1


def test_homens_em_excesso_so_o_excedente_forma_hh():
    s = sortear(grupo("HHHHHHMM", [90, 85, 80, 75, 70, 65, 60, 55]))
    assert hh(s) == 2  # (6 − 2) / 2
    # as duas mulheres ficam com homens
    for t in completos(s):
        if any(p.genero == "M" for p in t.jogadores):
            assert {p.genero for p in t.jogadores} == {"H", "M"}


def test_serpentina_quando_nao_ha_restricao():
    # 8 jogadores só mulheres: pura serpentina por nota
    notas = [90, 85, 70, 65, 60, 55, 40, 30]
    s = sortear(grupo("M" * 8, notas))
    somas = sorted(t.soma for t in completos(s))
    assert somas == [120, 120, 120, 125] or max(somas) - min(somas) <= 5
    assert s.amplitude == max(somas) - min(somas)


def test_determinismo():
    ps = grupo("HMHMHMHM", [88, 71, 64, 90, 55, 33, 47, 60])
    a, b = sortear(ps), sortear(ps)
    assert a == b
    assert sortear(ps, 3) == sortear(ps, 3)


def test_independe_da_ordem_em_que_a_lista_chega():
    ps = grupo("HMHMHMHM", [88, 71, 64, 90, 55, 33, 47, 60])
    embaralhada = list(reversed(ps))
    assert sortear(ps) == sortear(embaralhada)


def test_impar_o_ultimo_a_chegar_fica_sozinho_por_ultimo():
    # p3 chegou por último (ordem 7), mesmo sendo o de maior nota
    ps = grupo("HMHMHMH", [60, 60, 60, 99, 60, 60, 60], [3, 1, 2, 7, 5, 4, 6])
    s = sortear(ps)
    assert len(s.times) == 4
    ultimo = s.times[-1]
    assert ultimo.incompleto and [p.id for p in ultimo.jogadores] == ["p3"]
    assert all(not t.incompleto for t in s.times[:-1])
    assert ultimo.fila == 4


def test_fila_pela_menor_chegada_e_primeira_partida():
    ps = grupo("HMHMHMHM", [60] * 8, [5, 1, 8, 2, 3, 7, 4, 6])
    s = sortear(ps)
    menores = [min(p.ordem for p in t.jogadores) for t in s.times]
    assert menores == sorted(menores)
    assert [t.fila for t in s.times] == list(range(1, 5))
    # quem chegou em 1º e em 2º estão nos dois primeiros times,
    # ou no primeiro com o 3º no segundo
    primeiros = {p.ordem for t in s.times[:2] for p in t.jogadores}
    assert 1 in primeiros and (2 in primeiros or 3 in primeiros)


def test_primeiro_e_segundo_na_mesma_dupla_entra_a_do_terceiro():
    # força 1º e 2º juntos: só eles têm notas que combinam entre si
    ps = [
        Participante("a", "H", 50, 1),
        Participante("b", "M", 50, 2),
        Participante("c", "H", 50, 3),
        Participante("d", "M", 50, 4),
    ]
    # com notas iguais há várias combinações; escolhe uma em que a e b estão juntos
    for t in range(10):
        s = sortear(ps, t)
        t1 = s.times[0]
        if {p.id for p in t1.jogadores} == {"a", "b"}:
            assert 3 in {p.ordem for p in s.times[1].jogadores}
            return
    pytest.skip("nenhuma combinação equivalente colocou 1º e 2º juntos")


def test_resortear_difere_respeita_tolerancia_e_genero():
    ps = grupo("HMHMHMHM", [60, 60, 61, 61, 59, 59, 62, 62])
    base = sortear(ps)
    assert base.distintas > 1
    vistos = {tuple(tuple(sorted(p.id for p in t.jogadores)) for t in base.times)}
    for t in range(1, base.distintas):
        s = sortear(ps, t)
        assert s.amplitude <= base.amplitude + TOLERANCIA
        assert hh(s) == hh(base)
        chave = tuple(tuple(sorted(p.id for p in t_.jogadores)) for t_ in s.times)
        assert chave not in vistos  # cada tentativa traz uma combinação nova
        vistos.add(chave)
    # ao esgotar, volta ao início
    assert sortear(ps, base.distintas).times == base.times


def test_combinacao_unica_e_sinalizada():
    ps = grupo("MMHH", [100, 1, 100, 1])
    s = sortear(ps)
    assert s.distintas >= 1
    assert sortear(ps, s.distintas).times == s.times


def test_notas_iguais_e_extremos():
    s = sortear(grupo("MMMMMMMM", [1] * 8))
    assert s.amplitude == 0
    s = sortear(grupo("MMMM", [1, 100, 1, 100]))
    assert sorted(t.soma for t in s.times) == [101, 101]


def _matchings(itens):
    if not itens:
        yield []
        return
    a = itens[0]
    for i in range(1, len(itens)):
        resto = itens[1:i] + itens[i + 1 :]
        for m in _matchings(resto):
            yield [(a, itens[i]), *m]


def test_equilibrio_e_o_melhor_possivel_nos_casos_pequenos():
    rng = random.Random(7)
    for _ in range(150):
        n = rng.choice([4, 6, 8])
        ps = grupo(
            "".join(rng.choice("HM") for _ in range(n)),
            [rng.randint(1, 100) for _ in range(n)],
        )
        s = sortear(ps)
        pares = [p for t in completos(s) for p in t.jogadores]
        k = hh(s)
        melhor = min(
            sum((a.nota + b.nota) ** 2 for a, b in m)
            for m in _matchings(pares)
            if sum(a.genero == b.genero == "H" for a, b in m) == k
        )
        obtido = sum(t.soma**2 for t in completos(s))
        assert obtido == melhor


def test_desempenho_com_muitos_jogadores():
    rng = random.Random(3)
    ps = grupo(
        "".join(rng.choice("HM") for _ in range(25)),
        [rng.randint(1, 100) for _ in range(25)],
    )
    inicio = time.perf_counter()
    s = sortear(ps)
    for t in range(1, 6):
        sortear(ps, t)
    assert time.perf_counter() - inicio < 5
    assert len(s.times) == 13 and s.times[-1].incompleto


def test_todas_as_combinacoes_de_genero_ate_6_jogadores():
    for n in range(4, 7):
        for generos in product("HM", repeat=n):
            ps = grupo("".join(generos), [50 + i for i in range(n)])
            s = sortear(ps)
            impar = ps[-1].genero if n % 2 else None
            assert hh(s) == minimo_hh("".join(generos), impar)


# --- US23: fila das rodadas seguintes por tempo sem jogar --------------------


def _media(time, descanso):
    return sum(descanso.get(p.id, 0) for p in time.jogadores) / len(time.jogadores)


def test_descanso_nao_muda_a_combinacao_so_a_fila():
    ps = grupo("HMHMHMHM", [60, 61, 62, 63, 64, 65, 66, 67])
    descanso = {"p0": 5, "p1": 5, "p2": 1, "p3": 2, "p6": 4}
    sem, com = sortear(ps), sortear(ps, descanso=descanso)

    def duplas(s):
        return {frozenset(p.id for p in t.jogadores) for t in s.times}

    assert duplas(sem) == duplas(com)
    assert com.amplitude == sem.amplitude
    medias = [_media(t, descanso) for t in com.times]
    assert medias == sorted(medias)
    assert [t.fila for t in com.times] == list(range(1, 5))


def test_quem_jogou_por_ultimo_vai_para_o_fim_da_fila():
    # a e b chegaram primeiro, mas jogaram a última partida (4)
    ps = [
        Participante("a", "H", 60, 1),
        Participante("b", "M", 60, 2),
        Participante("c", "H", 60, 3),
        Participante("d", "M", 60, 4),
    ]
    descanso = {"a": 4, "b": 4, "c": 1, "d": 2}
    for t in range(10):
        s = sortear(ps, t, descanso=descanso)
        medias = [_media(x, descanso) for x in s.times]
        assert medias == sorted(medias)
        if {p.id for p in s.times[-1].jogadores} == {"a", "b"}:
            return
    pytest.skip("nenhuma combinação equivalente juntou a e b")


def test_quem_ainda_nao_jogou_entra_primeiro_e_a_chegada_desempata():
    ps = grupo("HMHMHMHM", [60] * 8)
    # todos jogaram a partida 3, menos p6 e p7 (chegaram depois, nunca jogaram)
    descanso = {f"p{i}": 3 for i in range(6)}
    s = sortear(ps, descanso=descanso)
    zerados = [t for t in s.times if _media(t, descanso) < 3]
    assert s.times[0] in zerados
    iguais = [t for t in s.times if _media(t, descanso) == 3]
    chegadas = [min(p.ordem for p in t.jogadores) for t in iguais]
    assert chegadas == sorted(chegadas)


def test_sem_descanso_e_a_primeira_rodada_de_sempre():
    ps = grupo("HMHMHMHM", [60, 61, 62, 63, 64, 65, 66, 67], [5, 1, 8, 2, 3, 7, 4, 6])
    assert sortear(ps) == sortear(ps, descanso={})


def test_incompleto_segue_por_ultimo_mesmo_descansado():
    ps = grupo("HMHMH", [60] * 5)
    descanso = {"p0": 9, "p1": 9, "p2": 8, "p3": 8}  # p4 nunca jogou
    s = sortear(ps, descanso=descanso)
    # US24: o ímpar é quem jogou por último sem criar H+H (p0, homem), no fim
    assert s.times[-1].incompleto and [p.id for p in s.times[-1].jogadores] == ["p0"]


def test_trio_ordena_pela_media_do_descanso():
    ps = grupo("HMHMHMHMH", [60, 61, 62, 63, 64, 65, 66, 67, 68])
    descanso = {"p0": 6, "p1": 6, "p2": 6, "p3": 1, "p4": 2, "p5": 3, "p6": 4}
    s = sortear(ps, descanso=descanso, tamanho=3)
    medias = [_media(t, descanso) for t in s.times]
    assert medias == sorted(medias)


# --- US24: o ímpar é quem jogou por último; o incompleto, sempre no fim -------


def test_rodada_seguinte_impar_e_quem_jogou_por_ultimo():
    ps = grupo("HMHMHMHMH", [60] * 9)  # p8 é o último a chegar
    descanso = {f"p{i}": 1 for i in range(9)} | {"p2": 5}
    s = sortear(ps, descanso=descanso)
    assert s.times[-1].incompleto
    assert [p.id for p in s.times[-1].jogadores] == ["p2"]
    assert all(not t.incompleto for t in s.times[:-1])


def test_impar_empate_no_descanso_cai_no_ultimo_a_chegar():
    ps = grupo("HMHMHMHMH", [60] * 9)
    descanso = {f"p{i}": 3 for i in range(9)}
    assert [p.id for p in sortear(ps, descanso=descanso).times[-1].jogadores] == ["p8"]


def test_primeira_rodada_impar_segue_o_ultimo_a_chegar():
    # sem descanso, mesmo com mais homens e uma mulher por último (RN-05)
    ps = grupo("HHHHMM" + "M", [60] * 7)
    s = sortear(ps)
    assert [p.id for p in s.times[-1].jogadores] == ["p6"]


def test_impar_nao_cria_dupla_hh_evitavel():
    # 6 H e 5 M: a mulher p9 jogou por último, mas tirá-la geraria H+H a mais;
    # o ímpar é o homem que jogou por último
    ps = grupo("HHHHHHMMMMM", [60] * 11)
    descanso = {f"p{i}": 1 for i in range(11)} | {"p9": 6, "p4": 5}
    s = sortear(ps, descanso=descanso)
    assert [p.id for p in s.times[-1].jogadores] == ["p4"]
    assert s.duplas_hh == 0


def test_trio_sobra_de_dois_sao_os_que_jogaram_por_ultimo():
    ps = grupo("HMHMHMHM", [60] * 8)  # 2 trios + sobra de 2
    descanso = {f"p{i}": 1 for i in range(8)} | {"p0": 4, "p1": 4}
    s = sortear(ps, descanso=descanso, tamanho=3)
    ultimo = s.times[-1]
    assert ultimo.incompleto and {p.id for p in ultimo.jogadores} == {"p0", "p1"}
    assert s.duplas_hh == 0  # nenhum trio de um sexo só


def test_incompleto_fica_no_fim_mesmo_sendo_o_mais_descansado():
    # todos jogaram a última partida: o incompleto não sobe na fila
    ps = grupo("HMHMH", [60] * 5)
    descanso = {"p0": 9, "p1": 9, "p2": 9, "p3": 9, "p4": 9}
    s = sortear(ps, descanso=descanso)
    assert s.times[-1].incompleto and s.times[-1].fila == len(s.times)
