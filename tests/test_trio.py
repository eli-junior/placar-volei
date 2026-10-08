# ruff: noqa: F811
"""Formato trio (CV8.DS6.US15, RN-16): sorteio, sobra e condução."""

import sqlite3

import pytest

from app.conducao import Candidato, lista_de_escalacao
from app.config import settings
from app.gerenciador_db import SCHEMA_VERSAO, init_gerenciador_sync
from app.sorteio import JogadoresInsuficientes, Participante, sortear
from tests.test_escalar_parceiro import Jogo, ac, base, placar  # noqa: F401


def grupo(generos: str, notas=None):
    notas = notas or [60] * len(generos)
    return [
        Participante(f"p{i}", g, n, i + 1)
        for i, (g, n) in enumerate(zip(generos, notas, strict=True))
    ]


def formato(s):
    return ["".join(p.genero for p in t.jogadores) for t in s.times]


@pytest.mark.parametrize("n", [0, 1, 5])
def test_menos_de_6_e_recusado(n):
    with pytest.raises(JogadoresInsuficientes) as e:
        sortear(grupo("HM" * 3)[:n], tamanho=3)
    assert e.value.minimo == 6 and e.value.faltam == 6 - n


@pytest.mark.parametrize("generos", ["HMHMHM", "HHHMMM", "HHHHMMMMM", "HMHMHMHM"])
def test_trios_sao_mistos_e_sobra_forma_time_incompleto(generos):
    s = sortear(grupo(generos), tamanho=3)
    completos = [t for t in s.times if not t.incompleto]
    sobra = [t for t in s.times if t.incompleto]
    assert all(len(t.jogadores) == 3 for t in completos)
    assert all(len({p.genero for p in t.jogadores}) == 2 for t in completos)
    assert len(sobra) == (1 if len(generos) % 3 else 0)
    if sobra:
        assert len(sobra[0].jogadores) == len(generos) % 3
        # a sobra são os últimos a chegar e vai por último na fila
        assert [p.ordem for p in sobra[0].jogadores] == list(
            range(len(generos) - len(generos) % 3 + 1, len(generos) + 1)
        )
        assert s.times[-1].incompleto


def test_sobra_de_dois_forma_time_de_dois_por_ultimo():
    s = sortear(grupo("HMHMHMHM"), tamanho=3)
    assert [len(t.jogadores) for t in s.times] == [3, 3, 2]
    assert s.times[-1].incompleto


def test_so_um_sexo_nao_tem_restricao():
    s = sortear(grupo("HHHHHHH"), tamanho=3)
    assert s.duplas_hh == 0 and [len(t.jogadores) for t in s.times] == [3, 3, 1]


def test_sem_mulher_suficiente_minimiza_trios_de_um_sexo():
    # 8 H e 1 M: 3 trios, só um pode ter a mulher
    s = sortear(grupo("HHHHHHHHM"), tamanho=3)
    assert s.duplas_hh == 2


def test_equilibra_pela_nota_e_e_deterministico():
    notas = [90, 80, 70, 60, 50, 40, 30, 20, 10]
    g = grupo("HMHMHMHMH", notas)
    a = sortear(g, tamanho=3)
    assert a == sortear(g, tamanho=3)
    assert a.amplitude <= 30
    outras = {
        tuple(tuple(p.id for p in t.jogadores) for t in sortear(g, i, tamanho=3).times)
        for i in range(a.distintas)
    }
    assert len(outras) == a.distintas


def test_time_na_fila_segue_a_chegada():
    s = sortear(grupo("HMHMHMHMH"), tamanho=3)
    primeiros = [min(p.ordem for p in t.jogadores) for t in s.times[: -0 or None]]
    assert primeiros == sorted(primeiros)


@pytest.mark.asyncio
async def test_api_sorteia_trios_e_recusa_poucos(ac):
    await ac.post("/api/sessao")
    for i, g in enumerate("HMHMH"):
        j = await ac.post(
            "/api/jogadores", json={"nome": f"Jog{chr(65 + i)} T", "genero": g}
        )
        await ac.put(f"/api/sessao/presencas/{j.json()['id']}")
    r = await ac.post("/api/rodada/sorteio", json={"alvo": 10, "formato": "trio"})
    assert r.status_code == 409 and "6" in r.text
    r = await ac.post("/api/rodada/sorteio", json={"alvo": 10, "formato": "quarteto"})
    assert r.status_code == 422


async def preparar_trio(ac, placar, generos):
    await ac.post("/api/sessao")
    for i, g in enumerate(generos):
        j = await ac.post(
            "/api/jogadores",
            json={"nome": f"Jog{chr(65 + i)} Teste", "genero": g, "nota": 60 + i},
        )
        await ac.put(f"/api/sessao/presencas/{j.json()['id']}")
    r = await ac.post("/api/rodada/sorteio", json={"alvo": 10, "formato": "trio"})
    assert r.status_code == 201, r.text
    assert r.json()["rodada"]["formato"] == "trio"
    await ac.post("/api/rodada/confirmar")
    jogo = Jogo(ac, placar)
    q = await placar.post("/api/quadras", json={"apelido": "Operador"})
    jogo.codigo = q.json()["id"]
    await ac.put("/api/sessao/quadra", json={"codigo": jogo.codigo})
    return jogo


@pytest.mark.asyncio
async def test_sobra_de_um_escolhe_dois_parceiros_na_sua_vez(ac, placar):
    jogo = await preparar_trio(ac, placar, "HMHMHMH")  # sobra: JogG (homem)
    c = (await jogo.jogar("A"))["conducao"]
    esc = c["escalacao"]
    assert esc["faltam"] == 2 and len(esc["grupos"][0]["jogadores"]) == 3
    assert c["pode_chamar"] is False
    # 1ª escolha: o time continua incompleto, agora pedindo 1
    r = await ac.post(
        "/api/rodada/escalar-parceiro",
        json={"jogador_id": esc["grupos"][0]["jogadores"][0]["id"]},
    )
    assert r.status_code == 200, r.text
    c = r.json()["conducao"]
    assert c["escalacao"]["faltam"] == 1 and c["pode_chamar"] is False
    escolha = c["escalacao"]["grupos"][0]["jogadores"][0]
    r = await ac.post(
        "/api/rodada/escalar-parceiro", json={"jogador_id": escolha["id"]}
    )
    c = r.json()["conducao"]
    time3 = next(t for t in c["em_quadra"] if t["fila"] == 3)
    assert not time3["incompleto"] and len(time3["jogadores"]) == 3
    assert {j["genero"] for j in time3["jogadores"]} == {"H", "M"}
    assert c["escalacao"] is None and c["pode_chamar"] is True


def _cand(i, g):
    return Candidato(f"c{i}", f"C{i}", g, 60, i)


def test_escalacao_do_trio_nao_fecha_um_sexo_so_havendo_alternativa():
    # H + H já escolhidos: o terceiro precisa ser mulher
    lista = lista_de_escalacao(
        genero_do_incompleto="H",
        origem="atrasado",
        eliminados=[_cand(1, "H"), _cand(2, "M")],
        livres=[],
        atuais=["H", "H"],
        tamanho=3,
    )
    assert [c.genero for g in lista["grupos"] for c in g["jogadores"]] == ["M"]
    assert [c.id for c in lista["recusados_hh"]] == ["c1"] and not lista["aviso_hh"]


def test_escalacao_do_trio_com_um_so_precisa_deixar_alternativa():
    # Incompleto H sozinho: pode pegar um H se ainda restar uma mulher
    lista = lista_de_escalacao(
        genero_do_incompleto="H",
        origem="atrasado",
        eliminados=[_cand(1, "H"), _cand(2, "H"), _cand(3, "M")],
        livres=[],
        atuais=["H"],
        tamanho=3,
    )
    assert len([c for g in lista["grupos"] for c in g["jogadores"]]) == 3
    # Sem nenhuma mulher elegível, aceita (com aviso): falta de alternativa
    lista = lista_de_escalacao(
        genero_do_incompleto="H",
        origem="atrasado",
        eliminados=[_cand(1, "H"), _cand(2, "H")],
        livres=[],
        atuais=["H"],
        tamanho=3,
    )
    assert lista["aviso_hh"] and len(lista["grupos"][0]["jogadores"]) == 2


def test_migra_do_schema_8():
    conn = sqlite3.connect(settings.gerenciador_db_path)
    conn.executescript(
        "ALTER TABLE rodadas DROP COLUMN formato; PRAGMA user_version = 8;"
    )
    conn.close()
    init_gerenciador_sync()
    conn = sqlite3.connect(settings.gerenciador_db_path)
    assert conn.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSAO
    assert "formato" in [r[1] for r in conn.execute("PRAGMA table_info(rodadas)")]
    conn.close()


def test_migra_do_schema_9_liberando_o_alvo():
    conn = sqlite3.connect(settings.gerenciador_db_path)
    sql = conn.execute(
        "SELECT sql FROM sqlite_master WHERE name = 'rodadas'"
    ).fetchone()[0]
    conn.execute("DROP TABLE rodadas")
    conn.execute(sql.replace("BETWEEN 6 AND 25", "IN (10, 12)"))
    conn.execute(
        "INSERT INTO rodadas (id, sessao_id, numero, alvo, estado, criado_em) "
        "VALUES ('r1', 's1', 1, 12, 'encerrada', 'x')"
    )
    conn.execute("PRAGMA user_version = 9")
    conn.commit()
    conn.close()
    init_gerenciador_sync()
    conn = sqlite3.connect(settings.gerenciador_db_path)
    assert conn.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSAO
    assert conn.execute("SELECT alvo, formato FROM rodadas").fetchall() == [
        (12, "dupla")
    ]
    conn.execute(
        "INSERT INTO rodadas (id, sessao_id, numero, alvo, estado, criado_em) "
        "VALUES ('r2', 's1', 2, 18, 'encerrada', 'x')"
    )
    indices = [r[1] for r in conn.execute("PRAGMA index_list(rodadas)")]
    assert "idx_rodada_ativa" in indices
    conn.close()
