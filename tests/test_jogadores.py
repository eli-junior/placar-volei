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


async def criar(ac, nome="Ana Souza", genero="M"):
    return await ac.post("/api/jogadores", json={"nome": nome, "genero": genero})


@pytest.mark.asyncio
async def test_sem_segredo_retorna_404():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        assert (await c.get("/api/jogadores")).status_code == 404
        r = await c.post("/api/jogadores", json={"nome": "Ana Souza", "genero": "M"})
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
        ({"nome": "Ana Souza"}, "genero"),
        ({"nome": "Ana Souza", "genero": "X"}, "genero"),
        ({"genero": "H"}, "nome"),
    ],
)
async def test_validacao(ac, corpo, campo):
    r = await ac.post("/api/jogadores", json=corpo)
    assert r.status_code == 422
    assert r.json()["erros"][0]["campo"] == campo
    assert (await ac.get("/api/jogadores")).json()["jogadores"] == []


@pytest.mark.asyncio
@pytest.mark.parametrize("repetido", ["ana souza", "ANA SOUZA", " Ana  Souza "])
async def test_nome_unico_sem_caixa(ac, repetido):
    await criar(ac, "Ana Souza")
    r = await criar(ac, repetido)
    assert r.status_code == 409
    assert r.json()["erros"][0]["campo"] == "nome"
    assert len((await ac.get("/api/jogadores")).json()["jogadores"]) == 1


@pytest.mark.asyncio
async def test_nome_unico_sem_acento(ac):
    await criar(ac, "João Silva", "H")
    assert (await criar(ac, "joao silva", "H")).status_code == 409


@pytest.mark.asyncio
async def test_editar_e_conflito(ac):
    ana = (await criar(ac, "Ana Souza")).json()
    await criar(ac, "Bia Lima")
    r = await ac.patch(
        f"/api/jogadores/{ana['id']}", json={"nome": "Ana Souza", "genero": "H"}
    )
    assert r.status_code == 200 and r.json()["genero"] == "H"
    r = await ac.patch(
        f"/api/jogadores/{ana['id']}", json={"nome": "bia lima", "genero": "M"}
    )
    assert r.status_code == 409
    r = await ac.patch(
        "/api/jogadores/inexistente", json={"nome": "Zé Souza", "genero": "M"}
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_inativar_libera_nome_e_reativar_respeita_unicidade(ac):
    ana = (await criar(ac, "Ana Souza")).json()
    r = await ac.post(f"/api/jogadores/{ana['id']}/inativar")
    assert r.status_code == 200 and r.json()["ativo"] is False
    assert (await ac.get("/api/jogadores")).json()["jogadores"] == []
    todos = (await ac.get("/api/jogadores?incluir_inativos=true")).json()["jogadores"]
    assert len(todos) == 1
    assert (await criar(ac, "Ana Souza")).status_code == 201
    r = await ac.post(f"/api/jogadores/{ana['id']}/reativar")
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_persiste_apos_reset_do_banco_das_quadras(ac):
    await criar(ac, "Ana Souza")
    settings.reset_db_on_startup = True
    await init_db(settings.db_path)
    init_jogadores_sync()
    lista = (await ac.get("/api/jogadores")).json()["jogadores"]
    assert [j["nome"] for j in lista] == ["Ana Souza"]


@pytest.mark.asyncio
async def test_persiste_com_schema_das_quadras_diferente(ac):
    await criar(ac, "Ana Souza")
    with sqlite3.connect(settings.db_path) as conn:
        conn.execute("UPDATE app_meta SET valor = 'outro' WHERE chave = 'schema'")
    await init_db(settings.db_path)  # schema "novo": apaga só o banco das quadras
    assert len((await ac.get("/api/jogadores")).json()["jogadores"]) == 1


# --- CV8.DS1.US15: nota, sobrenome e foto ---

JPEG = b"\xff\xd8\xff\xe0" + b"0" * 100


@pytest.mark.asyncio
async def test_nota_padrao_60_e_informada(ac):
    assert (await criar(ac, "Ana Souza")).json()["nota"] == 60
    r = await ac.post(
        "/api/jogadores", json={"nome": "Bia Lima", "genero": "M", "nota": 87}
    )
    assert r.json()["nota"] == 87
    r = await ac.post(
        "/api/jogadores", json={"nome": "Caio Reis", "genero": "H", "nota": 1.0}
    )
    assert r.json()["nota"] == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("nota", [0, 101, -5, 7.5, "abc", True, [60]])
async def test_nota_invalida(ac, nota):
    r = await ac.post(
        "/api/jogadores", json={"nome": "Ana Souza", "genero": "M", "nota": nota}
    )
    assert r.status_code == 422
    assert r.json()["erros"][0]["campo"] == "nota"
    assert (await ac.get("/api/jogadores")).json()["jogadores"] == []


@pytest.mark.asyncio
async def test_editar_nota_e_omitida_mantem(ac):
    j = (
        await ac.post(
            "/api/jogadores", json={"nome": "Ana Souza", "genero": "M", "nota": 80}
        )
    ).json()
    r = await ac.patch(
        f"/api/jogadores/{j['id']}", json={"nome": "Ana Souza", "genero": "M"}
    )
    assert r.json()["nota"] == 80
    r = await ac.patch(
        f"/api/jogadores/{j['id']}",
        json={"nome": "Ana Souza", "genero": "M", "nota": 95},
    )
    assert r.json()["nota"] == 95
    r = await ac.patch(
        f"/api/jogadores/{j['id']}",
        json={"nome": "Ana Souza", "genero": "M", "nota": 0},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize("nome", ["Ana", "  Ana  "])
async def test_nome_exige_duas_palavras(ac, nome):
    r = await criar(ac, nome)
    assert r.status_code == 422
    assert r.json()["erros"][0]["campo"] == "nome"
    assert "sobrenome" in r.json()["detail"]
    ok = (await criar(ac, "Ana Souza")).json()
    r = await ac.patch(f"/api/jogadores/{ok['id']}", json={"nome": nome, "genero": "M"})
    assert r.status_code == 422


def _banco_da_0_31_0(caminho):
    conn = sqlite3.connect(caminho)
    conn.executescript(
        """
        CREATE TABLE jogadores (
            id TEXT PRIMARY KEY, nome TEXT NOT NULL, nome_chave TEXT NOT NULL,
            genero TEXT NOT NULL CHECK (genero IN ('H', 'M')),
            ativo INTEGER NOT NULL DEFAULT 1,
            criado_em TEXT NOT NULL, atualizado_em TEXT NOT NULL);
        CREATE UNIQUE INDEX idx_jogadores_nome_ativo ON jogadores (nome_chave) WHERE ativo = 1;
        INSERT INTO jogadores VALUES ('a1', 'Ana', 'ana', 'M', 1, 'x', 'x');
        INSERT INTO jogadores VALUES ('b1', 'Bia Lima', 'bia lima', 'M', 0, 'x', 'x');
        PRAGMA user_version = 1;
        """
    )
    conn.commit()
    conn.close()


@pytest.mark.asyncio
async def test_migracao_da_0_31_0_preserva_dados_com_nota_60(ac, tmp_path):
    antigo = str(tmp_path / "antigo.db")
    _banco_da_0_31_0(antigo)
    settings.gerenciador_db_path = antigo
    init_jogadores_sync()
    init_jogadores_sync()  # idempotente
    lista = (await ac.get("/api/jogadores?incluir_inativos=true")).json()["jogadores"]
    assert {(j["nome"], j["nota"], j["ativo"]) for j in lista} == {
        ("Ana", 60, True),
        ("Bia Lima", 60, False),
    }
    # nome legado de uma palavra segue listado; editar exige completar
    r = await ac.patch("/api/jogadores/a1", json={"nome": "Ana", "genero": "M"})
    assert r.status_code == 422
    r = await ac.patch("/api/jogadores/a1", json={"nome": "Ana Souza", "genero": "M"})
    assert r.status_code == 200
    # reativar legado não reescreve o nome
    assert (await ac.post("/api/jogadores/b1/reativar")).status_code == 200


@pytest.mark.asyncio
async def test_foto_ciclo_completo(ac):
    j = (await criar(ac)).json()
    assert j["tem_foto"] is False
    assert (await ac.get(f"/api/jogadores/{j['id']}/foto")).status_code == 404

    r = await ac.put(
        f"/api/jogadores/{j['id']}/foto",
        content=JPEG,
        headers={"content-type": "image/jpeg"},
    )
    assert r.status_code == 200 and r.json()["tem_foto"] is True
    g = await ac.get(f"/api/jogadores/{j['id']}/foto")
    assert g.status_code == 200 and g.content == JPEG
    assert g.headers["content-type"] == "image/jpeg"
    etag = g.headers["etag"]
    assert (
        await ac.get(f"/api/jogadores/{j['id']}/foto", headers={"if-none-match": etag})
    ).status_code == 304
    lista = (await ac.get("/api/jogadores")).json()["jogadores"]
    assert lista[0]["tem_foto"] is True

    nova = JPEG + b"1"
    await ac.put(f"/api/jogadores/{j['id']}/foto", content=nova)
    assert (await ac.get(f"/api/jogadores/{j['id']}/foto")).content == nova

    r = await ac.delete(f"/api/jogadores/{j['id']}/foto")
    assert r.status_code == 200 and r.json()["tem_foto"] is False
    assert (await ac.get(f"/api/jogadores/{j['id']}/foto")).status_code == 404


@pytest.mark.asyncio
async def test_foto_recusa_formato_e_tamanho_e_mantem_a_anterior(ac):
    j = (await criar(ac)).json()
    await ac.put(f"/api/jogadores/{j['id']}/foto", content=JPEG)
    r = await ac.put(f"/api/jogadores/{j['id']}/foto", content=b"\x89PNG" + b"0" * 50)
    assert r.status_code == 422 and r.json()["erros"][0]["campo"] == "foto"
    r = await ac.put(
        f"/api/jogadores/{j['id']}/foto", content=JPEG + b"0" * (256 * 1024)
    )
    assert r.status_code == 413
    assert (await ac.get(f"/api/jogadores/{j['id']}/foto")).content == JPEG
    r = await ac.put("/api/jogadores/inexistente/foto", content=JPEG)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_foto_exige_segredo():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        assert (await c.get("/api/jogadores/x/foto")).status_code == 404
        assert (await c.put("/api/jogadores/x/foto", content=JPEG)).status_code == 404
        assert (await c.delete("/api/jogadores/x/foto")).status_code == 404


@pytest.mark.asyncio
async def test_foto_persiste_apos_reset(ac):
    j = (await criar(ac)).json()
    await ac.put(f"/api/jogadores/{j['id']}/foto", content=JPEG)
    settings.reset_db_on_startup = True
    await init_db(settings.db_path)
    init_jogadores_sync()
    assert (await ac.get(f"/api/jogadores/{j['id']}/foto")).content == JPEG
