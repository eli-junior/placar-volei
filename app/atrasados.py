"""Atrasado no meio da rodada (CV8.DS3.US9, RN-06).

O jogador que chega com a rodada em andamento vira, sozinho, um time
incompleto no fim da fila (`origem = 'atrasado'`) e escolhe o parceiro na sua
vez, pela lista de escalação. Dois atrasados nunca formam dupla entre si: quem
está em time ativo não é elegível. Depois do início do mata-mata ninguém entra;
o jogador continua ausente e entra no próximo sorteio.
"""

import uuid

from app.gerenciador_db import agora, erro_de_campo, exigir_sessao_aberta
from app.jogadores import obter_jogador


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
