import asyncio
import sqlite3
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.db import init_db
from app.gerenciador_db import init_gerenciador_sync
from app.main import app
from app.rate_limit import owner_rate_limiter

SEGREDO = {"x-owner-secret": "segredo-teste"}


@pytest.fixture(autouse=True)
async def base(tmp_path: Path):
    settings.db_path = str(tmp_path / "quadras.db")
    settings.gerenciador_db_path = str(tmp_path / "gerenciador.db")
    settings.owner_secret = "segredo-teste"
    owner_rate_limiter.resetar()
    await init_db(settings.db_path)
    init_gerenciador_sync()
    yield
    owner_rate_limiter.resetar()


@pytest.fixture
async def ac():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", headers=SEGREDO
    ) as c:
        yield c


async def presentes(ac, especificacao, abrir=True):
    """Cria e marca presentes, na ordem dada: [(nome, genero, nota), ...]."""
    if abrir:
        await ac.post("/api/sessao")
    ids = []
    for nome, genero, nota in especificacao:
        j = (
            await ac.post(
                "/api/jogadores", json={"nome": nome, "genero": genero, "nota": nota}
            )
        ).json()
        await ac.put(f"/api/sessao/presencas/{j['id']}")
        ids.append(j["id"])
    return ids


OITO = [
    ("Ana Um", "M", 90),
    ("Bia Dois", "M", 85),
    ("Caio Tres", "H", 70),
    ("Davi Quatro", "H", 65),
    ("Eva Cinco", "M", 60),
    ("Fabio Seis", "H", 55),
    ("Gil Sete", "H", 40),
    ("Helo Oito", "M", 30),
]


def times(estado):
    return estado["rodada"]["times"]


def nomes_time(t):
    return sorted(j["nome"] for j in t["jogadores"])


async def sortear(ac, alvo=10):
    return await ac.post("/api/rodada/sorteio", json={"alvo": alvo})


@pytest.mark.asyncio
async def test_sem_segredo_retorna_404():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        for caminho in ("sorteio", "resortear", "confirmar", "descartar", "cancelar"):
            r = await c.post(f"/api/rodada/{caminho}", json={"alvo": 10})
            assert r.status_code == 404


@pytest.mark.asyncio
async def test_sem_sessao_e_menos_de_quatro_sao_recusados(ac):
    assert (await sortear(ac)).status_code == 409
    await presentes(ac, OITO[:3])
    r = await sortear(ac)
    assert r.status_code == 409 and r.json()["erros"][0]["campo"] == "rodada"
    assert "faltam 1" in r.json()["detail"]
    assert (await ac.get("/api/sessao")).json()["rodada"] is None


@pytest.mark.asyncio
@pytest.mark.parametrize("alvo", [None, 5, 26, "10", True, 0, [10], 10.5])
async def test_alvo_invalido(ac, alvo):
    await presentes(ac, OITO)
    r = await sortear(ac, alvo)
    assert r.status_code == 422 and r.json()["erros"][0]["campo"] == "alvo"


@pytest.mark.asyncio
@pytest.mark.parametrize("alvo", [6, 8, 15, 25])
async def test_alvo_de_6_a_25(ac, alvo):
    await presentes(ac, OITO)
    r = await sortear(ac, alvo)
    assert r.status_code == 201 and r.json()["rodada"]["alvo"] == alvo


@pytest.mark.asyncio
async def test_proposta_com_oito(ac):
    await presentes(ac, OITO)
    r = await sortear(ac, 12)
    assert r.status_code == 201
    rodada = r.json()["rodada"]
    assert (
        rodada["numero"],
        rodada["alvo"],
        rodada["estado"],
        rodada["tentativa"],
    ) == (1, 12, "proposta", 0)
    assert [t["fila"] for t in rodada["times"]] == [1, 2, 3, 4]
    assert all(
        len(t["jogadores"]) == 2 and not t["incompleto"] for t in rodada["times"]
    )
    assert sorted(j["nome"] for t in rodada["times"] for j in t["jogadores"]) == sorted(
        n for n, _, _ in OITO
    )
    # genero: 4 H e 4 M → nenhuma dupla H+H
    for t in rodada["times"]:
        assert {j["genero"] for j in t["jogadores"]} == {"H", "M"}
    # fila pela menor chegada
    menores = [min(j["ordem_chegada"] for j in t["jogadores"]) for t in rodada["times"]]
    assert menores == sorted(menores)
    # somas equilibradas dentro da restrição de gênero (cada homem com uma mulher):
    # o melhor casamento possível (conferido por força bruta) dá 100, 125, 130, 140
    assert sorted(t["soma"] for t in rodada["times"]) == [100, 125, 130, 140]
    # exemplo do guia de validação: a fila segue a chegada (Ana, Bia, Caio, Davi)
    assert [nomes_time(t) for t in rodada["times"]] == [
        ["Ana Um", "Gil Sete"],
        ["Bia Dois", "Fabio Seis"],
        ["Caio Tres", "Helo Oito"],
        ["Davi Quatro", "Eva Cinco"],
    ]
    # idempotente em dois sorteios iguais (outra sessão não há; descarta e refaz)
    await ac.post("/api/rodada/descartar")
    de_novo = (await sortear(ac, 12)).json()["rodada"]
    assert [nomes_time(t) for t in de_novo["times"]] == [
        nomes_time(t) for t in rodada["times"]
    ]


@pytest.mark.asyncio
async def test_impar_ultimo_a_chegar_fica_sozinho_por_ultimo(ac):
    await presentes(ac, OITO[:5])
    rodada = (await sortear(ac)).json()["rodada"]
    assert [t["incompleto"] for t in rodada["times"]] == [False, False, True]
    assert nomes_time(rodada["times"][-1]) == ["Eva Cinco"]  # chegou em 5º
    assert rodada["times"][-1]["fila"] == 3


@pytest.mark.asyncio
async def test_so_uma_rodada_ativa_inclusive_concorrente(ac):
    await presentes(ac, OITO)
    respostas = await asyncio.gather(*[sortear(ac) for _ in range(5)])
    assert sorted(r.status_code for r in respostas) == [201] + [409] * 4
    with sqlite3.connect(settings.gerenciador_db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM rodadas").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM times").fetchone()[0] == 4


@pytest.mark.asyncio
async def test_resortear_troca_combinacao_e_alvo(ac):
    await presentes(
        ac, [(f"Jog{chr(65 + i)} Teste", "M", 60 + (i % 3)) for i in range(8)]
    )
    primeira = (await sortear(ac, 10)).json()["rodada"]
    assert primeira["distintas"] > 1
    segunda = (await ac.post("/api/rodada/resortear", json={"alvo": 12})).json()[
        "rodada"
    ]
    assert (segunda["tentativa"], segunda["alvo"]) == (1, 12)
    assert [nomes_time(t) for t in segunda["times"]] != [
        nomes_time(t) for t in primeira["times"]
    ]
    amplitude = lambda r: (
        max(t["soma"] for t in r["times"]) - min(t["soma"] for t in r["times"])
    )
    assert amplitude(segunda) <= amplitude(primeira) + 3
    # sem alvo no corpo, mantém o atual
    terceira = (await ac.post("/api/rodada/resortear", json={})).json()["rodada"]
    assert terceira["alvo"] == 12 and terceira["tentativa"] == 2
    assert (await ac.post("/api/rodada/resortear", json={"alvo": 5})).status_code == 422
    # continua um estado só, com um só conjunto de times
    with sqlite3.connect(settings.gerenciador_db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM times").fetchone()[0] == 4


@pytest.mark.asyncio
async def test_acoes_sem_proposta_sao_409(ac):
    await presentes(ac, OITO)
    for caminho in ("resortear", "confirmar", "descartar", "cancelar"):
        assert (await ac.post(f"/api/rodada/{caminho}", json={})).status_code == 409


@pytest.mark.asyncio
async def test_ciclo_confirmar_trava_presenca_e_cancelar_destrava(ac):
    ids = await presentes(ac, OITO)
    await sortear(ac)
    r = await ac.post("/api/rodada/confirmar")
    assert (
        r.json()["rodada"]["estado"] == "em_andamento"
        and r.json()["rodada"]["alvo"] == 10
    )
    # confirmada: não resorteia, não descarta, não sorteia outra
    assert (await ac.post("/api/rodada/resortear", json={})).status_code == 409
    assert (await ac.post("/api/rodada/descartar")).status_code == 409
    assert (await sortear(ac)).status_code == 409
    # presença travada
    assert (await ac.delete(f"/api/sessao/presencas/{ids[0]}")).status_code == 409
    assert (
        await ac.put("/api/sessao/ordem", json={"jogador_ids": ids})
    ).status_code == 409
    r = await ac.post(
        "/api/sessao/presencas/rapido", json={"nome": "Novo Jogador", "genero": "M"}
    )
    assert r.status_code == 409
    assert (
        len((await ac.get("/api/jogadores")).json()["jogadores"]) == 8
    )  # nada de órfão
    j = (
        await ac.post("/api/jogadores", json={"nome": "Outro Jogador", "genero": "H"})
    ).json()
    assert (await ac.put(f"/api/sessao/presencas/{j['id']}")).status_code == 409
    # inativar quem está na rodada
    assert (await ac.post(f"/api/jogadores/{ids[0]}/inativar")).status_code == 409
    # encerrar a sessão
    assert (await ac.post("/api/sessao/encerrar")).status_code == 409
    # o estado da sessão traz a rodada
    assert (await ac.get("/api/sessao")).json()["rodada"]["estado"] == "em_andamento"

    cancelada = (await ac.post("/api/rodada/cancelar")).json()
    assert cancelada["rodada"] is None
    assert (await ac.delete(f"/api/sessao/presencas/{ids[0]}")).status_code == 200
    assert (await ac.post(f"/api/jogadores/{ids[1]}/inativar")).status_code == 200
    # nova proposta é a rodada 2
    await ac.put(f"/api/sessao/presencas/{ids[0]}")
    await ac.post(f"/api/jogadores/{ids[1]}/reativar")
    await ac.put(f"/api/sessao/presencas/{ids[1]}")
    assert (await sortear(ac)).json()["rodada"]["numero"] == 2


@pytest.mark.asyncio
async def test_descartar_apaga_e_libera_presenca_e_reaproveita_numero(ac):
    ids = await presentes(ac, OITO)
    await sortear(ac)
    # proposta já trava a presença
    assert (await ac.delete(f"/api/sessao/presencas/{ids[0]}")).status_code == 409
    r = await ac.post("/api/rodada/descartar")
    assert r.json()["rodada"] is None
    with sqlite3.connect(settings.gerenciador_db_path) as conn:
        for tabela in ("rodadas", "times", "time_jogadores"):
            assert conn.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0] == 0
    assert (await ac.delete(f"/api/sessao/presencas/{ids[0]}")).status_code == 200
    await ac.put(f"/api/sessao/presencas/{ids[0]}")
    assert (await sortear(ac)).json()["rodada"]["numero"] == 1


@pytest.mark.asyncio
async def test_rodada_guarda_a_nota_do_sorteio(ac):
    ids = await presentes(ac, OITO)
    antes = (await sortear(ac)).json()["rodada"]
    await ac.patch(
        f"/api/jogadores/{ids[0]}", json={"nome": "Ana Um", "genero": "M", "nota": 5}
    )
    depois = (await ac.get("/api/sessao")).json()["rodada"]
    assert [[j["nota"] for j in t["jogadores"]] for t in depois["times"]] == [
        [j["nota"] for j in t["jogadores"]] for t in antes["times"]
    ]


@pytest.mark.asyncio
async def test_persiste_apos_reset_e_migra_do_schema_3(ac, tmp_path):
    await presentes(ac, OITO)
    await sortear(ac)
    await ac.post("/api/rodada/confirmar")
    settings.reset_db_on_startup = True
    await init_db(settings.db_path)
    init_gerenciador_sync()
    init_gerenciador_sync()  # idempotente
    assert (await ac.get("/api/sessao")).json()["rodada"]["estado"] == "em_andamento"

    # banco da 0.33.x (schema 3, sem tabelas de rodada) migra sem perder nada
    antigo = str(tmp_path / "v3.db")
    conn = sqlite3.connect(antigo)
    conn.executescript(
        """
        CREATE TABLE jogadores (id TEXT PRIMARY KEY, nome TEXT NOT NULL, nome_chave TEXT NOT NULL,
            genero TEXT NOT NULL, nota INTEGER NOT NULL DEFAULT 60, ativo INTEGER NOT NULL DEFAULT 1,
            criado_em TEXT NOT NULL, atualizado_em TEXT NOT NULL);
        CREATE TABLE sessoes (id TEXT PRIMARY KEY, aberta_em TEXT NOT NULL, encerrada_em TEXT);
        INSERT INTO jogadores VALUES ('a1','Ana Souza','ana souza','M',70,1,'x','x');
        INSERT INTO sessoes VALUES ('s1','x',NULL);
        PRAGMA user_version = 3;
        """
    )
    conn.commit()
    conn.close()
    settings.gerenciador_db_path = antigo
    init_gerenciador_sync()
    estado = (await ac.get("/api/sessao")).json()
    assert estado["sessao"]["id"] == "s1" and estado["rodada"] is None
    assert len((await ac.get("/api/jogadores")).json()["jogadores"]) == 1
