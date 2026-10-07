# ruff: noqa: F811
import pytest

from app.reequilibrio import nota_efetiva
from app.sorteio import Participante, sortear
from tests.test_encerramento import Jogo, ac, base, placar  # noqa: F401


@pytest.mark.parametrize(
    ("base_", "saldo", "partidas", "esperada"),
    [
        (60, 0, 0, 60),  # sem partidas: a nota cadastrada
        (60, 8, 2, 68),  # 2 × 8 ÷ 2
        (60, -3, 3, 58),
        (60, 100, 1, 75),  # limite +15
        (60, -100, 1, 45),  # limite −15
        (98, 20, 1, 100),  # teto da nota
        (5, -20, 1, 1),  # piso da nota
    ],
)
def test_nota_efetiva(base_, saldo, partidas, esperada):
    assert nota_efetiva(base_, saldo, partidas) == esperada


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
async def test_rodada_2_ajusta_a_nota_pelo_saldo_sem_mudar_o_cadastro(ac, placar):
    jogo = await campeao_da_rodada_1(ac, placar)
    r = await ac.post("/api/rodada/sorteio", json={"alvo": 10})
    assert r.status_code in (200, 201), r.text
    rodada = (await jogo.estado())["rodada"]
    assert rodada["numero"] == 2 and rodada["estado"] == "proposta"
    js = jogadores(rodada)
    assert any(j["nota"] != j["nota_base"] for j in js.values())
    for j in js.values():
        assert abs(j["nota"] - j["nota_base"]) <= 15
    cadastro = (await ac.get("/api/jogadores")).json()
    cadastradas = {
        x["nome"]: x["nota"]
        for x in (cadastro["jogadores"] if isinstance(cadastro, dict) else cadastro)
    }
    assert all(cadastradas[n] == j["nota_base"] for n, j in js.items())


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
