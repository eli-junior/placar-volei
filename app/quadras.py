import asyncio
import uuid
from datetime import UTC, datetime
from typing import Any

from app.config import settings
from app.db import get_db
from app.eventos import TipoEvento, append_evento_sync, get_quadra_lock

# --- ARENAS ---


def criar_arena_sync(db_path: str, nome: str) -> dict[str, Any]:
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM arenas")
        (total_arenas,) = cursor.fetchone()
        if total_arenas >= settings.max_arenas:
            raise ValueError(f"Limite máximo de {settings.max_arenas} arenas atingido.")

        arena_id = str(uuid.uuid4())
        agora = datetime.now(UTC).isoformat()
        nome_limpo = nome.strip()

        conn.execute(
            "INSERT INTO arenas (id, nome, criado_em) VALUES (?, ?, ?)",
            (arena_id, nome_limpo, agora),
        )
        conn.commit()

    return {
        "id": arena_id,
        "nome": nome_limpo,
        "criado_em": agora,
        "quadras_count": 0,
    }


async def criar_arena(db_path: str, nome: str) -> dict[str, Any]:
    return await asyncio.to_thread(criar_arena_sync, db_path, nome)


def listar_arenas_sync(db_path: str) -> list[dict[str, Any]]:
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT a.id, a.nome, a.criado_em,
                   COUNT(q.id) as quadras_count
            FROM arenas a
            LEFT JOIN quadras q ON q.arena_id = a.id
            GROUP BY a.id
            ORDER BY a.criado_em DESC
            """
        )
        rows = cursor.fetchall()
        return [
            {
                "id": r["id"],
                "nome": r["nome"],
                "criado_em": r["criado_em"],
                "quadras_count": r["quadras_count"],
            }
            for r in rows
        ]


async def listar_arenas(db_path: str) -> list[dict[str, Any]]:
    return await asyncio.to_thread(listar_arenas_sync, db_path)


def obter_arena_sync(db_path: str, arena_id: str) -> dict[str, Any] | None:
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT a.id, a.nome, a.criado_em,
                   COUNT(q.id) as quadras_count
            FROM arenas a
            LEFT JOIN quadras q ON q.arena_id = a.id
            WHERE a.id = ?
            GROUP BY a.id
            """,
            (arena_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "nome": row["nome"],
            "criado_em": row["criado_em"],
            "quadras_count": row["quadras_count"],
        }


async def obter_arena(db_path: str, arena_id: str) -> dict[str, Any] | None:
    return await asyncio.to_thread(obter_arena_sync, db_path, arena_id)


# --- QUADRAS ---


def criar_quadra_sync(
    db_path: str,
    arena_id: str,
    nome: str,
) -> dict[str, Any]:
    quadra_id = str(uuid.uuid4())
    partida_id = str(uuid.uuid4())
    agora = datetime.now(UTC).isoformat()
    nome_limpo = nome.strip()

    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM quadras WHERE arena_id = ?",
            (arena_id,),
        )
        (total_quadras,) = cursor.fetchone()
        if total_quadras >= settings.max_quadras_por_arena:
            raise ValueError(
                f"Limite máximo de {settings.max_quadras_por_arena} quadras para esta arena atingido."
            )

        conn.execute(
            "INSERT INTO quadras (id, arena_id, nome, criado_em) VALUES (?, ?, ?, ?)",
            (quadra_id, arena_id, nome_limpo, agora),
        )
        conn.execute(
            "INSERT INTO partidas (id, quadra_id, status, criado_em) VALUES (?, ?, ?, ?)",
            (partida_id, quadra_id, "EM_ANDAMENTO", agora),
        )
        conn.commit()

    # Registra o evento de partida iniciada com regra padrão
    append_evento_sync(
        db_path,
        quadra_id=quadra_id,
        partida_id=partida_id,
        tipo=TipoEvento.PARTIDA_INICIADA,
        payload={
            "alvo": 12,
            "vantagem": True,
            "teto": None,
            "equipe_a": "Equipe A",
            "equipe_b": "Equipe B",
        },
        autor_id=None,
    )

    return {
        "id": quadra_id,
        "arena_id": arena_id,
        "nome": nome_limpo,
        "criado_em": agora,
        "partida_id": partida_id,
    }


async def criar_quadra(db_path: str, arena_id: str, nome: str) -> dict[str, Any]:
    return await asyncio.to_thread(criar_quadra_sync, db_path, arena_id, nome)


def listar_quadras_sync(
    db_path: str, arena_id: str | None = None
) -> list[dict[str, Any]]:
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        query = """
            SELECT q.id, q.arena_id, q.nome, q.criado_em,
                   a.nome as arena_nome,
                   COUNT(p.id) as participantes_count
            FROM quadras q
            LEFT JOIN arenas a ON a.id = q.arena_id
            LEFT JOIN participantes p ON p.quadra_id = q.id
        """
        params = []
        if arena_id:
            query += " WHERE q.arena_id = ?"
            params.append(arena_id)
        query += " GROUP BY q.id ORDER BY q.criado_em DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [
            {
                "id": r["id"],
                "arena_id": r["arena_id"],
                "arena_nome": r["arena_nome"],
                "nome": r["nome"],
                "criado_em": r["criado_em"],
                "participantes_count": r["participantes_count"],
            }
            for r in rows
        ]


async def listar_quadras(
    db_path: str, arena_id: str | None = None
) -> list[dict[str, Any]]:
    return await asyncio.to_thread(listar_quadras_sync, db_path, arena_id)


def obter_quadra_sync(db_path: str, quadra_id: str) -> dict[str, Any] | None:
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT q.id, q.arena_id, q.nome, q.criado_em, a.nome as arena_nome
            FROM quadras q
            LEFT JOIN arenas a ON a.id = q.arena_id
            WHERE q.id = ?
            """,
            (quadra_id,),
        )
        quadra = cursor.fetchone()
        if not quadra:
            return None

        cursor.execute(
            """
            SELECT id FROM partidas
            WHERE quadra_id = ? AND status = 'EM_ANDAMENTO'
            ORDER BY criado_em DESC LIMIT 1
            """,
            (quadra_id,),
        )
        partida = cursor.fetchone()
        partida_id = partida["id"] if partida else None

        return {
            "id": quadra["id"],
            "arena_id": quadra["arena_id"],
            "arena_nome": quadra["arena_nome"],
            "nome": quadra["nome"],
            "criado_em": quadra["criado_em"],
            "partida_id": partida_id,
        }


async def obter_quadra(db_path: str, quadra_id: str) -> dict[str, Any] | None:
    return await asyncio.to_thread(obter_quadra_sync, db_path, quadra_id)


# --- PARTICIPANTES ---


def registrar_participante_sync(
    db_path: str,
    quadra_id: str,
    session_id: str,
    apelido: str,
) -> dict[str, Any]:
    participante_id = f"{quadra_id}:{session_id}"
    agora = datetime.now(UTC).isoformat()
    apelido_limpo = apelido.strip()

    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, quadra_id, apelido, papel, criado_em, ultimo_visto_em FROM participantes WHERE id = ?",
            (participante_id,),
        )
        existente = cursor.fetchone()

        if existente:
            cursor.execute(
                "UPDATE participantes SET apelido = ?, ultimo_visto_em = ? WHERE id = ?",
                (apelido_limpo, agora, participante_id),
            )
            conn.commit()
            return {
                "id": participante_id,
                "quadra_id": quadra_id,
                "apelido": apelido_limpo,
                "papel": existente["papel"],
                "criado_em": existente["criado_em"],
                "ultimo_visto_em": agora,
            }

        # Valida limite máximo de participantes para esta quadra
        cursor.execute(
            "SELECT COUNT(*) FROM participantes WHERE quadra_id = ?",
            (quadra_id,),
        )
        (total_participantes,) = cursor.fetchone()
        if total_participantes >= settings.max_participantes_por_quadra:
            raise ValueError(
                f"Limite máximo de {settings.max_participantes_por_quadra} participantes para esta quadra atingido."
            )

        papel = "ADMIN" if total_participantes == 0 else "ESPECTADOR"

        cursor.execute(
            """
            INSERT INTO participantes (id, quadra_id, apelido, papel, criado_em, ultimo_visto_em)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (participante_id, quadra_id, apelido_limpo, papel, agora, agora),
        )
        conn.commit()

        return {
            "id": participante_id,
            "quadra_id": quadra_id,
            "apelido": apelido_limpo,
            "papel": papel,
            "criado_em": agora,
            "ultimo_visto_em": agora,
        }


async def registrar_participante(
    db_path: str,
    quadra_id: str,
    session_id: str,
    apelido: str,
) -> dict[str, Any]:
    lock = get_quadra_lock(quadra_id)
    async with lock:
        return await asyncio.to_thread(
            registrar_participante_sync,
            db_path,
            quadra_id,
            session_id,
            apelido,
        )


def obter_participante_sync(
    db_path: str,
    quadra_id: str,
    session_id: str,
) -> dict[str, Any] | None:
    participante_id = f"{quadra_id}:{session_id}"
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, quadra_id, apelido, papel, criado_em, ultimo_visto_em FROM participantes WHERE id = ?",
            (participante_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "quadra_id": row["quadra_id"],
            "apelido": row["apelido"],
            "papel": row["papel"],
            "criado_em": row["criado_em"],
            "ultimo_visto_em": row["ultimo_visto_em"],
        }


async def obter_participante(
    db_path: str,
    quadra_id: str,
    session_id: str,
) -> dict[str, Any] | None:
    return await asyncio.to_thread(
        obter_participante_sync, db_path, quadra_id, session_id
    )


def listar_participantes_sync(db_path: str, quadra_id: str) -> list[dict[str, Any]]:
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, quadra_id, apelido, papel, criado_em, ultimo_visto_em
            FROM participantes
            WHERE quadra_id = ?
            ORDER BY criado_em ASC
            """,
            (quadra_id,),
        )
        rows = cursor.fetchall()
        return [
            {
                "id": r["id"],
                "quadra_id": r["quadra_id"],
                "apelido": r["apelido"],
                "papel": r["papel"],
                "criado_em": r["criado_em"],
                "ultimo_visto_em": r["ultimo_visto_em"],
            }
            for r in rows
        ]


async def listar_participantes(db_path: str, quadra_id: str) -> list[dict[str, Any]]:
    return await asyncio.to_thread(listar_participantes_sync, db_path, quadra_id)
