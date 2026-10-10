"""Nota do jogador evolui com as partidas (CV8; decisão de 2026-10-10).

Elo adaptado à escala 1-100. A cada partida encerrada cada jogador ajusta a
própria nota (`jogadores.nota`) e o ajuste efetivo fica em `ajustes_nota`, por
partida, para o "Desfazer a última partida" reverter. As funções de cálculo são
puras; `aplicar_partida` e `reverter_partida` falam com o banco.
"""

import math

K = 4
ESCALA = 30
NOTA_MINIMA, NOTA_MAXIMA = 1, 100


def limitar(nota: float) -> int:
    return max(NOTA_MINIMA, min(NOTA_MAXIMA, int(nota)))


def esperado(forca: float, forca_rival: float) -> float:
    """Chance de vitória do time pela diferença de força média (curva de Elo)."""
    return 1 / (1 + 10 ** ((forca_rival - forca) / ESCALA))


def _arredondar(x: float) -> int:
    """Arredonda metades para longe do zero (vitória e derrota ficam simétricas)."""
    return int(math.copysign(math.floor(abs(x) + 0.5), x))


def delta_do_time(
    forca: float, forca_rival: float, venceu: bool, margem: int, alvo: int
) -> int:
    """Quanto cada jogador do time ganha (ou perde). A margem da partida pesa de
    0,5 (vitória apertada) a 1,5 (goleada, a partir do alvo inteiro)."""
    fator = 0.5 + min(1.0, margem / alvo)
    return _arredondar(
        K * ((1.0 if venceu else 0.0) - esperado(forca, forca_rival)) * fator
    )


def _notas_do_time(conn, time_id: str) -> dict[str, int]:
    return {
        r["jogador_id"]: r["nota"]
        for r in conn.execute(
            "SELECT tj.jogador_id, j.nota FROM time_jogadores tj "
            "JOIN jogadores j ON j.id = tj.jogador_id WHERE tj.time_id = ?",
            (time_id,),
        )
    }


def aplicar_partida(conn, partida_id: str, agora: str) -> None:
    """Ajusta a nota dos jogadores dos dois times pelo resultado da partida
    encerrada. Idempotente: uma partida já ajustada não ajusta de novo."""
    if conn.execute(
        "SELECT 1 FROM ajustes_nota WHERE partida_id = ? LIMIT 1", (partida_id,)
    ).fetchone():
        return
    p = conn.execute(
        "SELECT p.time_a_id, p.time_b_id, p.placar_a, p.placar_b, r.alvo "
        "FROM partidas_rodada p JOIN rodadas r ON r.id = p.rodada_id "
        "WHERE p.id = ? AND p.estado = 'encerrada' AND p.placar_a IS NOT NULL",
        (partida_id,),
    ).fetchone()
    if p is None or p["placar_a"] == p["placar_b"]:
        return
    lado_a, lado_b = (
        _notas_do_time(conn, p["time_a_id"]),
        _notas_do_time(conn, p["time_b_id"]),
    )
    if not lado_a or not lado_b:
        return
    forca_a, forca_b = (
        sum(lado_a.values()) / len(lado_a),
        sum(lado_b.values()) / len(lado_b),
    )
    margem = abs(p["placar_a"] - p["placar_b"])
    a_venceu = p["placar_a"] > p["placar_b"]
    deltas = {}
    for notas, forca, rival, venceu in (
        (lado_a, forca_a, forca_b, a_venceu),
        (lado_b, forca_b, forca_a, not a_venceu),
    ):
        d = delta_do_time(forca, rival, venceu, margem, p["alvo"])
        for jogador_id, nota in notas.items():
            deltas[jogador_id] = (nota, d)
    for jogador_id, (antes, d) in deltas.items():
        depois = limitar(antes + d)
        conn.execute(
            "INSERT INTO ajustes_nota (partida_id, jogador_id, delta) VALUES (?, ?, ?)",
            (partida_id, jogador_id, depois - antes),
        )
        if depois != antes:
            conn.execute(
                "UPDATE jogadores SET nota = ?, atualizado_em = ? WHERE id = ?",
                (depois, agora, jogador_id),
            )


def reverter_partida(conn, partida_id: str, agora: str) -> None:
    """Desfaz os ajustes de uma partida (o "Desfazer a última partida")."""
    for r in conn.execute(
        "SELECT jogador_id, delta FROM ajustes_nota WHERE partida_id = ?",
        (partida_id,),
    ).fetchall():
        if r["delta"]:
            conn.execute(
                "UPDATE jogadores SET nota = MIN(?, MAX(?, nota - ?)), atualizado_em = ? "
                "WHERE id = ?",
                (NOTA_MAXIMA, NOTA_MINIMA, r["delta"], agora, r["jogador_id"]),
            )
    conn.execute("DELETE FROM ajustes_nota WHERE partida_id = ?", (partida_id,))
