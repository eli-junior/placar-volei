"""Retirar jogador no meio da rodada (CV8.DS7.US19, decisão C).

Quem sai deixa a **vaga vazia**: o time segue com a vitória e a posição e só
precisa de um substituto quando chega a vez de entrar em quadra (lista de
escalação, RN-07). Time que fica sem nenhum jogador deixa de existir; isso é
gravado como ajuste da fila (`ajustes_fila`, TS3) para os resultados já
registrados continuarem batendo. Quem saiu fica ausente (volta como atrasado,
US9). Em jogo não sai; sem elegível na vez de entrar, o time pode ser pulado.
"""

from app.conducao import Ajuste
from app.gerenciador_db import agora, erro_de_campo, exigir_sessao_aberta
from app.jogadores import recompactar_presencas
from app.rodada import _contexto, _escalacao, montar


def _rodada_em_andamento(conn):
    sessao = exigir_sessao_aberta(conn)
    rodada = montar(conn, sessao["id"])
    if rodada is None or rodada["estado"] != "em_andamento":
        raise erro_de_campo(409, "rodada", "não está em andamento", "sem_rodada")
    return sessao, rodada


def _gravar_ajuste(conn, rodada_id: str, apos: int, tipo: str, time_id: str) -> None:
    conn.execute(
        "INSERT INTO ajustes_fila (rodada_id, apos_partidas, tipo, time_id, criado_em) "
        "VALUES (?, ?, ?, ?, ?)",
        (rodada_id, apos, tipo, time_id, agora()),
    )


def retirar(conn, jogador_id) -> None:
    sessao, rodada = _rodada_em_andamento(conn)
    if not isinstance(jogador_id, str):
        raise erro_de_campo(422, "jogador_id", "informe o jogador", "valor_invalido")
    times = [
        t for t in rodada["times"] if any(j["id"] == jogador_id for j in t["jogadores"])
    ]
    if not times:
        raise erro_de_campo(409, "jogador", "não está na rodada", "fora_da_rodada")
    chamada = conn.execute(
        "SELECT time_a_id, time_b_id FROM partidas_rodada "
        "WHERE rodada_id = ? AND estado = 'chamada'",
        (rodada["id"],),
    ).fetchone()
    if chamada and any(
        t["id"] in (chamada["time_a_id"], chamada["time_b_id"]) for t in times
    ):
        raise erro_de_campo(
            409,
            "jogador",
            "está em jogo na partida chamada: encerre-a ou anule-a antes de retirar",
            "em_jogo",
        )
    _, linhas, situacao = _contexto(conn, rodada)
    ativos = {*situacao.em_quadra, *situacao.fila, *situacao.reis}
    for t in times:
        conn.execute(
            "DELETE FROM time_jogadores WHERE time_id = ? AND jogador_id = ?",
            (t["id"], jogador_id),
        )
        restam = len(t["jogadores"]) - 1
        if restam == 0:
            if t["id"] in ativos:
                _gravar_ajuste(conn, rodada["id"], len(linhas), "remover", t["id"])
        elif restam < rodada["tamanho"]:
            conn.execute("UPDATE times SET incompleto = 1 WHERE id = ?", (t["id"],))
    conn.execute(
        "DELETE FROM presencas WHERE sessao_id = ? AND jogador_id = ?",
        (sessao["id"], jogador_id),
    )
    recompactar_presencas(conn, sessao["id"])


def pular_time(conn) -> None:
    """Sem elegível para a vaga do time que está na vez, manda o time para o
    fim da fila (ou dos rivais, no mata-mata) e a próxima partida usa o seguinte."""
    _, rodada = _rodada_em_andamento(conn)
    if conn.execute(
        "SELECT 1 FROM partidas_rodada WHERE rodada_id = ? AND estado = 'chamada'",
        (rodada["id"],),
    ).fetchone():
        raise erro_de_campo(
            409,
            "rodada",
            "tem uma partida chamada: encerre-a ou anule-a antes de pular um time",
            "partida_chamada",
        )
    por_id, linhas, situacao = _contexto(conn, rodada)
    incompleto = next(
        (por_id[t] for t in situacao.em_quadra if por_id[t]["incompleto"]), None
    )
    if situacao.fase not in ("fila", "mata_mata") or incompleto is None:
        raise erro_de_campo(
            409, "rodada", "não há time incompleto esperando parceiro", "sem_incompleto"
        )
    if _escalacao(rodada, por_id, linhas, situacao, incompleto)["grupos"]:
        raise erro_de_campo(
            409,
            "rodada",
            "há quem possa completar o time: escolha o parceiro em vez de pular",
            "ha_elegiveis",
        )
    novo = Ajuste(len(linhas), "pular", incompleto["id"])
    if _contexto(conn, rodada, (novo,))[2].em_quadra == situacao.em_quadra:
        raise erro_de_campo(
            409,
            "rodada",
            "pular não mudaria a próxima partida: não há outro time para entrar",
            "sem_outro_time",
        )
    _gravar_ajuste(conn, rodada["id"], novo.apos, "pular", incompleto["id"])
