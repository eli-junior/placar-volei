# ruff: noqa: F811
import pytest

from app.config import settings
from app.gerenciador_db import conectar
from app.reequilibrio import ultima_partida
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


@pytest.mark.asyncio
async def test_rodada_2_poe_na_frente_quem_esta_ha_mais_tempo_sem_jogar(ac, placar):
    # Rodada 1 (10 jogadores, 5 duplas): T1×T2, T1×T3 (T1 rei), T4×T5,
    # mata-mata T4×T1. Última partida: T2 → 1, T3 → 2, T5 → 3, T4 e T1 → 4.
    jogo = await campeao_da_rodada_1(ac, placar)
    conn = conectar(settings.gerenciador_db_path)
    try:
        sessao_id = conn.execute(
            "SELECT id FROM sessoes WHERE encerrada_em IS NULL"
        ).fetchone()["id"]
        descanso = ultima_partida(conn, sessao_id)
    finally:
        conn.close()
    assert sorted(descanso.values()) == [1, 1, 2, 2, 3, 3, 4, 4, 4, 4]

    r = await ac.post("/api/rodada/sorteio", json={"alvo": 10})
    assert r.status_code in (200, 201), r.text
    rodada = (await jogo.estado())["rodada"]
    medias = [
        sum(descanso[j["id"]] for j in t["jogadores"]) / len(t["jogadores"])
        for t in sorted(rodada["times"], key=lambda t: t["fila"])
    ]
    assert medias == sorted(medias)
    assert medias[0] < medias[-1]


def _descanso_da_sessao():
    conn = conectar(settings.gerenciador_db_path)
    try:
        sessao_id = conn.execute(
            "SELECT id FROM sessoes WHERE encerrada_em IS NULL"
        ).fetchone()["id"]
        return ultima_partida(conn, sessao_id)
    finally:
        conn.close()


@pytest.mark.asyncio
async def test_partida_de_rodada_cancelada_conta_como_jogada(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    await jogo.jogar("A")
    r = await ac.post("/api/rodada/cancelar")
    assert r.status_code == 200, r.text
    assert sorted(_descanso_da_sessao().values()) == [1, 1, 1, 1]


@pytest.mark.asyncio
async def test_sem_ajustes_de_nota_usa_os_times_da_partida(ac, placar):
    # `make resetar-notas` entre rodadas apaga `ajustes_nota`
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    await jogo.jogar("A")
    antes = _descanso_da_sessao()
    conn = conectar(settings.gerenciador_db_path)
    try:
        with conn:
            conn.execute("DELETE FROM ajustes_nota")
    finally:
        conn.close()
    assert _descanso_da_sessao() == antes and len(antes) == 4


@pytest.mark.asyncio
async def test_rodada_2_impar_e_quem_jogou_por_ultimo_e_fica_no_fim(ac, placar):
    # 11 jogadores (6 H, 5 M): rodada 1 com o ímpar (último a chegar) no fim
    jogo = await Jogo(ac, placar).preparar(quantos=11)
    rodada1 = (await jogo.estado())["rodada"]
    impar1 = [t for t in rodada1["times"] if t["incompleto"]]
    assert len(impar1) == 1
    await jogo.jogar("A")
    assert (await ac.post("/api/rodada/cancelar")).status_code == 200
    descanso = _descanso_da_sessao()
    r = await ac.post("/api/rodada/sorteio", json={"alvo": 10})
    assert r.status_code in (200, 201), r.text
    times = sorted((await jogo.estado())["rodada"]["times"], key=lambda t: t["fila"])
    assert times[-1]["incompleto"] and not any(t["incompleto"] for t in times[:-1])
    impar = times[-1]["jogadores"][0]
    assert descanso.get(impar["id"]) == 1  # jogou a única partida
    assert impar["id"] != impar1[0]["jogadores"][0]["id"]
