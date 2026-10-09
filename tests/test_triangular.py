# ruff: noqa: F811
"""Rodada triangular de 3 times (CV8.DS8.US22, RN-18) de ponta a ponta."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from tests.test_atrasado import atrasado, cadastrar
from tests.test_encerramento import Jogo, ac, base, filas, placar  # noqa: F401


async def triangulo(ac, placar):
    return await Jogo(ac, placar).preparar(quantos=6, alvo=10)  # 3 duplas


@pytest.mark.asyncio
async def test_com_tres_times_a_rodada_e_triangular_e_comeca_na_etapa_1(ac, placar):
    await triangulo(ac, placar)
    c = (await ac.get("/api/sessao")).json()["conducao"]
    assert c["triangular"] == {"etapa": 1, "final": False}
    assert filas(c["em_quadra"]) == [1, 2] and filas(c["fila"]) == [3]


@pytest.mark.asyncio
async def test_terceiro_vence_os_dois_e_e_rei_e_a_rodada_se_encerra(ac, placar):
    jogo = await triangulo(ac, placar)
    c = (await jogo.jogar("A"))["conducao"]  # t1 vence t2: t2 enfrenta t3
    assert filas(c["em_quadra"]) == [2, 3] and filas(c["fila"]) == [1]
    assert c["triangular"] == {"etapa": 2, "final": False}
    c = (await jogo.jogar("B"))["conducao"]  # t3 vence t2: final contra t1
    assert filas(c["em_quadra"]) == [3, 1] and c["fila"] == []
    assert c["triangular"] == {"etapa": 3, "final": True}
    c = (await jogo.jogar("A"))["conducao"]  # t3 vence t1
    assert c["fase"] == "fim_da_fila" and c["finalista"]["fila"] == 3
    assert c["pode_iniciar_mata_mata"] is True and c["pode_chamar"] is False
    assert c["partidas_encerradas"] == 3 and c["triangular"] is None
    r = await ac.post("/api/rodada/iniciar-mata-mata")
    assert r.status_code == 200, r.text
    estado = (await ac.get("/api/sessao")).json()
    assert estado["rodada"] is None
    assert estado["ultimo_campeao"]["time"] == 3


@pytest.mark.asyncio
async def test_sem_rei_se_o_perdedor_da_primeira_vence_o_terceiro(ac, placar):
    jogo = await triangulo(ac, placar)
    await jogo.jogar("A")  # t1 vence t2
    c = (await jogo.jogar("A"))["conducao"]  # t2 vence t3
    assert c["fase"] == "sem_rei" and c["pode_encerrar_sem_campeao"] is True
    assert c["pode_chamar"] is False and "sem rei" in c["motivo"]
    assert (await ac.post("/api/rodada/chamar-partida")).status_code == 409
    r = await ac.post("/api/rodada/encerrar-sem-campeao")
    assert r.status_code == 200, r.text
    estado = (await ac.get("/api/sessao")).json()
    assert estado["rodada"] is None and estado["ultimo_campeao"] is None


@pytest.mark.asyncio
async def test_sem_rei_se_o_primeiro_vencedor_vence_a_final(ac, placar):
    jogo = await triangulo(ac, placar)
    await jogo.jogar("A")  # t1 vence t2
    await jogo.jogar("B")  # t3 vence t2
    c = (await jogo.jogar("B"))["conducao"]  # t1 vence t3 na final
    assert c["fase"] == "sem_rei" and c["pode_iniciar_mata_mata"] is False


@pytest.mark.asyncio
async def test_desfazer_volta_do_sem_rei_e_o_encerramento_e_manual(ac, placar):
    jogo = await triangulo(ac, placar)
    await jogo.jogar("A")
    await jogo.jogar("A")  # sem rei
    r = await ac.post("/api/rodada/desfazer-partida")
    assert r.status_code == 200, r.text
    c = r.json()["conducao"]
    assert c["fase"] == "fila" and filas(c["em_quadra"]) == [2, 3]
    assert c["triangular"] == {"etapa": 2, "final": False}


@pytest.mark.asyncio
async def test_encerrar_sem_campeao_so_depois_de_terminar_sem_rei(ac, placar):
    await triangulo(ac, placar)
    r = await ac.post("/api/rodada/encerrar-sem-campeao")
    assert r.status_code == 409
    assert r.json()["erros"][0]["tipo"] == "fora_do_sem_rei"


@pytest.mark.asyncio
async def test_encerrar_sem_campeao_exige_o_segredo():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        assert (await c.post("/api/rodada/encerrar-sem-campeao")).status_code == 404


@pytest.mark.asyncio
async def test_atrasado_nao_entra_na_rodada_triangular(ac, placar):
    await triangulo(ac, placar)
    novo = await cadastrar(ac, "Zeca Atrasado", "H")
    r = await atrasado(ac, novo)
    assert r.status_code == 409
    assert r.json()["erros"][0]["tipo"] == "rodada_triangular"


@pytest.mark.asyncio
async def test_pular_nao_e_oferecido_no_triangulo(ac, placar):
    await triangulo(ac, placar)
    r = await ac.post("/api/rodada/pular-time")
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_com_time_incompleto_a_rodada_nao_e_triangular(ac, placar):
    await Jogo(ac, placar).preparar(quantos=5, alvo=10)  # 2 duplas + 1 ímpar
    estado = (await ac.get("/api/sessao")).json()
    assert len(estado["rodada"]["times"]) == 3
    assert estado["conducao"]["triangular"] is None


@pytest.mark.asyncio
async def test_com_quatro_times_segue_o_rei_da_quadra(ac, placar):
    await Jogo(ac, placar).preparar(quantos=8, alvo=10)
    assert (await ac.get("/api/sessao")).json()["conducao"]["triangular"] is None


@pytest.mark.asyncio
async def test_retirar_no_triangulo_trava_a_vaga_e_a_saida_e_encerrar_sem_campeao(
    ac, placar
):
    await triangulo(ac, placar)
    estado = (await ac.get("/api/sessao")).json()
    t1 = next(t for t in estado["rodada"]["times"] if t["fila"] == 1)
    r = await ac.post(
        "/api/rodada/retirar", json={"jogador_id": t1["jogadores"][0]["id"]}
    )
    assert r.status_code == 200, r.text
    c = r.json()["conducao"]
    assert c["escalacao"]["ninguem"] is True and c["escalacao"]["pode_pular"] is False
    assert c["pode_encerrar_sem_campeao"] is True and c["pode_chamar"] is False
    r = await ac.post("/api/rodada/encerrar-sem-campeao")
    assert r.status_code == 200, r.text
    assert (await ac.get("/api/sessao")).json()["rodada"] is None


@pytest.mark.asyncio
async def test_time_sem_ninguem_no_triangulo_termina_sem_rei(ac, placar):
    await triangulo(ac, placar)
    estado = (await ac.get("/api/sessao")).json()
    t3 = next(t for t in estado["rodada"]["times"] if t["fila"] == 3)
    for j in t3["jogadores"]:
        r = await ac.post("/api/rodada/retirar", json={"jogador_id": j["id"]})
        assert r.status_code == 200, r.text
    c = r.json()["conducao"]
    assert c["fase"] == "sem_rei" and c["pode_encerrar_sem_campeao"] is True
    r = await ac.post("/api/rodada/desfazer-partida")  # nada a desfazer ainda
    assert r.status_code == 409
    assert (await ac.post("/api/rodada/encerrar-sem-campeao")).status_code == 200
