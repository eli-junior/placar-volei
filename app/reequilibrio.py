"""Reequilíbrio entre rodadas (CV8.DS2.US4): duplas anteriores da sessão.

Só lê rodadas `encerradas` (com campeão); rodada cancelada não conta. A nota do
jogador evolui com as partidas em `app.nota_viva` (decisão de 2026-10-10).
"""


def duplas_anteriores(conn, sessao_id: str, tamanho: int = 2) -> frozenset:
    """Times de `tamanho` já formados nas rodadas encerradas da sessão (conjuntos
    de ids): duplas por padrão, trios no formato trio."""
    por_time: dict[str, set[str]] = {}
    for r in conn.execute(
        "SELECT tj.time_id, tj.jogador_id FROM time_jogadores tj "
        "JOIN times t ON t.id = tj.time_id JOIN rodadas r ON r.id = t.rodada_id "
        "WHERE r.sessao_id = ? AND r.estado = 'encerrada'",
        (sessao_id,),
    ):
        por_time.setdefault(r["time_id"], set()).add(r["jogador_id"])
    return frozenset(frozenset(ids) for ids in por_time.values() if len(ids) == tamanho)


def tem_rodada_anterior(conn, sessao_id: str) -> bool:
    return (
        conn.execute(
            "SELECT 1 FROM rodadas WHERE sessao_id = ? AND estado = 'encerrada' LIMIT 1",
            (sessao_id,),
        ).fetchone()
        is not None
    )
