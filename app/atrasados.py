"""Atrasado no meio da rodada (CV8.DS3.US9, RN-06).

O jogador que chega com a rodada em andamento vira, sozinho, um time
incompleto no fim da fila (`origem = 'atrasado'`). Revisão da RN-06 (Navigator,
2026-10-14): quando os times sorteados estão acabando, os atrasados que esperam
formam times entre si, com o equilíbrio do sorteio (`agrupar`). Quem sobra
(o último a chegar) escolhe o parceiro na sua vez, pela lista de escalação.
Depois do início do mata-mata ninguém entra; o jogador continua ausente e
entra no próximo sorteio.
"""

import uuid

from app.gerenciador_db import agora, erro_de_campo, exigir_sessao_aberta, sessao_aberta
from app.jogadores import obter_jogador
from app.reequilibrio import duplas_anteriores
from app.rodada import _contexto, montar
from app.sorteio import MINIMO_POR_TAMANHO, Participante, sortear

# Times sorteados à frente dos atrasados quando eles se agrupam. Um, e não
# zero: o time que vira rei sai da quadra e puxa dois da fila de uma vez.
FOLGA = 1


def registrar_atrasado(conn, jogador_id) -> None:
    sessao = exigir_sessao_aberta(conn)
    rodada = conn.execute(
        "SELECT * FROM rodadas WHERE sessao_id = ? AND estado = 'em_andamento'",
        (sessao["id"],),
    ).fetchone()
    if rodada is None:
        raise erro_de_campo(409, "rodada", "não há rodada em andamento", "sem_rodada")
    if rodada["mata_mata_em"]:
        raise erro_de_campo(
            409,
            "rodada",
            "o mata-mata já começou: o atrasado entra na próxima rodada",
            "mata_mata_iniciado",
        )
    if rodada["triangular"]:
        raise erro_de_campo(
            409,
            "rodada",
            "a rodada é triangular, de 3 times: o atrasado entra na próxima rodada",
            "rodada_triangular",
        )
    if not isinstance(jogador_id, str):
        raise erro_de_campo(422, "jogador_id", "informe o jogador", "valor_invalido")
    jogador = obter_jogador(conn, jogador_id)
    if not jogador["ativo"]:
        raise erro_de_campo(409, "jogador", "está inativo", "inativo")
    if conn.execute(
        "SELECT 1 FROM presencas WHERE sessao_id = ? AND jogador_id = ?",
        (sessao["id"], jogador_id),
    ).fetchone():
        raise erro_de_campo(409, "jogador", "já está presente", "ja_presente")
    ordem = conn.execute(
        "SELECT COALESCE(MAX(ordem), 0) + 1 FROM presencas WHERE sessao_id = ?",
        (sessao["id"],),
    ).fetchone()[0]
    conn.execute(
        "INSERT INTO presencas (sessao_id, jogador_id, ordem, marcado_em) "
        "VALUES (?, ?, ?, ?)",
        (sessao["id"], jogador_id, ordem, agora()),
    )
    fila = conn.execute(
        "SELECT COALESCE(MAX(fila), 0) + 1 FROM times WHERE rodada_id = ?",
        (rodada["id"],),
    ).fetchone()[0]
    time_id = uuid.uuid4().hex
    conn.execute(
        "INSERT INTO times (id, rodada_id, fila, incompleto, origem) "
        "VALUES (?, ?, ?, 1, 'atrasado')",
        (time_id, rodada["id"], fila),
    )
    conn.execute(
        "INSERT INTO time_jogadores (time_id, jogador_id, nota, ordem_chegada) "
        "VALUES (?, ?, ?, ?)",
        (time_id, jogador_id, jogador["nota"], ordem),
    )


def agrupar(conn) -> None:
    """Forma os times dos atrasados que esperam, se a vez deles está chegando.

    Roda depois de toda mudança da rodada. Só mexe em times de atrasados
    incompletos que estão na fila e nunca jogaram: os resultados gravados não
    mudam. Os times reaproveitam as posições na fila; os que sobram vazios
    deixam de existir, como na substituição.
    """
    sessao = sessao_aberta(conn)
    rodada = montar(conn, sessao["id"]) if sessao else None
    if (
        rodada is None
        or rodada["estado"] != "em_andamento"
        or rodada["mata_mata_iniciado"]
        or rodada["triangular"]
    ):
        return
    por_id, linhas, situacao = _contexto(conn, rodada)
    jogaram = {t for r in linhas for t in (r["time_a_id"], r["time_b_id"])}
    fila = list(situacao.fila)
    esperando = [
        t
        for t in fila
        if por_id[t]["origem"] == "atrasado"
        and por_id[t]["incompleto"]
        and t not in jogaram
    ]
    if len(esperando) < 2 or fila.index(esperando[0]) > FOLGA:
        return
    tamanho = rodada["tamanho"]
    jogadores = sorted(
        (
            Participante(j["id"], j["genero"], j["nota"], j["ordem_chegada"])
            for t in esperando
            for j in por_id[t]["jogadores"]
        ),
        key=lambda p: p.ordem,
    )
    grupos = _grupos(jogadores, tamanho, duplas_anteriores(conn, sessao["id"], tamanho))
    for t in esperando:
        conn.execute("DELETE FROM time_jogadores WHERE time_id = ?", (t,))
    for time_id, grupo in zip(esperando, grupos, strict=False):
        conn.execute(
            "UPDATE times SET incompleto = ? WHERE id = ?",
            (int(len(grupo) < tamanho), time_id),
        )
        for p in grupo:
            conn.execute(
                "INSERT INTO time_jogadores (time_id, jogador_id, nota, ordem_chegada) "
                "VALUES (?, ?, ?, ?)",
                (time_id, p.id, p.nota, p.ordem),
            )
    for time_id in esperando[len(grupos) :]:
        conn.execute("DELETE FROM times WHERE id = ?", (time_id,))


def _grupos(jogadores, tamanho, anteriores) -> list[tuple]:
    """Times completos (pela ordem de chegada) e, no fim, quem sobra."""
    if len(jogadores) >= MINIMO_POR_TAMANHO[tamanho]:
        return [t.jogadores for t in sortear(jogadores, 0, anteriores, tamanho).times]
    # Poucos para sortear: um time só (sem escolha) e a sobra, os últimos a chegar.
    corte = len(jogadores) - len(jogadores) % tamanho
    return [g for g in (tuple(jogadores[:corte]), tuple(jogadores[corte:])) if g]
