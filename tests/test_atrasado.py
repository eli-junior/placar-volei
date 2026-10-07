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


@pytest.mark.asyncio
async def test_dois_atrasados_ficam_em_times_separados_e_nao_se_escolhem(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    a = await cadastrar(ac, "Ana Atrasada", "M")
    b = await cadastrar(ac, "Beto Atrasado", "H")
    await atrasado(ac, a)
    estado = (await atrasado(ac, b)).json()
    novos = [t for t in estado["rodada"]["times"] if t["origem"] == "atrasado"]
    assert [len(t["jogadores"]) for t in novos] == [1, 1]
    # Joga até os dois atrasados chegarem à quadra: nenhum é candidato do outro.
    while True:
        c = (await jogo.estado())["conducao"]
        if c["escalacao"] and c["escalacao"]["origem"] == "atrasado":
            ids = {j["id"] for g in c["escalacao"]["grupos"] for j in g["jogadores"]}
            assert not ids & {a, b}
            break
        assert c["fase"] == "fila", c["fase"]
        await jogo.jogar("A")
        assert len((await jogo.estado())["rodada"]["times"]) >= 6


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
