"""Desfazer a última partida encerrada (CV8.DS3.US7, RN-09).

O estado da rodada (fila, reis, eliminados, vitórias) é derivado das partidas
encerradas; apagar a última devolve tudo ao instante anterior. Vale um nível só:
`rodadas.desfeito` fica ligado até a próxima partida ser encerrada. Se a última
partida deu o campeão, a rodada é reaberta; isso só é possível enquanto não há
outra rodada ativa. Uma partida chamada depois da última é descartada junto (ela
foi chamada a partir do estado que está sendo desfeito).
"""

from app.gerenciador_db import erro_de_campo, exigir_sessao_aberta


def _alvo(conn, sessao_id: str):
    """(rodada, última partida encerrada) que o desfazer atingiria, ou (None, None)."""
    rodada = conn.execute(
        "SELECT * FROM rodadas WHERE sessao_id = ? AND estado IN ('proposta', 'em_andamento')",
        (sessao_id,),
    ).fetchone()
    if rodada is not None and rodada["estado"] == "proposta":
        return None, None
    if rodada is None:
        rodada = conn.execute(
            "SELECT * FROM rodadas WHERE sessao_id = ? AND estado = 'encerrada' "
            "ORDER BY numero DESC LIMIT 1",
            (sessao_id,),
        ).fetchone()
    if rodada is None or rodada["desfeito"]:
        return None, None
    ultima = conn.execute(
        "SELECT * FROM partidas_rodada WHERE rodada_id = ? AND estado = 'encerrada' "
        "ORDER BY ordem DESC LIMIT 1",
        (rodada["id"],),
    ).fetchone()
    return (rodada, ultima) if ultima else (None, None)


def pode_desfazer(conn, sessao_id: str) -> bool:
    return _alvo(conn, sessao_id)[0] is not None


def desfazer_ultima(conn) -> None:
    sessao = exigir_sessao_aberta(conn)
    rodada, ultima = _alvo(conn, sessao["id"])
    if rodada is None:
        raise erro_de_campo(
            409,
            "rodada",
            "não há partida encerrada para desfazer (ou ela já foi desfeita)",
            "sem_desfazer",
        )
    conn.execute(
        "DELETE FROM partidas_rodada WHERE rodada_id = ? AND estado = 'chamada'",
        (rodada["id"],),
    )
    conn.execute("DELETE FROM partidas_rodada WHERE id = ?", (ultima["id"],))
    # Voltar de uma partida da fila antes do mata-mata desfaz o início dele.
    conn.execute(
        "UPDATE rodadas SET desfeito = 1, estado = 'em_andamento', "
        "campeao_time_id = NULL, "
        "mata_mata_em = CASE WHEN ? = 'fila' THEN NULL ELSE mata_mata_em END "
        "WHERE id = ?",
        (ultima["fase"], rodada["id"]),
    )
