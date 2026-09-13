"""Script de validação da fundação e event store (CV1.DS1.TS1)."""

import asyncio
import os
import sqlite3
import sys
from pathlib import Path

# Garante import do app mesmo quando executado isolado
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import init_db_sync
from app.eventos import TipoEvento, append_evento, carregar_eventos
from app.projecao import projetar_estado


async def main():
    db_path = "data/validacao.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    # Garante diretório data/
    Path("data").mkdir(exist_ok=True)

    print(f"1. Inicializando banco em {db_path}...")
    init_db_sync(db_path)

    quadra_id = "quadra-demo"
    partida_id = "partida-demo"

    print("2. Gravando sequência de eventos...")
    await append_evento(
        db_path,
        quadra_id,
        partida_id,
        TipoEvento.PARTIDA_INICIADA,
        {"alvo": 12, "vantagem": True},
    )
    await append_evento(
        db_path,
        quadra_id,
        partida_id,
        TipoEvento.PONTO_MARCADO,
        {"equipe": "A"},
    )
    await append_evento(
        db_path,
        quadra_id,
        partida_id,
        TipoEvento.PONTO_MARCADO,
        {"equipe": "A"},
    )
    await append_evento(
        db_path,
        quadra_id,
        partida_id,
        TipoEvento.PONTO_MARCADO,
        {"equipe": "B"},
    )
    await append_evento(
        db_path,
        quadra_id,
        partida_id,
        TipoEvento.PONTO_DESFEITO,
        {"ref_seq": 3},
    )
    await append_evento(
        db_path,
        quadra_id,
        partida_id,
        TipoEvento.PONTO_MARCADO,
        {"equipe": "B"},
    )

    print("\n3. Inspecionando o arquivo SQLite diretamente:")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT seq, tipo, payload, criado_em FROM eventos ORDER BY seq"
    ).fetchall()

    for r in rows:
        print(
            f"  seq={r['seq']} | tipo={r['tipo']} | payload={r['payload']} | UTC={r['criado_em']}"
        )

    # Verificações
    seqs = [r["seq"] for r in rows]
    assert seqs == [1, 2, 3, 4, 5, 6], "Sequência quebrada ou com buraco!"
    assert len(rows) == 6, "Total de eventos diverge!"
    # Confere que o evento 3 (ponto anulado) AINDA EXISTE intacto no banco
    assert rows[2]["seq"] == 3 and rows[2]["tipo"] == TipoEvento.PONTO_MARCADO, (
        "Evento anulado foi alterado ou apagado!"
    )
    conn.close()

    print("\n4. Executando projeção de estado:")
    eventos = await carregar_eventos(db_path, partida_id)
    estado_1 = projetar_estado(eventos)
    estado_2 = projetar_estado(eventos)

    print(f"  Placar A: {estado_1.pontos_a} | Placar B: {estado_1.pontos_b}")
    print(f"  Pontos desfeitos: {estado_1.pontos_desfeitos}")
    print(f"  Partida encerrada: {estado_1.encerrada}")
    print(f"  Determinismo (estado_1 == estado_2): {estado_1 == estado_2}")

    assert estado_1.pontos_a == 1, (
        f"Esperado 1 ponto para A, obteve {estado_1.pontos_a}"
    )
    assert estado_1.pontos_b == 2, (
        f"Esperado 2 pontos para B, obteve {estado_1.pontos_b}"
    )
    assert estado_1 == estado_2, "Projeção não é determinística!"

    print(
        "\n>>> VALIDAÇÃO APROVADA: Integridade, imutabilidade e determinismo confirmados. <<<"
    )


if __name__ == "__main__":
    asyncio.run(main())
