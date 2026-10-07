import asyncio
import sqlite3
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.db import init_db
from app.jogadores import init_jogadores_sync
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
    init_jogadores_sync()
    yield
    owner_rate_limiter.resetar()


@pytest.fixture
async def ac():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", headers=SEGREDO
    ) as c:
        yield c


async def jogador(ac, nome, genero="M", nota=None):
    corpo = {"nome": nome, "genero": genero}
    if nota is not None:
        corpo["nota"] = nota
    return (await ac.post("/api/jogadores", json=corpo)).json()


async def abrir(ac):
    r = await ac.post("/api/sessao")
    assert r.status_code == 201
    return r.json()


def nomes(estado):
    return [p["nome"] for p in estado["presentes"]]


@pytest.mark.asyncio
async def test_sem_segredo_retorna_404():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        assert (await c.get("/api/sessao")).status_code == 404
        assert (await c.post("/api/sessao")).status_code == 404
        assert (await c.put("/api/sessao/presencas/x")).status_code == 404
        assert (await c.put("/api/sessao/ordem", json={})).status_code == 404


@pytest.mark.asyncio
async def test_sem_sessao_estado_vazio_e_operacoes_409(ac):
    j = await jogador(ac, "Ana Souza")
    e = (await ac.get("/api/sessao")).json()
    assert e["sessao"] is None and e["presentes"] == [] and e["minimo"] == 4
    assert (await ac.put(f"/api/sessao/presencas/{j['id']}")).status_code == 409
    assert (await ac.delete(f"/api/sessao/presencas/{j['id']}")).status_code == 409
    assert (
        await ac.put("/api/sessao/ordem", json={"jogador_ids": []})
    ).status_code == 409
    assert (await ac.post("/api/sessao/encerrar")).status_code == 409
    r = await ac.post(
        "/api/sessao/presencas/rapido", json={"nome": "Bia Lima", "genero": "M"}
    )
    assert r.status_code == 409
    # nada de jogador órfão criado pelo cadastro rápido
    assert len((await ac.get("/api/jogadores")).json()["jogadores"]) == 1


@pytest.mark.asyncio
async def test_so_uma_sessao_aberta(ac):
    await abrir(ac)
    r = await ac.post("/api/sessao")
    assert r.status_code == 409 and r.json()["erros"][0]["campo"] == "sessao"


@pytest.mark.asyncio
async def test_aberturas_concorrentes_criam_uma_so(ac):
    respostas = await asyncio.gather(*[ac.post("/api/sessao") for _ in range(6)])
    assert sorted(r.status_code for r in respostas) == [201] + [409] * 5
    with sqlite3.connect(settings.gerenciador_db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM sessoes").fetchone()[0] == 1


@pytest.mark.asyncio
async def test_encerrar_libera_nova_sessao_e_limpa_a_tela(ac):
    j = await jogador(ac, "Ana Souza")
    await abrir(ac)
    await ac.put(f"/api/sessao/presencas/{j['id']}")
    e = (await ac.post("/api/sessao/encerrar")).json()
    assert e["sessao"] is None and e["presentes"] == []
    nova = await abrir(ac)
    assert nova["presentes"] == []  # a presença não vaza para a sessão nova


@pytest.mark.asyncio
async def test_ordem_de_chegada_e_desmarcar_recompacta(ac):
    a, b, c = [await jogador(ac, n) for n in ("Ana Souza", "Bia Lima", "Caio Reis")]
    await abrir(ac)
    for j in (a, b, c):
        e = (await ac.put(f"/api/sessao/presencas/{j['id']}")).json()
    assert nomes(e) == ["Ana Souza", "Bia Lima", "Caio Reis"]
    assert [p["ordem"] for p in e["presentes"]] == [1, 2, 3]
    assert e["ausentes"] == []
    # marcar de novo quem já está é idempotente
    assert (
        nomes((await ac.put(f"/api/sessao/presencas/{a['id']}")).json())[0]
        == "Ana Souza"
    )
    # desmarcar e marcar: vai para o fim
    e = (await ac.delete(f"/api/sessao/presencas/{a['id']}")).json()
    assert nomes(e) == ["Bia Lima", "Caio Reis"] and [
        p["ordem"] for p in e["presentes"]
    ] == [1, 2]
    assert [x["nome"] for x in e["ausentes"]] == ["Ana Souza"]
    e = (await ac.put(f"/api/sessao/presencas/{a['id']}")).json()
    assert nomes(e) == ["Bia Lima", "Caio Reis", "Ana Souza"]


@pytest.mark.asyncio
async def test_so_ativos_e_existentes_podem_ser_marcados(ac):
    j = await jogador(ac, "Ana Souza")
    await ac.post(f"/api/jogadores/{j['id']}/inativar")
    await abrir(ac)
    assert (await ac.put(f"/api/sessao/presencas/{j['id']}")).status_code == 409
    assert (await ac.put("/api/sessao/presencas/inexistente")).status_code == 404
    assert (await ac.get("/api/sessao")).json()["ausentes"] == []


@pytest.mark.asyncio
async def test_reordenar_valido_e_invalido(ac):
    a, b, c = [await jogador(ac, n) for n in ("Ana Souza", "Bia Lima", "Caio Reis")]
    await abrir(ac)
    for j in (a, b, c):
        await ac.put(f"/api/sessao/presencas/{j['id']}")
    e = (
        await ac.put(
            "/api/sessao/ordem", json={"jogador_ids": [c["id"], a["id"], b["id"]]}
        )
    ).json()
    assert nomes(e) == ["Caio Reis", "Ana Souza", "Bia Lima"]
    assert nomes((await ac.get("/api/sessao")).json()) == nomes(e)
    for ruim in (
        [a["id"], b["id"]],  # falta um
        [a["id"], a["id"], b["id"]],  # repetido
        [a["id"], b["id"], c["id"], "x"],  # sobra
        "abc",
        None,
        [1, 2, 3],
    ):
        r = await ac.put("/api/sessao/ordem", json={"jogador_ids": ruim})
        assert r.status_code == 422 and r.json()["erros"][0]["campo"] == "jogador_ids"
    assert nomes((await ac.get("/api/sessao")).json()) == nomes(e)


@pytest.mark.asyncio
async def test_cadastro_rapido_cria_e_marca_no_fim(ac):
    a = await jogador(ac, "Ana Souza")
    await abrir(ac)
    await ac.put(f"/api/sessao/presencas/{a['id']}")
    r = await ac.post(
        "/api/sessao/presencas/rapido", json={"nome": "Bia  Lima", "genero": "m"}
    )
    assert r.status_code == 201
    corpo = r.json()
    assert corpo["jogador"]["nota"] == 60 and corpo["jogador"]["nome"] == "Bia Lima"
    assert nomes(corpo) == ["Ana Souza", "Bia Lima"]
    # as validações da US1/US15 valem
    assert (
        await ac.post(
            "/api/sessao/presencas/rapido", json={"nome": "Bia", "genero": "M"}
        )
    ).status_code == 422
    assert (
        await ac.post(
            "/api/sessao/presencas/rapido", json={"nome": "bia lima", "genero": "M"}
        )
    ).status_code == 409
    assert (
        await ac.post(
            "/api/sessao/presencas/rapido",
            json={"nome": "Caio Reis", "genero": "H", "nota": 0},
        )
    ).status_code == 422
    assert len(nomes((await ac.get("/api/sessao")).json())) == 2


@pytest.mark.asyncio
async def test_inativar_presente_remove_e_recompacta_reativar_nao_recoloca(ac):
    a, b, c = [await jogador(ac, n) for n in ("Ana Souza", "Bia Lima", "Caio Reis")]
    await abrir(ac)
    for j in (a, b, c):
        await ac.put(f"/api/sessao/presencas/{j['id']}")
    await ac.post(f"/api/jogadores/{b['id']}/inativar")
    e = (await ac.get("/api/sessao")).json()
    assert nomes(e) == ["Ana Souza", "Caio Reis"] and [
        p["ordem"] for p in e["presentes"]
    ] == [1, 2]
    await ac.post(f"/api/jogadores/{b['id']}/reativar")
    e = (await ac.get("/api/sessao")).json()
    assert nomes(e) == ["Ana Souza", "Caio Reis"]
    assert [x["nome"] for x in e["ausentes"]] == ["Bia Lima"]


@pytest.mark.asyncio
async def test_marcacoes_concorrentes_nao_repetem_posicao(ac):
    js = [await jogador(ac, f"Jogador{chr(65 + i)} Teste") for i in range(8)]
    await abrir(ac)
    await asyncio.gather(*[ac.put(f"/api/sessao/presencas/{j['id']}") for j in js])
    e = (await ac.get("/api/sessao")).json()
    assert [p["ordem"] for p in e["presentes"]] == list(range(1, 9))


@pytest.mark.asyncio
async def test_persiste_apos_reset_e_migra_do_schema_2(ac, tmp_path):
    j = await jogador(ac, "Ana Souza")
    await abrir(ac)
    await ac.put(f"/api/sessao/presencas/{j['id']}")
    settings.reset_db_on_startup = True
    await init_db(settings.db_path)
    init_jogadores_sync()
    init_jogadores_sync()  # idempotente
    e = (await ac.get("/api/sessao")).json()
    assert e["sessao"] is not None and nomes(e) == ["Ana Souza"]

    # banco da 0.32.0 (sem as tabelas de sessão) migra sem perder jogadores
    antigo = str(tmp_path / "v2.db")
    conn = sqlite3.connect(antigo)
    conn.executescript(
        """
        CREATE TABLE jogadores (id TEXT PRIMARY KEY, nome TEXT NOT NULL, nome_chave TEXT NOT NULL,
            genero TEXT NOT NULL, nota INTEGER NOT NULL DEFAULT 60, ativo INTEGER NOT NULL DEFAULT 1,
            criado_em TEXT NOT NULL, atualizado_em TEXT NOT NULL);
        INSERT INTO jogadores VALUES ('a1','Ana Souza','ana souza','M',70,1,'x','x');
        PRAGMA user_version = 2;
        """
    )
    conn.commit()
    conn.close()
    settings.gerenciador_db_path = antigo
    init_jogadores_sync()
    assert (await ac.get("/api/sessao")).json()["sessao"] is None
    assert len((await ac.get("/api/jogadores")).json()["jogadores"]) == 1
    await abrir(ac)
    assert (await ac.put("/api/sessao/presencas/a1")).status_code == 200


@pytest.mark.asyncio
async def test_desmarcar_depois_de_reordenar_nao_empata_posicoes(ac):
    js = [await jogador(ac, f"Jogador{chr(65 + i)} Teste") for i in range(6)]
    await abrir(ac)
    for j in js:
        await ac.put(f"/api/sessao/presencas/{j['id']}")
    ids = [j["id"] for j in js]
    nova = [ids[3], ids[0], ids[5], ids[1], ids[4], ids[2]]
    await ac.put("/api/sessao/ordem", json={"jogador_ids": nova})
    esperado = list(nova)
    for tirar in (ids[1], ids[3], ids[2]):
        e = (await ac.delete(f"/api/sessao/presencas/{tirar}")).json()
        esperado.remove(tirar)
        assert [p["id"] for p in e["presentes"]] == esperado
    with sqlite3.connect(settings.gerenciador_db_path) as conn:
        ordens = [
            r[0] for r in conn.execute("SELECT ordem FROM presencas ORDER BY ordem")
        ]
    assert ordens == list(range(1, len(esperado) + 1))
