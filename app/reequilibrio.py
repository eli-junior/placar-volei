"""Reequilíbrio entre rodadas (CV8.DS2.US4): nota efetiva e duplas anteriores.

Só lê rodadas `encerradas` (com campeão) da sessão; rodada cancelada não conta.
A nota cadastrada do jogador nunca muda: o ajuste vale só na sessão (RN-14).
"""

AJUSTE_MAXIMO = 15


def nota_efetiva(base: int, saldo: int, partidas: int) -> int:
    """`clamp(base + clamp(round(2 × saldo ÷ partidas), ±15), 1, 100)` (RN-14)."""
    if partidas <= 0:
        return base
    ajuste = max(-AJUSTE_MAXIMO, min(AJUSTE_MAXIMO, round(2 * saldo / partidas)))
    return max(1, min(100, base + ajuste))


def saldos_da_sessao(conn, sessao_id: str) -> dict[str, tuple[int, int]]:
    """Por jogador: (saldo, partidas) nas rodadas encerradas da sessão. O
    escalado soma os dois times em que jogou."""
    acumulado: dict[str, list[int]] = {}
    partidas = conn.execute(
        "SELECT p.time_a_id, p.time_b_id, p.placar_a, p.placar_b "
        "FROM partidas_rodada p JOIN rodadas r ON r.id = p.rodada_id "
        "WHERE r.sessao_id = ? AND r.estado = 'encerrada' "
        "AND p.estado = 'encerrada' AND p.placar_a IS NOT NULL",
        (sessao_id,),
    ).fetchall()
    for p in partidas:
        for time_id, feitos, sofridos in (
            (p["time_a_id"], p["placar_a"], p["placar_b"]),
            (p["time_b_id"], p["placar_b"], p["placar_a"]),
        ):
            for j in conn.execute(
                "SELECT jogador_id FROM time_jogadores WHERE time_id = ?", (time_id,)
            ):
                linha = acumulado.setdefault(j["jogador_id"], [0, 0])
                linha[0] += feitos - sofridos
                linha[1] += 1
    return {k: (v[0], v[1]) for k, v in acumulado.items()}


def duplas_anteriores(conn, sessao_id: str) -> frozenset:
    """Duplas já formadas nas rodadas encerradas da sessão (conjuntos de ids)."""
    por_time: dict[str, set[str]] = {}
    for r in conn.execute(
        "SELECT tj.time_id, tj.jogador_id FROM time_jogadores tj "
        "JOIN times t ON t.id = tj.time_id JOIN rodadas r ON r.id = t.rodada_id "
        "WHERE r.sessao_id = ? AND r.estado = 'encerrada'",
        (sessao_id,),
    ):
        por_time.setdefault(r["time_id"], set()).add(r["jogador_id"])
    return frozenset(frozenset(ids) for ids in por_time.values() if len(ids) == 2)


def tem_rodada_anterior(conn, sessao_id: str) -> bool:
    return (
        conn.execute(
            "SELECT 1 FROM rodadas WHERE sessao_id = ? AND estado = 'encerrada' LIMIT 1",
            (sessao_id,),
        ).fetchone()
        is not None
    )
