# ruff: noqa: F811
import pytest

from app.sorteio import Participante, sortear
from tests.test_encerramento import Jogo, ac, base, placar  # noqa: F401


def quatro():
    return [Participante(f"p{i}", "H" if i % 2 else "M", 60, i) for i in range(4)]


def test_evita_repetir_duplas_da_sessao_entre_equivalentes():
    primeira = sortear(quatro())
    anteriores = frozenset(frozenset(p.id for p in t.jogadores) for t in primeira.times)
    segunda = sortear(quatro(), anteriores=anteriores)
    assert primeira.repetidas == 0
    assert segunda.repetidas == 0
    novas = {frozenset(p.id for p in t.jogadores) for t in segunda.times}
    assert novas.isdisjoint(anteriores)


def test_genero_prevalece_sobre_repeticao():
    # 3 homens + 1 mulher: nenhuma dupla H+H é evitável além do mínimo (1).
    ps = [Participante(f"p{i}", "M" if i == 0 else "H", 60, i) for i in range(4)]
    s = sortear(ps)
    assert s.duplas_hh == 1


async def campeao_da_rodada_1(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=10)
    for vence in ("A", "A", "A"):
        await jogo.jogar(vence)
    await ac.post("/api/rodada/iniciar-mata-mata")
    await jogo.jogar("B")
    return jogo


def jogadores(rodada):
    return {j["nome"]: j for t in rodada["times"] for j in t["jogadores"]}


@pytest.mark.asyncio
async def test_rodada_2_sorteia_com_a_nota_atual_que_evoluiu(ac, placar):
    jogo = await campeao_da_rodada_1(ac, placar)
    cadastro = (await ac.get("/api/jogadores")).json()
    atuais = {
        x["nome"]: x["nota"]
        for x in (cadastro["jogadores"] if isinstance(cadastro, dict) else cadastro)
    }
    assert any(n != 60 and n != 61 and n != 62 for n in atuais.values())
    r = await ac.post("/api/rodada/sorteio", json={"alvo": 10})
    assert r.status_code in (200, 201), r.text
    rodada = (await jogo.estado())["rodada"]
    assert rodada["numero"] == 2 and rodada["estado"] == "proposta"
    js = jogadores(rodada)
    # o sorteio usa a nota atual do cadastro, sem ajuste de saldo por cima
    assert all(j["nota"] == j["nota_base"] == atuais[n] for n, j in js.items())


@pytest.mark.asyncio
async def test_rodada_2_nao_repete_duplas_e_resorteia(ac, placar):
    jogo = await campeao_da_rodada_1(ac, placar)
    await ac.post("/api/rodada/sorteio", json={"alvo": 10})
    primeira = (await jogo.estado())["rodada"]
    r = await ac.post("/api/rodada/resortear", json={})
    assert r.status_code in (200, 201), r.text
    segunda = (await jogo.estado())["rodada"]
    assert segunda["tentativa"] == primeira["tentativa"] + 1


@pytest.mark.asyncio
async def test_rodada_cancelada_nao_entra_no_saldo(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    await jogo.jogar("A")
    await ac.post("/api/rodada/cancelar")
    await ac.post("/api/rodada/sorteio", json={"alvo": 10})
    rodada = (await jogo.estado())["rodada"]
    assert all(j["nota"] == j["nota_base"] for j in jogadores(rodada).values())
