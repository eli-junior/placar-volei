import asyncio
import sqlite3
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.comandos import snapshot_sync
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


@pytest.fixture
async def placar():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


class Jogo:
    """Uma rodada em andamento com a quadra do placar vinculada."""

    def __init__(self, ac, placar):
        self.ac, self.placar = ac, placar
        self.codigo = None
        self.versao = None

    async def preparar(self, quantos=8, alvo=10):
        await self.ac.post("/api/sessao")
        for i in range(quantos):
            genero = "H" if i % 2 else "M"
            j = await self.ac.post(
                "/api/jogadores",
                json={
                    "nome": f"Jog{chr(65 + i)} Teste",
                    "genero": genero,
                    "nota": 60 + i % 3,
                },
            )
            await self.ac.put(f"/api/sessao/presencas/{j.json()['id']}")
        await self.ac.post("/api/rodada/sorteio", json={"alvo": alvo})
        await self.ac.post("/api/rodada/confirmar")
        r = await self.placar.post("/api/quadras", json={"apelido": "Operador"})
        self.codigo = r.json()["id"]
        await self.ac.put("/api/sessao/quadra", json={"codigo": self.codigo})
        return self

    async def estado(self):
        return (await self.ac.get("/api/sessao")).json()

    async def chamar(self):
        r = await self.ac.post("/api/rodada/chamar-partida")
        assert r.status_code == 201, r.text
        self.versao = str(
            snapshot_sync(settings.db_path, self.codigo)["quadra"]["controle_versao"]
        )
        return r.json()

    async def pontos(self, equipe, quantos):
        for _ in range(quantos):
            r = await self.placar.post(
                f"/api/quadras/{self.codigo}/pontos",
                json={"equipe": equipe},
                headers={"x-control-version": self.versao},
            )
            assert r.status_code == 201, r.text

    async def encerrar(self):
        return await self.ac.post("/api/rodada/encerrar-partida")

    async def jogar(self, vence="A", alvo=10, perdedor=3):
        """Chama, joga até o fim no placar (vence 'A' ou 'B') e encerra."""
        await self.chamar()
        await self.pontos("B" if vence == "A" else "A", perdedor)
        await self.pontos(vence, alvo)
        r = await self.encerrar()
        assert r.status_code == 200, r.text
        return r.json()


def filas(times):
    return [t["fila"] for t in times]


@pytest.mark.asyncio
async def test_sem_segredo_retorna_404():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        assert (await c.post("/api/rodada/encerrar-partida")).status_code == 404


@pytest.mark.asyncio
async def test_sem_partida_chamada_e_recusado(ac, placar):
    jogo = await Jogo(ac, placar).preparar()
    r = await jogo.encerrar()
    assert r.status_code == 409 and "não tem partida chamada" in r.json()["detail"]
    await ac.post("/api/rodada/cancelar")
    r = await jogo.encerrar()  # sem rodada em andamento
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_partida_em_jogo_e_recusada_com_o_placar_parcial(ac, placar):
    jogo = await Jogo(ac, placar).preparar()
    await jogo.chamar()
    await jogo.pontos("A", 7)
    await jogo.pontos("B", 5)
    r = await jogo.encerrar()
    assert r.status_code == 409 and "7 × 5" in r.json()["detail"]
    c = (await jogo.estado())["conducao"]
    assert (
        c["pode_encerrar"] is False
        and "Em jogo no placar (7 × 5)" in c["motivo_encerrar"]
    )
    assert c["partida"]["placar"] == {
        "a": 7,
        "b": 5,
        "encerrada": False,
        "vencedor": None,
        "mesma_partida": True,
    }
    assert c["historico"] == []
    with sqlite3.connect(settings.gerenciador_db_path) as conn:
        assert conn.execute("SELECT estado FROM partidas_rodada").fetchall() == [
            ("chamada",)
        ]


@pytest.mark.asyncio
async def test_encerrar_grava_placar_e_vencedor_dos_dois_lados(ac, placar):
    jogo = await Jogo(ac, placar).preparar(alvo=10)
    estado = await jogo.jogar("A", perdedor=3)
    c = estado["conducao"]
    assert c["historico"] == [
        {
            "ordem": 1,
            "time_a": 1,
            "time_b": 2,
            "fase": "fila",
            "placar_a": 10,
            "placar_b": 3,
            "vencedor": 1,
            "encerrada_em": c["historico"][0]["encerrada_em"],
        }
    ]
    # time 1 fica (1 vitória) e enfrenta o próximo da fila; time 2 foi eliminado
    assert filas(c["em_quadra"]) == [1, 3]
    assert {e["time"] for e in c["eliminados"]} == {2}
    assert c["partida"] is None and c["partidas_encerradas"] == 1
    assert next(t for t in c["em_quadra"] if t["fila"] == 1)["vitorias"] == 1
    # o placar da quadra segue mostrando o resultado final até a próxima chamada
    assert (
        snapshot_sync(settings.db_path, jogo.codigo)["estado_partida"]["encerrada"]
        is True
    )

    # segunda partida: agora o time B (o 3) vence → time 1 eliminado
    estado = await jogo.jogar("B", perdedor=8)  # 8 × 10 também fecha (vantagem de 2)
    c = estado["conducao"]
    assert c["historico"][1]["placar_a"] == 8 and c["historico"][1]["placar_b"] == 10
    assert c["historico"][1]["vencedor"] == 3
    assert filas(c["em_quadra"]) == [3, 4]
    assert {e["time"] for e in c["eliminados"]} == {1, 2}


@pytest.mark.asyncio
async def test_duas_vitorias_seguidas_viram_rei_e_entram_os_dois_proximos(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=10, alvo=10)  # 5 times
    await jogo.jogar("A")  # t1 vence t2
    estado = await jogo.jogar("A")  # t1 vence t3 → rei
    c = estado["conducao"]
    assert [r["fila"] for r in c["reis"]] == [1] and c["reis"][0]["ordem"] == 1
    assert filas(c["em_quadra"]) == [4, 5] and c["fila"] == []
    assert {e["time"] for e in c["eliminados"]} == {2, 3}
    assert c["fase"] == "fila" and c["pode_chamar"] is True


@pytest.mark.asyncio
async def test_fim_da_fila_bloqueia_novas_chamadas(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8, alvo=10)  # 4 times
    await jogo.jogar("A")  # t1 vence t2; t3 entra
    estado = await jogo.jogar("A")  # t1 vence t3 → rei; t4 fica sozinho na quadra
    c = estado["conducao"]
    assert c["fase"] == "fim_da_fila"
    assert filas(c["em_quadra"]) == [4] and c["finalista"]["fila"] == 4
    assert c["pode_chamar"] is False and "fase de fila terminou" in c["motivo"]
    assert (await ac.post("/api/rodada/chamar-partida")).status_code == 409


@pytest.mark.asyncio
async def test_partida_trocada_no_placar_nao_pode_ser_lida(ac, placar):
    jogo = await Jogo(ac, placar).preparar()
    await jogo.chamar()
    await jogo.pontos("A", 10)
    # alguém usa "nova partida" no placar: a partida da chamada saiu de cena
    r = await placar.post(f"/api/quadras/{jogo.codigo}/reiniciar", json={})
    assert r.status_code == 200, r.text
    r = await jogo.encerrar()
    assert r.status_code == 409 and "trocada" in r.json()["detail"]
    c = (await jogo.estado())["conducao"]
    assert c["pode_encerrar"] is False and "outra partida" in c["motivo_encerrar"]


@pytest.mark.asyncio
async def test_quadra_indisponivel_mantem_a_partida_chamada(ac, placar):
    jogo = await Jogo(ac, placar).preparar()
    await jogo.chamar()
    await jogo.pontos("A", 10)
    with sqlite3.connect(settings.db_path) as conn:
        conn.execute("DELETE FROM quadras WHERE id = ?", (jogo.codigo,))
    r = await jogo.encerrar()
    assert r.status_code == 409 and "continua aguardando" in r.json()["detail"]
    c = (await jogo.estado())["conducao"]
    assert c["partida"] is not None and c["pode_encerrar"] is False
    # vincula outra quadra: a chamada em aberto não se perde, mas não há como ler o resultado
    r = await placar.post("/api/quadras", json={"apelido": "Operador"})
    assert (
        await ac.put("/api/sessao/quadra", json={"codigo": r.json()["id"]})
    ).status_code == 409


@pytest.mark.asyncio
async def test_encerrar_e_idempotente_e_concorrente(ac, placar):
    jogo = await Jogo(ac, placar).preparar()
    await jogo.chamar()
    await jogo.pontos("A", 10)
    respostas = await asyncio.gather(*[jogo.encerrar() for _ in range(4)])
    assert sorted(r.status_code for r in respostas) == [200] + [409] * 3
    with sqlite3.connect(settings.gerenciador_db_path) as conn:
        assert (
            conn.execute(
                "SELECT COUNT(*) FROM partidas_rodada WHERE estado='encerrada'"
            ).fetchone()[0]
            == 1
        )


@pytest.mark.asyncio
async def test_depois_de_encerrar_a_proxima_chamada_zera_o_placar(ac, placar):
    jogo = await Jogo(ac, placar).preparar()
    await jogo.jogar("A")
    r = await ac.post("/api/rodada/chamar-partida")
    assert r.status_code == 201
    e = snapshot_sync(settings.db_path, jogo.codigo)["estado_partida"]
    assert (e["pontos_a"], e["pontos_b"], e["encerrada"]) == (0, 0, False)
    c = r.json()["conducao"]
    assert (
        c["partida"]["ordem"] == 2
        and c["partida"]["time_a"] == 1
        and c["partida"]["time_b"] == 3
    )


@pytest.mark.asyncio
async def test_cancelar_com_partidas_mantem_o_historico(ac, placar):
    jogo = await Jogo(ac, placar).preparar()
    await jogo.jogar("A")
    r = await ac.post("/api/rodada/cancelar")
    assert r.status_code == 200 and r.json()["rodada"] is None
    with sqlite3.connect(settings.gerenciador_db_path) as conn:
        assert (
            conn.execute(
                "SELECT COUNT(*) FROM partidas_rodada WHERE estado='encerrada'"
            ).fetchone()[0]
            == 1
        )
        assert conn.execute("SELECT estado FROM rodadas").fetchall() == [("cancelada",)]


@pytest.mark.asyncio
async def test_painel_conta_as_partidas_registradas(ac, placar):
    jogo = await Jogo(ac, placar).preparar()
    assert (await jogo.estado())["conducao"]["partidas_encerradas"] == 0
    estado = await jogo.jogar("A")
    assert estado["conducao"]["partidas_encerradas"] == 1


# Anular a partida chamada (fix: joguinho sempre encerrável, QA 2026-10-08).


async def anular(ac):
    return await ac.post("/api/rodada/anular-partida")


@pytest.mark.asyncio
async def test_anular_sem_segredo_retorna_404():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        assert (await c.post("/api/rodada/anular-partida")).status_code == 404


@pytest.mark.asyncio
async def test_anular_sem_partida_chamada_e_recusado(ac, placar):
    await Jogo(ac, placar).preparar()
    r = await anular(ac)
    assert r.status_code == 409 and "não tem partida chamada" in r.json()["detail"]


@pytest.mark.asyncio
async def test_quadra_sumiu_anular_trocar_de_quadra_e_chamar_de_novo(ac, placar):
    jogo = await Jogo(ac, placar).preparar()
    await jogo.chamar()
    await jogo.pontos("A", 4)
    with sqlite3.connect(settings.db_path) as conn:
        conn.execute("DELETE FROM quadras WHERE id = ?", (jogo.codigo,))
    c = (await jogo.estado())["conducao"]
    assert c["pode_encerrar"] is False and c["pode_anular"] is True
    assert "anule a partida" in c["motivo_encerrar"]

    r = await anular(ac)
    assert r.status_code == 200, r.text
    estado = r.json()
    assert estado["rodada"]["estado"] == "em_andamento"
    c = estado["conducao"]
    assert c["partida"] is None and c["pode_anular"] is False
    assert filas(c["em_quadra"]) == [1, 2] and c["historico"] == []

    nova = await placar.post("/api/quadras", json={"apelido": "Operador"})
    jogo.codigo = nova.json()["id"]
    r = await ac.put("/api/sessao/quadra", json={"codigo": jogo.codigo})
    assert r.status_code == 200, r.text
    estado = await jogo.jogar("B")
    assert estado["conducao"]["historico"][0]["vencedor"] == 2


@pytest.mark.asyncio
async def test_anular_jogo_parado_no_meio_nao_conta_e_nao_mexe_no_placar(ac, placar):
    jogo = await Jogo(ac, placar).preparar()
    await jogo.jogar("A")
    await jogo.chamar()
    await jogo.pontos("A", 3)
    r = await anular(ac)
    assert r.status_code == 200, r.text
    c = r.json()["conducao"]
    assert c["partida"] is None and c["partidas_encerradas"] == 1
    assert filas(c["em_quadra"]) == [1, 3]
    e = snapshot_sync(settings.db_path, jogo.codigo)["estado_partida"]
    assert (e["pontos_a"], e["pontos_b"]) == (3, 0)
    with sqlite3.connect(settings.gerenciador_db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM partidas_rodada").fetchone()[0] == 1


@pytest.mark.asyncio
async def test_cancelar_com_partida_chamada_libera_o_vinculo(ac, placar):
    jogo = await Jogo(ac, placar).preparar()
    await jogo.chamar()
    with sqlite3.connect(settings.db_path) as conn:
        conn.execute("DELETE FROM quadras WHERE id = ?", (jogo.codigo,))
    assert (await ac.post("/api/rodada/cancelar")).status_code == 200
    with sqlite3.connect(settings.gerenciador_db_path) as conn:
        assert (
            conn.execute(
                "SELECT COUNT(*) FROM partidas_rodada WHERE estado = 'chamada'"
            ).fetchone()[0]
            == 0
        )
    nova = await placar.post("/api/quadras", json={"apelido": "Operador"})
    r = await ac.put("/api/sessao/quadra", json={"codigo": nova.json()["id"]})
    assert r.status_code == 200, r.text
    assert (await ac.delete("/api/sessao/quadra")).status_code == 200
    assert (await ac.post("/api/sessao/encerrar")).status_code == 200


@pytest.mark.asyncio
async def test_chamada_orfa_de_rodada_cancelada_nao_trava_o_vinculo(ac, placar):
    """Bancos de antes da correção: a rodada foi cancelada com a chamada aberta."""
    jogo = await Jogo(ac, placar).preparar()
    await jogo.chamar()
    with sqlite3.connect(settings.gerenciador_db_path) as conn:
        conn.execute("UPDATE rodadas SET estado = 'cancelada'")
    r = await ac.delete("/api/sessao/quadra")
    assert r.status_code == 200, r.text
