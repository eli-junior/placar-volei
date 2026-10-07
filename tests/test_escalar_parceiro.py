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
    def __init__(self, ac, placar):
        self.ac, self.placar, self.codigo, self.versao = ac, placar, None, None

    async def preparar(self, generos="HMHMH"):
        """5 jogadores chegando na ordem; o último a chegar fica incompleto."""
        await self.ac.post("/api/sessao")
        for i, g in enumerate(generos):
            j = await self.ac.post(
                "/api/jogadores",
                json={"nome": f"Jog{chr(65 + i)} Teste", "genero": g, "nota": 60 + i},
            )
            await self.ac.put(f"/api/sessao/presencas/{j.json()['id']}")
        await self.ac.post("/api/rodada/sorteio", json={"alvo": 10})
        await self.ac.post("/api/rodada/confirmar")
        r = await self.placar.post("/api/quadras", json={"apelido": "Operador"})
        self.codigo = r.json()["id"]
        await self.ac.put("/api/sessao/quadra", json={"codigo": self.codigo})
        return self

    async def estado(self):
        return (await self.ac.get("/api/sessao")).json()

    async def jogar(self, vence="A", perdedor=3):
        r = await self.ac.post("/api/rodada/chamar-partida")
        assert r.status_code == 201, r.text
        versao = str(
            snapshot_sync(settings.db_path, self.codigo)["quadra"]["controle_versao"]
        )
        for equipe, n in (("B" if vence == "A" else "A", perdedor), (vence, 10)):
            for _ in range(n):
                p = await self.placar.post(
                    f"/api/quadras/{self.codigo}/pontos",
                    json={"equipe": equipe},
                    headers={"x-control-version": versao},
                )
                assert p.status_code == 201
        r = await self.ac.post("/api/rodada/encerrar-partida")
        assert r.status_code == 200, r.text
        return r.json()

    async def ate_o_incompleto(self):
        """Joga a 1ª partida (time 1 vence o 2) e devolve o painel com o incompleto em quadra."""
        return (await self.jogar("A"))["conducao"]


def nomes(lista):
    return [j["nome"] for g in lista for j in g["jogadores"]]


@pytest.mark.asyncio
async def test_sem_segredo_retorna_404():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        assert (
            await c.post("/api/rodada/escalar-parceiro", json={"jogador_id": "x"})
        ).status_code == 404


@pytest.mark.asyncio
async def test_incompleto_em_quadra_mostra_a_lista_e_bloqueia_a_chamada(ac, placar):
    jogo = await Jogo(ac, placar).preparar("HMHMH")  # incompleto: JogE (homem)
    c = await jogo.ate_o_incompleto()
    assert [t["fila"] for t in c["em_quadra"]] == [1, 3] and c["em_quadra"][1][
        "incompleto"
    ]
    esc = c["escalacao"]
    assert esc["time"] == 3 and esc["origem"] == "impar" and esc["ninguem"] is False
    # time 2 foi eliminado: um homem e uma mulher; o incompleto é homem → só a mulher
    assert len(esc["grupos"]) == 1 and len(esc["grupos"][0]["jogadores"]) == 1
    assert (
        esc["grupos"][0]["jogadores"][0]["genero"] == "M" and esc["aviso_hh"] is False
    )
    assert c["pode_chamar"] is False and "Escolha o parceiro do Time 3" in c["motivo"]
    assert (await ac.post("/api/rodada/chamar-partida")).status_code == 409


@pytest.mark.asyncio
async def test_escolher_completa_o_time_e_o_escalado_sai_dos_eliminados(ac, placar):
    jogo = await Jogo(ac, placar).preparar("HMHMH")
    c = await jogo.ate_o_incompleto()
    mulher = c["escalacao"]["grupos"][0]["jogadores"][0]
    assert mulher["nome"] in nomes(
        [{"jogadores": [{"nome": e["nome"]} for e in c["eliminados"]]}]
    )
    r = await ac.post("/api/rodada/escalar-parceiro", json={"jogador_id": mulher["id"]})
    assert r.status_code == 200, r.text
    c = r.json()["conducao"]
    time3 = next(t for t in c["em_quadra"] if t["fila"] == 3)
    assert time3["incompleto"] is False and len(time3["jogadores"]) == 2
    assert [j["nome"] for j in time3["jogadores"] if j["escalado"]] == [mulher["nome"]]
    assert mulher["nome"] not in [
        e["nome"] for e in c["eliminados"]
    ]  # joga pelo 2º time
    assert c["escalacao"] is None and c["pode_chamar"] is True
    # o time 2 original continua com os dois jogadores gravados (histórico)
    with sqlite3.connect(settings.gerenciador_db_path) as conn:
        assert (
            conn.execute(
                "SELECT COUNT(*) FROM time_jogadores WHERE escalado = 1"
            ).fetchone()[0]
            == 1
        )
        assert (
            conn.execute(
                "SELECT COUNT(*) FROM time_jogadores WHERE jogador_id = ?",
                (mulher["id"],),
            ).fetchone()[0]
            == 2
        )


@pytest.mark.asyncio
async def test_saldo_do_escalado_soma_as_duas_participacoes(ac, placar):
    jogo = await Jogo(ac, placar).preparar("HMHMH")
    c = await jogo.ate_o_incompleto()  # t1 10×3 t2
    mulher = c["escalacao"]["grupos"][0]["jogadores"][0]
    await ac.post("/api/rodada/escalar-parceiro", json={"jogador_id": mulher["id"]})
    estado = await jogo.jogar("B", perdedor=5)  # t3 (B) vence t1 por 10×5
    saldos = {s["nome"]: s for s in estado["conducao"]["saldos"]}
    assert saldos[mulher["nome"]]["partidas"] == 2
    assert (
        saldos[mulher["nome"]]["saldo"] == -7 + 5
    )  # perdeu 3×10 pelo time 2 e ganhou 10×5 pelo time 3


@pytest.mark.asyncio
async def test_escalado_volta_aos_eliminados_quando_o_segundo_time_tambem_perde(
    ac, placar
):
    jogo = await Jogo(ac, placar).preparar("HMHMH")
    c = await jogo.ate_o_incompleto()
    mulher = c["escalacao"]["grupos"][0]["jogadores"][0]
    await ac.post("/api/rodada/escalar-parceiro", json={"jogador_id": mulher["id"]})
    estado = await jogo.jogar("A", perdedor=4)  # t1 vence o t3 do escalado → t1 rei
    c = estado["conducao"]
    assert mulher["nome"] in [e["nome"] for e in c["eliminados"]]
    assert [r["fila"] for r in c["reis"]] == [1]


@pytest.mark.asyncio
async def test_hh_com_alternativa_e_recusado_e_sem_alternativa_e_permitido(ac, placar):
    jogo = await Jogo(ac, placar).preparar("HMHMH")
    c = await jogo.ate_o_incompleto()
    eliminados = {e["nome"]: e for e in c["eliminados"]}
    homem = next(e for e in eliminados.values() if e["genero"] == "H")
    r = await ac.post("/api/rodada/escalar-parceiro", json={"jogador_id": homem["id"]})
    assert r.status_code == 409 and "H+H" in r.json()["detail"]


@pytest.mark.asyncio
async def test_so_homens_aceita_hh_com_aviso(ac, placar):
    jogo = await Jogo(ac, placar).preparar("HHHHH")
    c = await jogo.ate_o_incompleto()
    esc = c["escalacao"]
    assert esc["aviso_hh"] is True and len(esc["grupos"][0]["jogadores"]) == 2
    escolhido = esc["grupos"][0]["jogadores"][0]
    assert (
        await ac.post(
            "/api/rodada/escalar-parceiro", json={"jogador_id": escolhido["id"]}
        )
    ).status_code == 200


@pytest.mark.asyncio
async def test_incompleta_mulher_ve_homens_e_mulheres(ac, placar):
    jogo = await Jogo(ac, placar).preparar("HMHMM")
    c = await jogo.ate_o_incompleto()
    assert {j["genero"] for g in c["escalacao"]["grupos"] for j in g["jogadores"]} == {
        "H",
        "M",
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "corpo",
    [{}, {"jogador_id": None}, {"jogador_id": 7}, {"jogador_id": "inexistente"}],
)
async def test_escolha_fora_da_lista_e_recusada(ac, placar, corpo):
    jogo = await Jogo(ac, placar).preparar("HMHMH")
    await jogo.ate_o_incompleto()
    r = await ac.post("/api/rodada/escalar-parceiro", json=corpo)
    assert r.status_code == 409 and r.json()["erros"][0]["campo"] == "jogador"


@pytest.mark.asyncio
async def test_quem_esta_em_quadra_ou_e_rei_nao_e_elegivel(ac, placar):
    jogo = await Jogo(ac, placar).preparar("HMHMH")
    c = await jogo.ate_o_incompleto()
    em_quadra = c["em_quadra"][0]["jogadores"][0]  # time 1 segue em quadra
    r = await ac.post(
        "/api/rodada/escalar-parceiro", json={"jogador_id": em_quadra["id"]}
    )
    assert r.status_code == 409
    incompleto = c["em_quadra"][1]["jogadores"][0]
    assert (
        await ac.post(
            "/api/rodada/escalar-parceiro", json={"jogador_id": incompleto["id"]}
        )
    ).status_code == 409


@pytest.mark.asyncio
async def test_sem_incompleto_ou_com_partida_chamada_e_recusado(ac, placar):
    jogo = await Jogo(ac, placar).preparar("HMHMH")
    r = await ac.post("/api/rodada/escalar-parceiro", json={"jogador_id": "x"})
    assert (
        r.status_code == 409 and "incompleto" in r.json()["detail"]
    )  # ainda na 1ª partida
    c = await jogo.ate_o_incompleto()
    mulher = c["escalacao"]["grupos"][0]["jogadores"][0]
    await ac.post("/api/rodada/escalar-parceiro", json={"jogador_id": mulher["id"]})
    await ac.post("/api/rodada/chamar-partida")
    r = await ac.post("/api/rodada/escalar-parceiro", json={"jogador_id": mulher["id"]})
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_escolhas_concorrentes_so_uma_vale(ac, placar):
    jogo = await Jogo(ac, placar).preparar("HMMMM")
    c = await jogo.ate_o_incompleto()
    candidatos = c["escalacao"]["grupos"][0]["jogadores"]
    respostas = await asyncio.gather(
        *[
            ac.post("/api/rodada/escalar-parceiro", json={"jogador_id": x["id"]})
            for x in candidatos * 2
        ]
    )
    assert sorted(r.status_code for r in respostas).count(200) == 1
    with sqlite3.connect(settings.gerenciador_db_path) as conn:
        assert (
            conn.execute(
                "SELECT COUNT(*) FROM time_jogadores WHERE escalado = 1"
            ).fetchone()[0]
            == 1
        )


@pytest.mark.asyncio
async def test_atrasado_usa_sempre_a_lista_de_escalacao(ac, placar):
    jogo = await Jogo(ac, placar).preparar("HMHMH")
    c = await jogo.ate_o_incompleto()
    with sqlite3.connect(settings.gerenciador_db_path) as conn:
        conn.execute("UPDATE times SET origem = 'atrasado' WHERE incompleto = 1")
    esc = (await jogo.estado())["conducao"]["escalacao"]
    assert esc["origem"] == "atrasado" and "escalação" in esc["grupos"][0]["rotulo"]
    assert c["escalacao"]["grupos"][0]["rotulo"].startswith("Lista de escalação")


@pytest.mark.asyncio
async def test_persiste_apos_reset_e_migra_do_schema_5(ac, placar, tmp_path):
    jogo = await Jogo(ac, placar).preparar("HMHMH")
    c = await jogo.ate_o_incompleto()
    mulher = c["escalacao"]["grupos"][0]["jogadores"][0]
    await ac.post("/api/rodada/escalar-parceiro", json={"jogador_id": mulher["id"]})
    settings.reset_db_on_startup = True
    await init_db(settings.db_path)
    init_gerenciador_sync()
    init_gerenciador_sync()
    time3 = next(
        t for t in (await jogo.estado())["conducao"]["em_quadra"] if t["fila"] == 3
    )
    assert not time3["incompleto"] and any(j["escalado"] for j in time3["jogadores"])

    antigo = str(tmp_path / "v5.db")
    conn = sqlite3.connect(antigo)
    conn.executescript(
        """
        CREATE TABLE jogadores (id TEXT PRIMARY KEY, nome TEXT NOT NULL, nome_chave TEXT NOT NULL,
            genero TEXT NOT NULL, nota INTEGER NOT NULL DEFAULT 60, ativo INTEGER NOT NULL DEFAULT 1,
            criado_em TEXT NOT NULL, atualizado_em TEXT NOT NULL);
        CREATE TABLE sessoes (id TEXT PRIMARY KEY, aberta_em TEXT NOT NULL, encerrada_em TEXT, quadra_id TEXT);
        CREATE TABLE rodadas (id TEXT PRIMARY KEY, sessao_id TEXT NOT NULL, numero INTEGER NOT NULL,
            alvo INTEGER NOT NULL, estado TEXT NOT NULL, tentativa INTEGER NOT NULL DEFAULT 0,
            distintas INTEGER NOT NULL DEFAULT 1, criado_em TEXT NOT NULL, confirmado_em TEXT);
        CREATE TABLE times (id TEXT PRIMARY KEY, rodada_id TEXT NOT NULL, fila INTEGER NOT NULL,
            incompleto INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE time_jogadores (time_id TEXT NOT NULL, jogador_id TEXT NOT NULL,
            nota INTEGER NOT NULL, ordem_chegada INTEGER NOT NULL, PRIMARY KEY (time_id, jogador_id));
        INSERT INTO times VALUES ('t1', 'r1', 1, 1);
        PRAGMA user_version = 5;
        """
    )
    conn.commit()
    conn.close()
    settings.gerenciador_db_path = antigo
    init_gerenciador_sync()
    init_gerenciador_sync()
    with sqlite3.connect(antigo) as c2:
        assert c2.execute("SELECT origem FROM times").fetchone() == ("impar",)
        assert (
            c2.execute(
                "SELECT COUNT(*) FROM time_jogadores WHERE escalado = 1"
            ).fetchone()[0]
            == 0
        )
