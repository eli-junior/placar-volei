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


async def criar(ac, nome="Ana", genero="M"):
    return await ac.post("/api/jogadores", json={"nome": nome, "genero": genero})


@pytest.mark.asyncio
async def test_sem_segredo_retorna_404():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        assert (await c.get("/api/jogadores")).status_code == 404
        r = await c.post("/api/jogadores", json={"nome": "Ana", "genero": "M"})
        assert r.status_code == 404


@pytest.mark.asyncio
async def test_criar_e_listar(ac):
    r = await criar(ac, "  Ana   Paula ", "m")
    assert r.status_code == 201
    assert r.json()["nome"] == "Ana Paula" and r.json()["genero"] == "M"
    lista = (await ac.get("/api/jogadores")).json()["jogadores"]
    assert [j["nome"] for j in lista] == ["Ana Paula"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "corpo,campo",
    [
        ({"nome": "", "genero": "M"}, "nome"),
        ({"nome": "   ", "genero": "M"}, "nome"),
        ({"nome": "x" * 41, "genero": "M"}, "nome"),
        ({"nome": "Ana"}, "genero"),
        ({"nome": "Ana", "genero": "X"}, "genero"),
        ({"genero": "H"}, "nome"),
    ],
)
async def test_validacao(ac, corpo, campo):
    r = await ac.post("/api/jogadores", json=corpo)
    assert r.status_code == 422
    assert r.json()["erros"][0]["campo"] == campo
    assert (await ac.get("/api/jogadores")).json()["jogadores"] == []


@pytest.mark.asyncio
@pytest.mark.parametrize("repetido", ["ana", "ANA", " Ana "])
async def test_nome_unico_sem_caixa(ac, repetido):
    await criar(ac, "Ana")
    r = await criar(ac, repetido)
    assert r.status_code == 409
    assert r.json()["erros"][0]["campo"] == "nome"
    assert len((await ac.get("/api/jogadores")).json()["jogadores"]) == 1


@pytest.mark.asyncio
async def test_nome_unico_sem_acento(ac):
    await criar(ac, "João", "H")
    assert (await criar(ac, "joao", "H")).status_code == 409


@pytest.mark.asyncio
async def test_editar_e_conflito(ac):
    ana = (await criar(ac, "Ana")).json()
    await criar(ac, "Bia")
    r = await ac.patch(
        f"/api/jogadores/{ana['id']}", json={"nome": "Ana", "genero": "H"}
    )
    assert r.status_code == 200 and r.json()["genero"] == "H"
    r = await ac.patch(
        f"/api/jogadores/{ana['id']}", json={"nome": "bia", "genero": "M"}
    )
    assert r.status_code == 409
    r = await ac.patch("/api/jogadores/inexistente", json={"nome": "Z", "genero": "M"})
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_inativar_libera_nome_e_reativar_respeita_unicidade(ac):
    ana = (await criar(ac, "Ana")).json()
    r = await ac.post(f"/api/jogadores/{ana['id']}/inativar")
    assert r.status_code == 200 and r.json()["ativo"] is False
    assert (await ac.get("/api/jogadores")).json()["jogadores"] == []
    todos = (await ac.get("/api/jogadores?incluir_inativos=true")).json()["jogadores"]
    assert len(todos) == 1
    assert (await criar(ac, "Ana")).status_code == 201
    r = await ac.post(f"/api/jogadores/{ana['id']}/reativar")
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_persiste_apos_reset_do_banco_das_quadras(ac):
    await criar(ac, "Ana")
    settings.reset_db_on_startup = True
    await init_db(settings.db_path)
    init_jogadores_sync()
    lista = (await ac.get("/api/jogadores")).json()["jogadores"]
    assert [j["nome"] for j in lista] == ["Ana"]


@pytest.mark.asyncio
async def test_persiste_com_schema_das_quadras_diferente(ac):
    await criar(ac, "Ana")
    with sqlite3.connect(settings.db_path) as conn:
        conn.execute("UPDATE app_meta SET valor = 'outro' WHERE chave = 'schema'")
    await init_db(settings.db_path)  # schema "novo": apaga só o banco das quadras
    assert len((await ac.get("/api/jogadores")).json()["jogadores"]) == 1
