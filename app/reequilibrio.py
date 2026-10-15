"""Reequilíbrio entre rodadas (CV8.DS2.US4): duplas anteriores da sessão.

Só lê rodadas `encerradas` (com campeão); rodada cancelada não conta. A nota do
jogador evolui com as partidas em `app.nota_viva` (decisão de 2026-10-10).
`ultima_partida` (US23) conta também rodadas canceladas: o cansaço é físico.
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


def ultima_partida(conn, sessao_id: str) -> dict[str, int]:
    """Por jogador, o número (1, 2, 3... em ordem cronológica) da última partida
    encerrada que ele jogou na sessão, em qualquer rodada, cancelada inclusive
    (US23). Quem jogou cada partida vem de `ajustes_nota`, gravado no
    encerramento; sem esse registro (notas resetadas ou partida antiga), dos
    times da partida."""
    ultima: dict[str, int] = {}
    partidas = conn.execute(
        "SELECT p.id, p.time_a_id, p.time_b_id FROM partidas_rodada p "
        "JOIN rodadas r ON r.id = p.rodada_id "
        "WHERE r.sessao_id = ? AND p.estado = 'encerrada' "
        "ORDER BY r.numero, p.ordem",
        (sessao_id,),
    ).fetchall()
    for numero, p in enumerate(partidas, start=1):
        ids = [
            r["jogador_id"]
            for r in conn.execute(
                "SELECT jogador_id FROM ajustes_nota WHERE partida_id = ?", (p["id"],)
            )
        ] or [
            r["jogador_id"]
            for r in conn.execute(
                "SELECT jogador_id FROM time_jogadores WHERE time_id IN (?, ?)",
                (p["time_a_id"], p["time_b_id"]),
            )
        ]
        for jogador_id in ids:
            ultima[jogador_id] = numero
    return ultima
