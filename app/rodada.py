"""Rodada: sorteio da primeira rodada, proposta, confirmação (CV8.DS2.US3).

Só regras e dados; as rotas ficam em `app.sessao` (a rodada sempre sai junto do
estado da sessão). O algoritmo está em `app.sorteio`.

Ciclo: `proposta` (pode resortear, descartar ou confirmar) → `em_andamento`
(fila fixa; jogar as partidas é a DS3) → `cancelada`. Presença e inativação
ficam travadas enquanto houver rodada em proposta ou em andamento.
"""

import uuid

from app.gerenciador_db import agora, erro_de_campo, exigir_sessao_aberta
from app.sorteio import JogadoresInsuficientes, Participante, sortear

ALVOS = (10, 12)
ATIVAS = ("proposta", "em_andamento")


def rodada_ativa(conn, sessao_id: str):
    return conn.execute(
        "SELECT * FROM rodadas WHERE sessao_id = ? AND estado IN ('proposta', 'em_andamento')",
        (sessao_id,),
    ).fetchone()


def exigir_sem_rodada_ativa(conn, sessao_id: str) -> None:
    if rodada_ativa(conn, sessao_id):
        raise erro_de_campo(
            409,
            "rodada",
            "ativa: descarte a proposta ou cancele a rodada antes de mexer na presença",
            "rodada_ativa",
        )


def montar(conn, sessao_id: str) -> dict | None:
    """A rodada ativa da sessão no formato da API, ou None."""
    r = rodada_ativa(conn, sessao_id)
    if r is None:
        return None
    times = []
    for t in conn.execute(
        "SELECT * FROM times WHERE rodada_id = ? ORDER BY fila", (r["id"],)
    ):
        jogadores = [
            {
                "id": j["jogador_id"],
                "nome": j["nome"],
                "genero": j["genero"],
                "nota": j["nota"],
                "ordem_chegada": j["ordem_chegada"],
            }
            for j in conn.execute(
                "SELECT tj.jogador_id, tj.nota, tj.ordem_chegada, j.nome, j.genero "
                "FROM time_jogadores tj JOIN jogadores j ON j.id = tj.jogador_id "
                "WHERE tj.time_id = ? ORDER BY tj.ordem_chegada",
                (t["id"],),
            )
        ]
        times.append(
            {
                "fila": t["fila"],
                "incompleto": bool(t["incompleto"]),
                "soma": sum(j["nota"] for j in jogadores),
                "jogadores": jogadores,
            }
        )
    return {
        "id": r["id"],
        "numero": r["numero"],
        "alvo": r["alvo"],
        "estado": r["estado"],
        "tentativa": r["tentativa"],
        "distintas": r["distintas"],
        "times": times,
    }


def _alvo_valido(bruto) -> int:
    if isinstance(bruto, bool) or bruto not in ALVOS:
        raise erro_de_campo(422, "alvo", "deve ser 10 ou 12", "valor_invalido")
    return int(bruto)


def _participantes(conn, sessao_id: str) -> list[Participante]:
    return [
        Participante(r["id"], r["genero"], r["nota"], r["ordem"])
        for r in conn.execute(
            "SELECT j.id, j.genero, j.nota, p.ordem FROM presencas p "
            "JOIN jogadores j ON j.id = p.jogador_id WHERE p.sessao_id = ? "
            "ORDER BY p.ordem",
            (sessao_id,),
        )
    ]


def _sortear(participantes: list[Participante], tentativa: int):
    try:
        return sortear(participantes, tentativa)
    except JogadoresInsuficientes as e:
        raise erro_de_campo(
            409,
            "rodada",
            f"precisa de ao menos 4 presentes: {e}",
            "minimo",
        ) from None


def _gravar_times(conn, rodada_id: str, resultado, notas_por_id=None) -> None:
    for time in resultado.times:
        time_id = uuid.uuid4().hex
        conn.execute(
            "INSERT INTO times (id, rodada_id, fila, incompleto) VALUES (?, ?, ?, ?)",
            (time_id, rodada_id, time.fila, int(time.incompleto)),
        )
        for p in time.jogadores:
            conn.execute(
                "INSERT INTO time_jogadores (time_id, jogador_id, nota, ordem_chegada) "
                "VALUES (?, ?, ?, ?)",
                (time_id, p.id, p.nota, p.ordem),
            )


def _apagar_times(conn, rodada_id: str) -> None:
    conn.execute(
        "DELETE FROM time_jogadores WHERE time_id IN "
        "(SELECT id FROM times WHERE rodada_id = ?)",
        (rodada_id,),
    )
    conn.execute("DELETE FROM times WHERE rodada_id = ?", (rodada_id,))


def criar_proposta(conn, alvo) -> None:
    alvo = _alvo_valido(alvo)
    sessao = exigir_sessao_aberta(conn)
    if rodada_ativa(conn, sessao["id"]):
        raise erro_de_campo(409, "rodada", "já existe uma rodada ativa", "rodada_ativa")
    resultado = _sortear(_participantes(conn, sessao["id"]), 0)
    numero = conn.execute(
        "SELECT COALESCE(MAX(numero), 0) + 1 FROM rodadas WHERE sessao_id = ?",
        (sessao["id"],),
    ).fetchone()[0]
    rodada_id = uuid.uuid4().hex
    conn.execute(
        "INSERT INTO rodadas (id, sessao_id, numero, alvo, estado, tentativa, "
        "distintas, criado_em) VALUES (?, ?, ?, ?, 'proposta', 0, ?, ?)",
        (rodada_id, sessao["id"], numero, alvo, resultado.distintas, agora()),
    )
    _gravar_times(conn, rodada_id, resultado)


def _exigir_proposta(conn):
    sessao = exigir_sessao_aberta(conn)
    r = rodada_ativa(conn, sessao["id"])
    if r is None or r["estado"] != "proposta":
        raise erro_de_campo(
            409, "rodada", "não há proposta para esta ação", "sem_proposta"
        )
    return sessao, r


def resortear(conn, alvo=None) -> None:
    sessao, r = _exigir_proposta(conn)
    novo_alvo = _alvo_valido(alvo) if alvo is not None else r["alvo"]
    tentativa = r["tentativa"] + 1
    resultado = _sortear(_participantes(conn, sessao["id"]), tentativa)
    _apagar_times(conn, r["id"])
    _gravar_times(conn, r["id"], resultado)
    conn.execute(
        "UPDATE rodadas SET alvo = ?, tentativa = ?, distintas = ? WHERE id = ?",
        (novo_alvo, tentativa, resultado.distintas, r["id"]),
    )


def confirmar(conn) -> None:
    _sessao, r = _exigir_proposta(conn)
    conn.execute(
        "UPDATE rodadas SET estado = 'em_andamento', confirmado_em = ? WHERE id = ?",
        (agora(), r["id"]),
    )


def descartar(conn) -> None:
    _sessao, r = _exigir_proposta(conn)
    _apagar_times(conn, r["id"])
    conn.execute("DELETE FROM rodadas WHERE id = ?", (r["id"],))


def cancelar(conn) -> None:
    sessao = exigir_sessao_aberta(conn)
    r = rodada_ativa(conn, sessao["id"])
    if r is None or r["estado"] != "em_andamento":
        raise erro_de_campo(409, "rodada", "não há rodada em andamento", "sem_rodada")
    conn.execute("UPDATE rodadas SET estado = 'cancelada' WHERE id = ?", (r["id"],))
