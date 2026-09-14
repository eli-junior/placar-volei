import asyncio
import json
import uuid
from contextlib import nullcontext
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from app.db import get_db


class TipoEvento:
    PARTIDA_INICIADA = "PARTIDA_INICIADA"
    PONTO_MARCADO = "PONTO_MARCADO"
    PONTO_DESFEITO = "PONTO_DESFEITO"
    REGRA_ALTERADA = "REGRA_ALTERADA"
    PARTIDA_ENCERRADA = "PARTIDA_ENCERRADA"
    PAPEL_ALTERADO = "PAPEL_ALTERADO"
    ADMIN_SUCEDIDO = "ADMIN_SUCEDIDO"
    ADMIN_ASSUMIDO = "ADMIN_ASSUMIDO"
    CONTROLE_ASSUMIDO = "CONTROLE_ASSUMIDO"


@dataclass(frozen=True)
class Evento:
    id: str
    quadra_id: str
    partida_id: str
    seq: int
    tipo: str
    payload: dict[str, Any]
    autor_id: str | None
    criado_em: str


_quadra_locks: dict[str, asyncio.Lock] = {}


def get_quadra_lock(quadra_id: str) -> asyncio.Lock:
    if quadra_id not in _quadra_locks:
        _quadra_locks[quadra_id] = asyncio.Lock()
    return _quadra_locks[quadra_id]


def append_evento_sync(
    db_path: str,
    quadra_id: str,
    partida_id: str,
    tipo: str,
    payload: dict[str, Any],
    autor_id: str | None = None,
    *,
    connection=None,
) -> Evento:
    with nullcontext(connection) if connection is not None else get_db(db_path) as conn:
        if connection is None:
            conn.execute("BEGIN IMMEDIATE")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COALESCE(MAX(seq), 0) FROM eventos WHERE partida_id = ?",
            (partida_id,),
        )
        (max_seq,) = cursor.fetchone()
        next_seq = max_seq + 1
        evento_id = str(uuid.uuid4())
        criado_em = datetime.now(UTC).isoformat()
        payload_json = json.dumps(payload, ensure_ascii=False)

        cursor.execute(
            """
            INSERT INTO eventos (id, quadra_id, partida_id, seq, tipo, payload, autor_id, criado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evento_id,
                quadra_id,
                partida_id,
                next_seq,
                tipo,
                payload_json,
                autor_id,
                criado_em,
            ),
        )
        if connection is None:
            conn.commit()

        return Evento(
            id=evento_id,
            quadra_id=quadra_id,
            partida_id=partida_id,
            seq=next_seq,
            tipo=tipo,
            payload=payload,
            autor_id=autor_id,
            criado_em=criado_em,
        )


async def append_evento(
    db_path: str,
    quadra_id: str,
    partida_id: str,
    tipo: str,
    payload: dict[str, Any],
    autor_id: str | None = None,
) -> Evento:
    lock = get_quadra_lock(quadra_id)
    async with lock:
        return await asyncio.to_thread(
            append_evento_sync,
            db_path,
            quadra_id,
            partida_id,
            tipo,
            payload,
            autor_id,
        )


def carregar_eventos_sync(
    db_path: str, partida_id: str, *, connection=None
) -> list[Evento]:
    with nullcontext(connection) if connection is not None else get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, quadra_id, partida_id, seq, tipo, payload, autor_id, criado_em
            FROM eventos
            WHERE partida_id = ?
            ORDER BY seq ASC
            """,
            (partida_id,),
        )
        rows = cursor.fetchall()
        return [
            Evento(
                id=row["id"],
                quadra_id=row["quadra_id"],
                partida_id=row["partida_id"],
                seq=row["seq"],
                tipo=row["tipo"],
                payload=json.loads(row["payload"]),
                autor_id=row["autor_id"],
                criado_em=row["criado_em"],
            )
            for row in rows
        ]


async def carregar_eventos(db_path: str, partida_id: str) -> list[Evento]:
    return await asyncio.to_thread(carregar_eventos_sync, db_path, partida_id)
