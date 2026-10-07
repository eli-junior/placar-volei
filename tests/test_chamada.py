import asyncio
import sqlite3
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app import ponte
from app.comandos import snapshot_sync
from app.config import settings
from app.db import init_db
from app.gerenciador_db import init_gerenciador_sync
from app.main import app
from app.rate_limit import owner_rate_limiter

SEGREDO = {"x-owner-secret": "segredo-teste"}

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


@pytest.fixture
async def placar():
    """Cliente do placar de sempre (com cookie de participante), sem segredo."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


async def quadra_do_placar(placar, nome="Quadra 1") -> str:
    r = await placar.post("/api/quadras", json={"apelido": "Operador", "nome": nome})
    assert r.status_code == 201
    return r.json()["id"]


async def rodada_em_andamento(ac, especificacao=OITO, alvo=12):
    await ac.post("/api/sessao")
    for nome, genero, nota in especificacao:
        j = (
            await ac.post(
                "/api/jogadores", json={"nome": nome, "genero": genero, "nota": nota}
            )
        ).json()
        await ac.put(f"/api/sessao/presencas/{j['id']}")
    await ac.post("/api/rodada/sorteio", json={"alvo": alvo})
    return (await ac.post("/api/rodada/confirmar")).json()


def estado_placar(codigo):
    return snapshot_sync(settings.db_path, codigo)["estado_partida"]


@pytest.mark.asyncio
async def test_sem_segredo_retorna_404():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        assert (
            await c.put("/api/sessao/quadra", json={"codigo": "12345"})
        ).status_code == 404
        assert (await c.delete("/api/sessao/quadra")).status_code == 404
        assert (await c.post("/api/rodada/chamar-partida")).status_code == 404


@pytest.mark.asyncio
async def test_vincular_validacoes_e_desvincular(ac, placar):
    assert (
        await ac.put("/api/sessao/quadra", json={"codigo": "12345"})
    ).status_code == 409  # sem sessão
    await ac.post("/api/sessao")
    for ruim in (None, "", "abc", "1234", "123456", [1], True):
        r = await ac.put("/api/sessao/quadra", json={"codigo": ruim})
        assert r.status_code == 422 and r.json()["erros"][0]["campo"] == "codigo", ruim
    r = await ac.put("/api/sessao/quadra", json={"codigo": "99999"})
    assert r.status_code == 409 and r.json()["erros"][0]["campo"] == "quadra"
    codigo = await quadra_do_placar(placar)
    estado = (await ac.put("/api/sessao/quadra", json={"codigo": codigo})).json()
    assert estado["quadra"] == {
        "codigo": codigo,
        "nome": "Quadra 1",
        "disponivel": True,
    }
    assert (await ac.get("/api/sessao")).json()["quadra"]["codigo"] == codigo
    estado = (await ac.delete("/api/sessao/quadra")).json()
    assert estado["quadra"] is None


@pytest.mark.asyncio
async def test_painel_inicial_e_gate_sem_quadra(ac, placar):
    estado = await rodada_em_andamento(ac)
    c = estado["conducao"]
    assert c["fase"] == "fila" and [t["fila"] for t in c["em_quadra"]] == [1, 2]
    assert [t["fila"] for t in c["fila"]] == [3, 4]
    assert c["reis"] == [] and c["eliminados"] == [] and c["partida"] is None
    assert c["pode_chamar"] is False and "Vincule uma quadra" in c["motivo"]
    r = await ac.post("/api/rodada/chamar-partida")
    assert r.status_code == 409 and "Vincule" in r.json()["detail"]
    codigo = await quadra_do_placar(placar)
    estado = (await ac.put("/api/sessao/quadra", json={"codigo": codigo})).json()
    assert (
        estado["conducao"]["pode_chamar"] is True
        and estado["conducao"]["motivo"] is None
    )


@pytest.mark.asyncio
async def test_conducao_so_existe_com_rodada_em_andamento(ac):
    await ac.post("/api/sessao")
    assert (await ac.get("/api/sessao")).json()["conducao"] is None
    for nome, genero, nota in OITO:
        j = (
            await ac.post(
                "/api/jogadores", json={"nome": nome, "genero": genero, "nota": nota}
            )
        ).json()
        await ac.put(f"/api/sessao/presencas/{j['id']}")
    assert (await ac.post("/api/rodada/sorteio", json={"alvo": 10})).json()[
        "conducao"
    ] is None


@pytest.mark.asyncio
async def test_chamar_carrega_o_placar(ac, placar):
    await rodada_em_andamento(ac, alvo=12)
    codigo = await quadra_do_placar(placar)
    await ac.put("/api/sessao/quadra", json={"codigo": codigo})
    r = await ac.post("/api/rodada/chamar-partida")
    assert r.status_code == 201
    c = r.json()["conducao"]
    assert c["partida"]["ordem"] == 1 and (
        c["partida"]["time_a"],
        c["partida"]["time_b"],
    ) == (1, 2)
    assert c["pode_chamar"] is False and "partida chamada" in c["motivo"]
    # o time 1 é Ana Um + Gil Sete, o 2 é Bia Dois + Fabio Seis (exemplo do guia da US3)
    p = estado_placar(codigo)
    assert (p["equipe_a"], p["equipe_b"]) == ("Ana + Gil", "Bia + Fabio")
    assert list(p["jogadores_a"]) == ["Ana", "Gil"] and list(p["jogadores_b"]) == [
        "Bia",
        "Fabio",
    ]
    assert (p["alvo"], p["vantagem"], p["pontos_a"], p["pontos_b"], p["encerrada"]) == (
        12,
        True,
        0,
        0,
        False,
    )
    with sqlite3.connect(settings.gerenciador_db_path) as conn:
        linha = conn.execute(
            "SELECT estado, quadra_id, partida_quadra_id FROM partidas_rodada"
        ).fetchall()
    assert linha == [
        ("chamada", codigo, snapshot_sync(settings.db_path, codigo)["partida_id"])
    ]
    # nada de partida nova a cada chamada: a segunda é recusada
    assert (await ac.post("/api/rodada/chamar-partida")).status_code == 409


@pytest.mark.asyncio
async def test_chamadas_concorrentes_criam_uma_so(ac, placar):
    await rodada_em_andamento(ac)
    codigo = await quadra_do_placar(placar)
    await ac.put("/api/sessao/quadra", json={"codigo": codigo})
    respostas = await asyncio.gather(
        *[ac.post("/api/rodada/chamar-partida") for _ in range(4)]
    )
    assert sorted(r.status_code for r in respostas) == [201] + [409] * 3
    with sqlite3.connect(settings.gerenciador_db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM partidas_rodada").fetchone()[0] == 1


@pytest.mark.asyncio
async def test_recusa_se_a_quadra_tem_partida_com_pontos(ac, placar):
    await rodada_em_andamento(ac)
    codigo = await quadra_do_placar(placar)
    await ac.put("/api/sessao/quadra", json={"codigo": codigo})
    versao = str(snapshot_sync(settings.db_path, codigo)["quadra"]["controle_versao"])
    r = await placar.post(
        f"/api/quadras/{codigo}/pontos",
        json={"equipe": "A"},
        headers={"x-control-version": versao},
    )
    assert r.status_code == 201
    r = await ac.post("/api/rodada/chamar-partida")
    assert r.status_code == 409 and "em andamento (1 × 0)" in r.json()["detail"]
    assert estado_placar(codigo)["pontos_a"] == 1  # nada foi zerado
    with sqlite3.connect(settings.gerenciador_db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM partidas_rodada").fetchone()[0] == 0
    # partida encerrada no placar não impede
    for _ in range(11):
        await placar.post(
            f"/api/quadras/{codigo}/pontos",
            json={"equipe": "A"},
            headers={"x-control-version": versao},
        )
    assert estado_placar(codigo)["encerrada"] is True
    assert (await ac.post("/api/rodada/chamar-partida")).status_code == 201
    assert estado_placar(codigo)["pontos_a"] == 0


@pytest.mark.asyncio
async def test_quadra_sumida_fica_indisponivel_e_a_chamada_e_recusada(ac, placar):
    await rodada_em_andamento(ac)
    codigo = await quadra_do_placar(placar)
    await ac.put("/api/sessao/quadra", json={"codigo": codigo})
    with sqlite3.connect(settings.db_path) as conn:  # a quadra do placar é efêmera
        conn.execute("DELETE FROM quadras WHERE id = ?", (codigo,))
    estado = (await ac.get("/api/sessao")).json()
    assert estado["quadra"]["disponivel"] is False
    assert "não está mais disponível" in estado["conducao"]["motivo"]
    r = await ac.post("/api/rodada/chamar-partida")
    assert r.status_code == 409
    with sqlite3.connect(settings.gerenciador_db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM partidas_rodada").fetchone()[0] == 0
    # vincula de novo a uma quadra nova
    novo = await quadra_do_placar(placar, "Quadra 2")
    assert (await ac.put("/api/sessao/quadra", json={"codigo": novo})).json()["quadra"][
        "disponivel"
    ]


@pytest.mark.asyncio
async def test_falha_no_placar_desfaz_o_registro(ac, placar, monkeypatch):
    await rodada_em_andamento(ac)
    codigo = await quadra_do_placar(placar)
    await ac.put("/api/sessao/quadra", json={"codigo": codigo})

    def quebra(*args, **kwargs):
        raise RuntimeError("placar fora do ar")

    monkeypatch.setattr(ponte, "executar_sync", quebra)
    with pytest.raises(RuntimeError):
        await ac.post("/api/rodada/chamar-partida")
    with sqlite3.connect(settings.gerenciador_db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM partidas_rodada").fetchone()[0] == 0
    monkeypatch.undo()
    assert (await ac.post("/api/rodada/chamar-partida")).status_code == 201


@pytest.mark.asyncio
async def test_nao_troca_o_vinculo_com_partida_chamada(ac, placar):
    await rodada_em_andamento(ac)
    codigo = await quadra_do_placar(placar)
    outra = await quadra_do_placar(placar, "Quadra 2")
    await ac.put("/api/sessao/quadra", json={"codigo": codigo})
    await ac.post("/api/rodada/chamar-partida")
    assert (
        await ac.put("/api/sessao/quadra", json={"codigo": outra})
    ).status_code == 409
    assert (await ac.delete("/api/sessao/quadra")).status_code == 409


def _inserir_resultado(rodada, ordem, a_fila, b_fila, vencedor_fila, quadra="00000"):
    por_fila = {t["fila"]: t["id"] for t in rodada["times"]}
    with sqlite3.connect(settings.gerenciador_db_path) as conn:
        conn.execute(
            "INSERT INTO partidas_rodada (id, rodada_id, ordem, time_a_id, time_b_id, estado, "
            "quadra_id, chamada_em, placar_a, placar_b, vencedor_time_id, encerrada_em) "
            "VALUES (?, ?, ?, ?, ?, 'encerrada', ?, 'x', 12, 5, ?, 'x')",
            (
                f"p{ordem}",
                rodada["id"],
                ordem,
                por_fila[a_fila],
                por_fila[b_fila],
                quadra,
                por_fila[vencedor_fila],
            ),
        )


@pytest.mark.asyncio
async def test_painel_com_resultados_reis_eliminados_e_fila(ac, placar):
    # 11 jogadores: 5 duplas completas + 1 incompleta (fila 6)
    espec = [(f"Jog{chr(65 + i)} Teste", "M", 60 + (i % 4)) for i in range(11)]
    estado = await rodada_em_andamento(ac, espec)
    rodada = estado["rodada"]
    _inserir_resultado(rodada, 1, 1, 2, 1)
    _inserir_resultado(rodada, 2, 1, 3, 1)  # time 1 vence 2 seguidas → rei
    c = (await ac.get("/api/sessao")).json()["conducao"]
    assert [t["fila"] for t in c["reis"]] == [1] and c["reis"][0]["ordem"] == 1
    assert [t["fila"] for t in c["em_quadra"]] == [4, 5]
    assert [t["fila"] for t in c["fila"]] == [6]
    assert sorted({e["time"] for e in c["eliminados"]}) == [2, 3]
    assert len(c["eliminados"]) == 4 and c["partidas_encerradas"] == 2
    # gate do time incompleto: t4 vence t5; o incompleto (6) entra contra t4
    _inserir_resultado(rodada, 3, 4, 5, 4)
    codigo = await quadra_do_placar(placar)
    c = (await ac.put("/api/sessao/quadra", json={"codigo": codigo})).json()["conducao"]
    assert [t["fila"] for t in c["em_quadra"]] == [4, 6]
    assert c["pode_chamar"] is False and "Time 6 é incompleto" in c["motivo"]
    r = await ac.post("/api/rodada/chamar-partida")
    assert r.status_code == 409 and "incompleto" in r.json()["detail"]


@pytest.mark.asyncio
async def test_migra_do_schema_4_preservando_dados(ac):
    antigo = str(Path(settings.gerenciador_db_path).with_name("v4.db"))
    conn = sqlite3.connect(antigo)
    conn.executescript(
        """
        CREATE TABLE jogadores (id TEXT PRIMARY KEY, nome TEXT NOT NULL, nome_chave TEXT NOT NULL,
            genero TEXT NOT NULL, nota INTEGER NOT NULL DEFAULT 60, ativo INTEGER NOT NULL DEFAULT 1,
            criado_em TEXT NOT NULL, atualizado_em TEXT NOT NULL);
        CREATE TABLE sessoes (id TEXT PRIMARY KEY, aberta_em TEXT NOT NULL, encerrada_em TEXT);
        INSERT INTO jogadores VALUES ('a1','Ana Souza','ana souza','M',70,1,'x','x');
        INSERT INTO sessoes VALUES ('s1','x',NULL);
        PRAGMA user_version = 4;
        """
    )
    conn.commit()
    conn.close()
    settings.gerenciador_db_path = antigo
    init_gerenciador_sync()
    init_gerenciador_sync()
    estado = (await ac.get("/api/sessao")).json()
    assert estado["sessao"]["id"] == "s1" and estado["quadra"] is None
    with sqlite3.connect(antigo) as c:
        assert c.execute("SELECT COUNT(*) FROM partidas_rodada").fetchone()[0] == 0
