# ruff: noqa: F811
import pytest

from tests.test_encerramento import Jogo, ac, base, placar  # noqa: F401


async def cadastrar(ac, nome, genero="M", nota=60):
    r = await ac.post(
        "/api/jogadores", json={"nome": nome, "genero": genero, "nota": nota}
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


async def atrasado(ac, jogador_id):
    return await ac.post("/api/rodada/atrasado", json={"jogador_id": jogador_id})


@pytest.mark.asyncio
async def test_atrasado_vira_time_incompleto_no_fim_da_fila(ac, placar):
    await Jogo(ac, placar).preparar(quantos=8)
    novo = await cadastrar(ac, "Zeca Atrasado", "H")
    r = await atrasado(ac, novo)
    assert r.status_code == 200, r.text
    estado = r.json()
    times = estado["rodada"]["times"]
    ultimo = times[-1]
    assert (
        ultimo["fila"] == 5 and ultimo["incompleto"] and ultimo["origem"] == "atrasado"
    )
    assert [j["id"] for j in ultimo["jogadores"]] == [novo]
    assert any(p["id"] == novo and p["ordem"] == 9 for p in estado["presentes"])
    assert estado["conducao"]["fila"][-1]["fila"] == 5


def _atrasados(estado):
    return [t for t in estado["rodada"]["times"] if t["origem"] == "atrasado"]


async def _jogar_ate_agrupar(jogo, quantos_times):
    """Joga até os atrasados virarem `quantos_times` times; nenhum atrasado
    sozinho chega à quadra antes disso."""
    for _ in range(10):
        estado = await jogo.estado()
        if len(_atrasados(estado)) == quantos_times:
            return estado
        esc = estado["conducao"]["escalacao"]
        assert not (esc and esc["origem"] == "atrasado"), esc
        assert estado["conducao"]["fase"] == "fila"
        await jogo.jogar("A")
    raise AssertionError("os atrasados não se agruparam")


@pytest.mark.asyncio
async def test_atrasados_esperam_separados_e_formam_dupla_no_fim_da_fila(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    a = await cadastrar(ac, "Ana Atrasada", "M")
    b = await cadastrar(ac, "Beto Atrasado", "H")
    await atrasado(ac, a)
    estado = (await atrasado(ac, b)).json()
    # Ainda há times sorteados à frente: cada um espera no seu time.
    assert [len(t["jogadores"]) for t in _atrasados(estado)] == [1, 1]
    estado = await _jogar_ate_agrupar(jogo, 1)
    (time,) = _atrasados(estado)
    assert {j["id"] for j in time["jogadores"]} == {a, b}
    assert not time["incompleto"]
    # O time vazio deixou de existir e a fila mostra a dupla formada.
    assert sum(1 for t in estado["conducao"]["fila"] if t["fila"] == time["fila"]) <= 1


@pytest.mark.asyncio
async def test_tres_atrasados_o_ultimo_a_chegar_escolhe_um_eliminado(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    ids = [await cadastrar(ac, f"Atr{n} Teste", "M", 60) for n in "ABC"]
    for i in ids:
        await atrasado(ac, i)
    estado = await _jogar_ate_agrupar(jogo, 2)
    dupla, sobra = _atrasados(estado)
    assert {j["id"] for j in dupla["jogadores"]} == set(ids[:2])
    assert [j["id"] for j in sobra["jogadores"]] == [ids[2]] and sobra["incompleto"]
    # Na vez dele, a escalação oferece os eliminados.
    for _ in range(10):
        c = (await jogo.estado())["conducao"]
        if c["escalacao"]:
            assert c["escalacao"]["origem"] == "atrasado"
            nomes = [j["id"] for g in c["escalacao"]["grupos"] for j in g["jogadores"]]
            assert nomes and ids[2] not in nomes
            return
        await jogo.jogar("A")
    raise AssertionError("o atrasado que sobrou não chegou à quadra")


@pytest.mark.asyncio
async def test_atrasado_que_chega_depois_faz_dupla_com_a_sobra(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    ids = [await cadastrar(ac, f"Atr{n} Teste", "M", 60) for n in "ABC"]
    for i in ids:
        await atrasado(ac, i)
    await _jogar_ate_agrupar(jogo, 2)
    d = await cadastrar(ac, "AtrD Teste", "H", 60)
    await atrasado(ac, d)
    times = _atrasados(await _jogar_ate_agrupar(jogo, 2))
    assert not any(t["incompleto"] for t in times)
    assert {j["id"] for j in times[1]["jogadores"]} == {ids[2], d}


@pytest.mark.asyncio
async def test_atrasados_se_agrupam_equilibrados(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    notas = {"Forte": 95, "Bom": 85, "Fraco": 35, "Novato": 25}
    ids = {n: await cadastrar(ac, f"{n} Teste", "M", nota) for n, nota in notas.items()}
    for i in ids.values():
        await atrasado(ac, i)
    estado = await _jogar_ate_agrupar(jogo, 2)
    somas = sorted(sum(j["nota"] for j in t["jogadores"]) for t in _atrasados(estado))
    assert somas == [120, 120]  # Forte + Novato e Bom + Fraco, não pela chegada


@pytest.mark.asyncio
async def test_recusas(ac, placar):
    novo = await cadastrar(ac, "Zeca Atrasado", "H")
    await ac.post("/api/sessao")
    assert (await atrasado(ac, novo)).status_code == 409  # sem rodada
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    presente = (await jogo.estado())["presentes"][0]["id"]
    r = await atrasado(ac, presente)
    assert r.status_code == 409 and "já está presente" in r.json()["detail"]
    assert (await atrasado(ac, "nao-existe")).status_code in (404, 409)
    assert (await ac.post("/api/rodada/atrasado", json={})).status_code == 422


@pytest.mark.asyncio
async def test_bloqueado_apos_o_mata_mata_e_entra_na_proxima_rodada(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=10)
    novo = await cadastrar(ac, "Zeca Atrasado", "H")
    for vence in ("A", "A", "A"):
        await jogo.jogar(vence)
    await ac.post("/api/rodada/iniciar-mata-mata")
    r = await atrasado(ac, novo)
    assert r.status_code == 409 and "próxima rodada" in r.json()["detail"]
    await jogo.jogar("B")  # campeão
    await ac.put(f"/api/sessao/presencas/{novo}")
    r = await ac.post("/api/rodada/sorteio", json={"alvo": 10})
    assert r.status_code in (200, 201)
    nomes = {
        j["id"]
        for t in (await jogo.estado())["rodada"]["times"]
        for j in t["jogadores"]
    }
    assert novo in nomes


def _p(i, genero="M", nota=60):
    from app.sorteio import Participante

    return Participante(f"j{i}", genero, nota, i)


def test_grupos_sobra_e_o_ultimo_a_chegar_e_trio_junta_os_que_sobram():
    from app.atrasados import _grupos

    ids = lambda grupos: [[p.id for p in g] for g in grupos]
    # Duplas: 3 viram uma dupla e a sobra; 5 vão ao sorteio, que deixa o último.
    assert ids(_grupos([_p(1), _p(2), _p(3)], 2, frozenset())) == [["j1", "j2"], ["j3"]]
    cinco = _grupos([_p(i) for i in range(1, 6)], 2, frozenset())
    assert [len(g) for g in cinco] == [2, 2, 1] and cinco[-1][0].id == "j5"
    # Trio: dois sozinhos esperando viram um time de dois (ainda incompleto).
    assert ids(_grupos([_p(1), _p(2)], 3, frozenset())) == [["j1", "j2"]]
    assert ids(_grupos([_p(i) for i in range(1, 5)], 3, frozenset())) == [
        ["j1", "j2", "j3"],
        ["j4"],
    ]
