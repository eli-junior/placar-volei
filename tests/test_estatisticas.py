"""Resenha do Joguinho (CV8.DS9.US25): prêmios, galeria e tabela da sessão."""

# ruff: noqa: F811
import pytest
from httpx import ASGITransport, AsyncClient

from app.estatisticas import Jogador, Partida, calcular
from app.main import app
from tests.test_encerramento import Jogo, ac, base, placar  # noqa: F401

JOGADORES = {
    i: Jogador(i, nome, g)
    for i, nome, g in (
        ("a", "Ana", "M"),
        ("b", "Beto", "H"),
        ("c", "Caio", "H"),
        ("d", "Duda", "M"),
        ("e", "Edu", "H"),
        ("f", "Fabi", "M"),
    )
}


def partida(n, a, b, lado_a, lado_b, alvo=10, duracao=None):
    return Partida(n, 1, alvo, a, b, tuple(lado_a), tuple(lado_b), duracao)


def dia():
    # Ana e Beto ganham tudo juntos; Caio perde tudo, inclusive um pneu.
    return [
        partida(1, 10, 2, "ab", "cd", duracao=600),
        partida(2, 10, 8, "ab", "ce", duracao=900),
        partida(3, 12, 10, "ab", "cf", duracao=1500),
        partida(4, 10, 6, "de", "cf", duracao=700),
    ]


def premios(resultado):
    return {p["id"]: p for p in resultado["premios"]}


def test_rei_dupla_de_ouro_e_imparavel():
    r = premios(calcular(dia(), JOGADORES))
    assert r["rei"]["jogadores"] == ["a", "b"]
    assert r["rei"]["titulo"] == "Realeza do dia"  # empate: título coletivo
    assert r["rei"]["texto"] == "3 vitórias em 3 jogos"
    assert r["dupla_de_ouro"]["jogadores"] == ["a", "b"]
    assert r["dupla_de_ouro"]["texto"] == "3 vitórias juntos, sem perder"
    assert r["imparavel"]["texto"] == "3 vitórias seguidas"


def test_rei_unico_tem_titulo_pelo_genero():
    unico = [partida(1, 10, 5, "a", "b"), partida(2, 10, 5, "a", "c")]
    assert premios(calcular(unico, JOGADORES))["rei"]["titulo"] == "Rainha do dia"


def test_zoeira_pe_frio_ladeira_fregues_e_pneu():
    r = premios(calcular(dia(), JOGADORES))
    assert r["pe_frio"]["jogadores"] == ["c"]
    assert r["pe_frio"]["texto"] == "4 derrotas em 4 jogos"
    assert r["ladeira"]["texto"] == "4 derrotas seguidas"
    # Caio perdeu 3x para Ana e Beto; o nome desempata a dona da freguesia.
    assert r["fregues"]["jogadores"] == ["c"]
    assert r["fregues"]["texto"] == "perdeu 3x para Ana e não ganhou nenhuma"
    assert r["pneu"]["jogadores"] == ["c", "d"]
    assert r["pneu"]["texto"] == "tomou 10 x 2 e saiu de rosquinha"
    assert r["carrasco"]["jogadores"] == ["a", "b"]
    assert r["pneu"]["partida"]["placar_b"] == 2


def test_infarto_prefere_prorrogacao_e_maratona_e_a_mais_longa():
    r = premios(calcular(dia(), JOGADORES))
    assert r["infarto"]["partida"]["placar_a"] == 12
    assert "prorrogação" in r["infarto"]["texto"]
    assert r["maratona"]["texto"].startswith("25 min")


def test_sem_lavada_nao_tem_pneu_e_sem_aperto_nao_tem_infarto():
    jogos = [partida(1, 10, 6, "ab", "cd"), partida(2, 10, 7, "cd", "ab")]
    r = premios(calcular(jogos, JOGADORES))
    assert "pneu" not in r and "carrasco" not in r and "infarto" not in r


def test_muralha_e_peneira_pela_media_sofrida():
    r = premios(calcular(dia(), JOGADORES))
    assert r["muralha"]["jogadores"] == ["a", "b"]
    assert r["muralha"]["texto"] == "só 6.7 pontos sofridos por jogo"
    # Fabi sofreu 12 e 10 (11.0); Caio, 42 em 4 jogos (10.5)
    assert r["peneira"]["jogadores"] == ["f"]


def test_foguete_e_circuit_breaker_pela_nota():
    r = premios(calcular(dia(), JOGADORES, deltas={"a": 5, "c": -7, "d": 0}))
    assert r["foguete"]["jogadores"] == ["a"]
    assert r["circuit_breaker"]["jogadores"] == ["c"]
    assert "7 pontos" in r["circuit_breaker"]["texto"]


def test_madrugador_e_o_primeiro_presente():
    r = premios(calcular([], JOGADORES, presentes=["f", "a"]))
    assert r["madrugador"]["jogadores"] == ["f"]
    assert r["madrugador"]["titulo"] == "Madrugadora"


def test_galeria_titulo_principal_selos_e_padrao():
    resultado = calcular(
        dia(),
        JOGADORES,
        presentes=["a", "b", "c", "d", "e", "f"],
        campeoes=[{"rodada": 1, "jogadores": ["a", "b"]}],
    )
    galeria = {g["jogador"]: g for g in resultado["galeria"]}
    assert galeria["a"]["titulo"] == "Rainha do dia"
    assert "🏆" in galeria["a"]["selos"] and "🤝" in galeria["a"]["selos"]
    assert galeria["c"]["titulo"] == "Tomou pneu" and galeria["c"]["tom"] == "negativo"
    assert galeria["e"]["titulo"] == "Bom de areia" or galeria["e"]["selos"] == []
    # ordem: quem mais venceu primeiro
    assert [g["jogador"] for g in resultado["galeria"]][:2] == ["a", "b"]


def test_presente_que_nao_jogou_so_veio_pela_resenha():
    resultado = calcular(
        [partida(1, 10, 5, "ab", "cd")], JOGADORES, presentes=["a", "e"]
    )
    galeria = {g["jogador"]: g for g in resultado["galeria"]}
    assert galeria["e"]["titulo"] == "Só veio pela resenha"


def test_tabela_e_resumo():
    resultado = calcular(dia(), JOGADORES, rodadas=1)
    primeira = resultado["tabela"][0]
    assert primeira["jogador"] == "a"
    assert (primeira["jogos"], primeira["vitorias"], primeira["aproveitamento"]) == (
        3,
        3,
        100,
    )
    assert primeira["saldo"] == 32 - 20
    assert resultado["resumo"] == {
        "partidas": 4,
        "pontos": 68,
        "jogadores": 6,
        "rodadas": 1,
    }


def test_sessao_vazia_nao_quebra():
    resultado = calcular([], JOGADORES)
    assert resultado["premios"] == [] and resultado["tabela"] == []


# --- integração --------------------------------------------------------------


@pytest.mark.asyncio
async def test_sem_segredo_retorna_404():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        assert (await c.get("/api/sessao/estatisticas")).status_code == 404


@pytest.mark.asyncio
async def test_sem_sessao_responde_vazio(ac):
    r = await ac.get("/api/sessao/estatisticas")
    assert r.status_code == 200 and r.json() == {"sessao": None}


@pytest.mark.asyncio
async def test_resenha_da_sessao_com_partidas(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    await jogo.jogar("A")
    await jogo.jogar("A", perdedor=0)
    dados = (await ac.get("/api/sessao/estatisticas")).json()
    assert dados["resumo"]["partidas"] == 2
    assert dados["resumo"]["jogadores"] == 8
    vencedores = [t for t in dados["tabela"] if t["vitorias"] == 2]
    assert len(vencedores) == 2  # o rei da quadra venceu as duas
    ids = {p["id"] for p in dados["premios"]}
    assert {"rei", "carrasco", "pneu", "madrugador"} <= ids
    assert all(t["jogador"] in dados["jogadores"] for t in dados["tabela"])
    assert len(dados["galeria"]) == 8


@pytest.mark.asyncio
async def test_sessao_encerrada_continua_na_resenha(ac, placar):
    jogo = await Jogo(ac, placar).preparar(quantos=8)
    await jogo.jogar("A")
    await ac.post("/api/sessao/encerrar", json={"cancelar_rodada": True})
    dados = (await ac.get("/api/sessao/estatisticas")).json()
    assert dados["sessao"]["encerrada_em"] is not None
    assert dados["resumo"]["partidas"] == 1
