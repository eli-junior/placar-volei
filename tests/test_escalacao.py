from app.conducao import Candidato, lista_de_escalacao, saldos


def c(id, genero, chegada, nome=None, nota=60):
    return Candidato(id, nome or id, genero, nota, chegada)


def ids(lista):
    return [x.id for g in lista["grupos"] for x in g["jogadores"]]


def test_incompleto_homem_so_recebe_mulheres_havendo_alternativa():
    elim = [c("h1", "H", 1), c("m1", "M", 3), c("m2", "M", 2)]
    lista = lista_de_escalacao(
        genero_do_incompleto="H", origem="impar", eliminados=elim, livres=[]
    )
    assert ids(lista) == ["m2", "m1"]  # por ordem de chegada
    assert lista["aviso_hh"] is False
    assert [x.id for x in lista["recusados_hh"]] == ["h1"]


def test_incompleto_homem_sem_mulher_elegivel_aceita_homem_com_aviso():
    elim = [c("h2", "H", 2), c("h1", "H", 1)]
    lista = lista_de_escalacao(
        genero_do_incompleto="H", origem="impar", eliminados=elim, livres=[]
    )
    assert ids(lista) == ["h1", "h2"] and lista["aviso_hh"] is True
    assert lista["recusados_hh"] == []


def test_incompleto_mulher_aceita_qualquer_genero():
    elim = [c("h1", "H", 2), c("m1", "M", 1)]
    lista = lista_de_escalacao(
        genero_do_incompleto="M", origem="impar", eliminados=elim, livres=[]
    )
    assert ids(lista) == ["m1", "h1"] and lista["aviso_hh"] is False


def test_impar_prefere_quem_ainda_nao_jogou_e_cai_na_escalacao_se_vazio():
    elim = [c("e1", "M", 1)]
    livre = [c("l1", "M", 5)]
    com = lista_de_escalacao(
        genero_do_incompleto="M", origem="impar", eliminados=elim, livres=livre
    )
    assert ids(com) == ["l1"] and com["grupos"][0]["rotulo"] == "Ainda não jogaram"
    sem = lista_de_escalacao(
        genero_do_incompleto="M", origem="impar", eliminados=elim, livres=[]
    )
    assert ids(sem) == ["e1"] and "escalação" in sem["grupos"][0]["rotulo"]


def test_atrasado_usa_sempre_a_lista_de_escalacao():
    elim = [c("e1", "M", 1)]
    livre = [c("l1", "M", 5)]
    lista = lista_de_escalacao(
        genero_do_incompleto="M", origem="atrasado", eliminados=elim, livres=livre
    )
    assert ids(lista) == ["e1"]


def test_ninguem_elegivel():
    lista = lista_de_escalacao(
        genero_do_incompleto="M", origem="impar", eliminados=[], livres=[]
    )
    assert lista["grupos"] == [] and lista["aviso_hh"] is False


def test_saldo_soma_as_duas_participacoes_do_escalado():
    times = {
        "t1": [{"id": "a", "nome": "Ana"}, {"id": "b", "nome": "Bia"}],
        "t2": [{"id": "c", "nome": "Caio"}, {"id": "d", "nome": "Davi"}],
        "t3": [
            {"id": "e", "nome": "Eva"},
            {"id": "c", "nome": "Caio"},
        ],  # Caio escalado
    }
    partidas = [
        {
            "time_a_id": "t1",
            "time_b_id": "t2",
            "placar_a": 10,
            "placar_b": 4,
        },  # t2 perde
        {
            "time_a_id": "t1",
            "time_b_id": "t3",
            "placar_a": 8,
            "placar_b": 10,
        },  # t3 vence
    ]
    por_id = {s["id"]: s for s in saldos(times, partidas)}
    assert por_id["a"] == {"id": "a", "nome": "Ana", "partidas": 2, "saldo": 6 - 2}
    assert (
        por_id["c"]["partidas"] == 2 and por_id["c"]["saldo"] == -6 + 2
    )  # perdeu uma e ganhou outra
    assert por_id["e"]["saldo"] == 2 and por_id["d"]["saldo"] == -6
    assert saldos(times, []) == []
