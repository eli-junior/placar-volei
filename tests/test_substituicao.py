# ruff: noqa: F811
import pytest

from tests.test_encerramento import Jogo, ac, base, placar  # noqa: F401


async def substituir(ac, saiu, entra):
    return await ac.post(
        "/api/rodada/substituir", json={"saiu_id": saiu, "entra_id": entra}
    )


def time_de(estado, jogador_id):
    todos = [
        *estado["conducao"]["em_quadra"],
        *estado["conducao"]["fila"],
        *estado["conducao"]["reis"],
    ]
    return next(t for t in todos if any(j["id"] == jogador_id for j in t["jogadores"]))


@pytest.mark.asyncio
async def test_impar_aguardando_substitui_e_o_time_mantem_vitorias(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=9)
    await jogo.jogar("A")  # Time 1 vence e fica em quadra com 1 vitória
    estado = await jogo.estado()
    time1 = estado["conducao"]["em_quadra"][0]
    assert time1["vitorias"] == 1
    saiu = time1["jogadores"][0]["id"]
    impar = estado["conducao"]["fila"][-1]["jogadores"][0]["id"]
    assert estado["conducao"]["substituicao"]["entram"]
    r = await substituir(ac, saiu, impar)
    assert r.status_code == 200, r.text
    novo = r.json()
    t = time_de(novo, impar)
    assert t["fila"] == time1["fila"] and t["vitorias"] == 1
    assert not any(
        j["id"] == saiu for p in novo["rodada"]["times"] for j in p["jogadores"]
    )
    assert saiu not in {p["id"] for p in novo["presentes"]}  # ausente
    assert saiu in {a["id"] for a in novo["ausentes"]}
    assert len(novo["rodada"]["times"]) == len(estado["rodada"]["times"]) - 1


@pytest.mark.asyncio
async def test_eliminado_substitui_como_escalado(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    await jogo.jogar("A")
    estado = await jogo.estado()
    eliminado = estado["conducao"]["eliminados"][0]
    saiu = estado["conducao"]["fila"][0]["jogadores"][0]
    candidatos = estado["conducao"]["substituicao"]["entram"]
    alvo = next(c for c in candidatos if c["id"] == eliminado["id"])
    r = await substituir(ac, saiu["id"], alvo["id"])
    if r.status_code == 409:  # H+H com alternativa: escolhe quem o servidor aceita
        assert "formaria dupla H+H" in r.json()["detail"]
        alvo = next(c for c in candidatos if c["genero"] == "M")
        r = await substituir(ac, saiu["id"], alvo["id"])
    assert r.status_code == 200, r.text
    novo = r.json()
    t = time_de(novo, alvo["id"])
    assert next(j for j in t["jogadores"] if j["id"] == alvo["id"])["escalado"] is True
    assert alvo["id"] not in {j["id"] for j in novo["conducao"]["eliminados"]}


@pytest.mark.asyncio
async def test_recusas(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=9)
    estado = await jogo.estado()
    saiu = estado["conducao"]["em_quadra"][0]["jogadores"][0]["id"]
    impar = estado["conducao"]["fila"][-1]["jogadores"][0]["id"]
    r = await substituir(ac, saiu, saiu)
    assert r.status_code == 422
    r = await ac.post("/api/rodada/substituir", json={})
    assert r.status_code == 422
    r = await substituir(ac, saiu, "ninguem")
    assert r.status_code == 409 and "não está entre" in r.json()["detail"]
    r = await substituir(ac, "ninguem", impar)
    assert r.status_code == 409
    await jogo.chamar()
    assert (await substituir(ac, saiu, impar)).status_code == 409
    assert (await jogo.estado())["conducao"]["substituicao"] is None


@pytest.mark.asyncio
async def test_opcoes_sem_jogador_repetido_no_mata_mata(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    await jogo.jogar("A")
    await jogo.jogar("A")  # Time 1 é rei; o Time 4 sobra e abre o mata-mata
    await ac.post("/api/rodada/iniciar-mata-mata")
    sub = (await jogo.estado())["conducao"]["substituicao"]
    ids = [j["id"] for j in sub["saem"]]
    assert len(ids) == len(set(ids))
