import asyncio
import random
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from app.config import settings
from app.db import get_db
from app.eventos import TipoEvento, append_evento_sync, get_quadra_lock
from app.identidade import hash_sessao

# --- ARENAS (Legado/Compatibilidade) ---


class CapacidadeEsgotada(ValueError):
    pass


def criar_arena_sync(db_path: str, nome: str) -> dict[str, Any]:
    nome_limpo = nome.strip()
    if not nome_limpo:
        raise ValueError("Nome da arena não pode ser vazio.")

    with get_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM arenas")
        (total,) = cursor.fetchone()
        if total >= settings.max_arenas:
            raise ValueError(f"Limite máximo de {settings.max_arenas} arenas atingido.")

        cursor.execute(
            "SELECT id FROM arenas WHERE lower(nome) = lower(?)", (nome_limpo,)
        )
        if cursor.fetchone():
            raise ValueError(f"Já existe uma arena com o nome '{nome_limpo}'.")

        arena_id = str(uuid.uuid4())
        agora = datetime.now(UTC).isoformat()
        cursor.execute(
            "INSERT INTO arenas (id, nome, criado_em) VALUES (?, ?, ?)",
            (arena_id, nome_limpo, agora),
        )
        if settings.default_arenas_file:
            from app.fixtures import adicionar_arena_fixture_sync

            adicionar_arena_fixture_sync(settings.default_arenas_file, nome_limpo)

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
            SELECT a.id, a.nome, a.criado_em, COUNT(q.id) as quadras_count
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
            "SELECT id, nome, criado_em FROM arenas WHERE id = ?", (arena_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "nome": row["nome"],
            "criado_em": row["criado_em"],
        }


async def obter_arena(db_path: str, arena_id: str) -> dict[str, Any] | None:
    return await asyncio.to_thread(obter_arena_sync, db_path, arena_id)


# --- QUADRAS / PLACARES COM CÓDIGO DE 5 DÍGITOS ---


def gerar_codigo_quadra_sync(conn) -> str:
    """Gera um código numérico de 5 dígitos (10000 a 99999) único entre as quadras ativas."""
    for _ in range(100):
        codigo = str(random.randint(10000, 99999))
        cursor = conn.execute("SELECT 1 FROM quadras WHERE id = ?", (codigo,))
        if not cursor.fetchone():
            return codigo
    raise RuntimeError("Não foi possível gerar um código único para a quadra.")


def limpar_quadras_expiradas_sync(db_path: str) -> int:
    """Remove quadras sem atualização há mais de 1 hora (TTL configurável)."""
    limite = (
        datetime.now(UTC) - timedelta(seconds=settings.quadra_ttl_seconds)
    ).isoformat()
    with get_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(quadras);")
        colunas = [row["name"] for row in cursor.fetchall()]
        if "atualizado_em" not in colunas:
            return 0

        cursor.execute("SELECT id FROM quadras WHERE atualizado_em < ?", (limite,))
        expiradas = [r["id"] for r in cursor.fetchall()]
        if expiradas:
            placeholders = ",".join("?" for _ in expiradas)
            cursor.execute(
                f"DELETE FROM eventos WHERE quadra_id IN ({placeholders})", expiradas
            )
            cursor.execute(
                f"DELETE FROM participantes WHERE quadra_id IN ({placeholders})",
                expiradas,
            )
            cursor.execute(
                f"DELETE FROM partidas WHERE quadra_id IN ({placeholders})", expiradas
            )
            cursor.execute(
                f"DELETE FROM quadras WHERE id IN ({placeholders})", expiradas
            )
            conn.commit()
        return len(expiradas)


async def limpar_quadras_expiradas(db_path: str) -> int:
    return await asyncio.to_thread(limpar_quadras_expiradas_sync, db_path)


def tocar_quadra_sync(db_path: str, quadra_id: str) -> None:
    """Atualiza o timestamp de última atividade da quadra."""
    agora = datetime.now(UTC).isoformat()
    with get_db(db_path) as conn:
        conn.execute(
            "UPDATE quadras SET atualizado_em = ? WHERE id = ?",
            (agora, quadra_id),
        )
        conn.commit()


async def tocar_quadra(db_path: str, quadra_id: str) -> None:
    await asyncio.to_thread(tocar_quadra_sync, db_path, quadra_id)


def criar_quadra_sync(
    db_path: str,
    arena_id: str | None = None,
    nome: str | None = None,
    session_id: str | None = None,
    apelido: str | None = None,
    equipe_a: str = "Equipe A",
    equipe_b: str = "Equipe B",
    jogadores_a: list[str] | None = None,
    jogadores_b: list[str] | None = None,
    alvo: int = 12,
    vantagem: bool = True,
    teto: int | None = None,
) -> dict[str, Any]:
    if teto is not None and teto < alvo:
        raise ValueError("O teto da vantagem não pode ser menor que a pontuação-alvo.")

    limpar_quadras_expiradas_sync(db_path)

    with get_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM quadras")
        (total_quadras,) = cursor.fetchone()
        if total_quadras >= settings.max_quadras:
            raise CapacidadeEsgotada(
                f"Limite máximo de {settings.max_quadras} quadras atingido."
            )

        arena_nome = None
        if arena_id:
            cursor.execute(
                "SELECT COUNT(*) FROM quadras WHERE arena_id = ?", (arena_id,)
            )
            (total_arena,) = cursor.fetchone()
            if total_arena >= settings.max_quadras_por_arena:
                raise CapacidadeEsgotada(
                    f"Limite máximo de {settings.max_quadras_por_arena} quadras para esta arena atingido."
                )
            cursor.execute("SELECT nome FROM arenas WHERE id = ?", (arena_id,))
            row_arena = cursor.fetchone()
            arena_nome = row_arena["nome"] if row_arena else None

        quadra_id = gerar_codigo_quadra_sync(conn)
        partida_id = str(uuid.uuid4())
        agora = datetime.now(UTC).isoformat()
        nome_limpo = nome.strip() if nome and nome.strip() else f"Quadra #{quadra_id}"

        conn.execute(
            "INSERT INTO quadras (id, arena_id, nome, criado_em, atualizado_em) VALUES (?, ?, ?, ?, ?)",
            (quadra_id, arena_id, nome_limpo, agora, agora),
        )
        conn.execute(
            "INSERT INTO partidas (id, quadra_id, status, criado_em) VALUES (?, ?, ?, ?)",
            (partida_id, quadra_id, "EM_ANDAMENTO", agora),
        )

        participante = None
        if apelido and session_id:
            participante_id = str(uuid.uuid4())
            apelido_limpo = apelido.strip()
            conn.execute(
                """
                INSERT INTO participantes (id, quadra_id, apelido, papel, criado_em, ultimo_visto_em, session_hash)
                VALUES (?, ?, ?, 'ADMIN', ?, ?, ?)
                """,
                (
                    participante_id,
                    quadra_id,
                    apelido_limpo,
                    agora,
                    agora,
                    hash_sessao(session_id),
                ),
            )
            participante = {
                "id": participante_id,
                "quadra_id": quadra_id,
                "apelido": apelido_limpo,
                "papel": "ADMIN",
                "criado_em": agora,
                "ultimo_visto_em": agora,
            }
        if participante:
            conn.execute(
                "UPDATE quadras SET controle_id = ?, controle_versao = 1 WHERE id = ?",
                (participante["id"], quadra_id),
            )
        # Registra o evento de partida iniciada com as regras configuradas
        append_evento_sync(
            db_path,
            quadra_id=quadra_id,
            partida_id=partida_id,
            tipo=TipoEvento.PARTIDA_INICIADA,
            payload={
                "alvo": alvo,
                "vantagem": vantagem,
                "teto": teto,
                "equipe_a": equipe_a or "Equipe A",
                "equipe_b": equipe_b or "Equipe B",
                "jogadores_a": jogadores_a or [],
                "jogadores_b": jogadores_b or [],
            },
            autor_id=participante["id"] if participante else None,
            connection=conn,
        )
        if settings.default_arenas_file and arena_nome:
            from app.fixtures import adicionar_quadra_fixture_sync

            adicionar_quadra_fixture_sync(
                settings.default_arenas_file, arena_nome, nome_limpo
            )

        conn.commit()

    resultado = {
        "id": quadra_id,
        "arena_id": arena_id,
        "arena_nome": arena_nome,
        "nome": nome_limpo,
        "criado_em": agora,
        "atualizado_em": agora,
        "partida_id": partida_id,
        "controle_id": participante["id"] if participante else None,
        "controle_versao": 1 if participante else 0,
    }
    if participante:
        resultado["participante"] = participante
    return resultado


async def criar_quadra(
    db_path: str,
    arena_id: str | None = None,
    nome: str | None = None,
    session_id: str | None = None,
    apelido: str | None = None,
    equipe_a: str = "Equipe A",
    equipe_b: str = "Equipe B",
    jogadores_a: list[str] | None = None,
    jogadores_b: list[str] | None = None,
    alvo: int = 12,
    vantagem: bool = True,
    teto: int | None = None,
) -> dict[str, Any]:
    return await asyncio.to_thread(
        criar_quadra_sync,
        db_path=db_path,
        arena_id=arena_id,
        nome=nome,
        session_id=session_id,
        apelido=apelido,
        equipe_a=equipe_a,
        equipe_b=equipe_b,
        jogadores_a=jogadores_a,
        jogadores_b=jogadores_b,
        alvo=alvo,
        vantagem=vantagem,
        teto=teto,
    )


def obter_quadra_sync(db_path: str, quadra_id: str) -> dict[str, Any] | None:
    limpar_quadras_expiradas_sync(db_path)
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT q.id, q.arena_id, q.nome, q.criado_em, q.atualizado_em, q.controle_id, q.controle_versao, a.nome as arena_nome
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
            "SELECT id FROM partidas WHERE quadra_id = ? ORDER BY criado_em DESC LIMIT 1",
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
            "atualizado_em": quadra["atualizado_em"],
            "partida_id": partida_id,
            "controle_id": quadra["controle_id"],
            "controle_versao": quadra["controle_versao"],
        }


async def obter_quadra(db_path: str, quadra_id: str) -> dict[str, Any] | None:
    return await asyncio.to_thread(obter_quadra_sync, db_path, quadra_id)


def listar_quadras_sync(
    db_path: str, arena_id: str | None = None
) -> list[dict[str, Any]]:
    limpar_quadras_expiradas_sync(db_path)
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        query = """
            SELECT q.id, q.arena_id, q.nome, q.criado_em, q.atualizado_em,
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
        query += " GROUP BY q.id ORDER BY q.atualizado_em DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [
            {
                "id": r["id"],
                "arena_id": r["arena_id"],
                "arena_nome": r["arena_nome"],
                "nome": r["nome"],
                "criado_em": r["criado_em"],
                "atualizado_em": r["atualizado_em"],
                "participantes_count": r["participantes_count"],
            }
            for r in rows
        ]


async def listar_quadras(
    db_path: str, arena_id: str | None = None
) -> list[dict[str, Any]]:
    return await asyncio.to_thread(listar_quadras_sync, db_path, arena_id)


def registrar_participante_sync(
    db_path: str,
    quadra_id: str,
    session_id: str,
    apelido: str,
) -> dict[str, Any]:
    limpar_quadras_expiradas_sync(db_path)
    participante_id = str(uuid.uuid4())
    agora = datetime.now(UTC).isoformat()
    apelido_limpo = apelido.strip()

    with get_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM quadras WHERE id = ?", (quadra_id,))
        if not cursor.fetchone():
            raise ValueError("Quadra não encontrada ou já expirou por inatividade.")

        cursor.execute(
            "SELECT id, quadra_id, apelido, papel, criado_em, ultimo_visto_em FROM participantes WHERE quadra_id = ? AND session_hash = ?",
            (quadra_id, hash_sessao(session_id)),
        )
        existente = cursor.fetchone()

        if existente:
            participante_id = existente["id"]
            cursor.execute(
                "UPDATE participantes SET apelido = ?, ultimo_visto_em = ? WHERE id = ?",
                (apelido_limpo, agora, participante_id),
            )
            cursor.execute(
                "UPDATE quadras SET atualizado_em = ? WHERE id = ?",
                (agora, quadra_id),
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
            raise CapacidadeEsgotada(
                f"Limite máximo de {settings.max_participantes_por_quadra} participantes para esta quadra atingido."
            )

        papel = "ADMIN" if total_participantes == 0 else "ESPECTADOR"
        if papel == "ADMIN":
            conn.execute(
                "UPDATE quadras SET controle_id = ?, controle_versao = 1 WHERE id = ?",
                (participante_id, quadra_id),
            )

        cursor.execute(
            """
            INSERT INTO participantes (id, quadra_id, apelido, papel, criado_em, ultimo_visto_em, session_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                participante_id,
                quadra_id,
                apelido_limpo,
                papel,
                agora,
                agora,
                hash_sessao(session_id),
            ),
        )
        cursor.execute(
            "UPDATE quadras SET atualizado_em = ? WHERE id = ?",
            (agora, quadra_id),
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
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, quadra_id, apelido, papel, criado_em, ultimo_visto_em FROM participantes WHERE quadra_id = ? AND session_hash = ?",
            (quadra_id, hash_sessao(session_id)),
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


def atualizar_ultimo_visto_sync(db_path: str, participante_id: str) -> None:
    agora = datetime.now(UTC).isoformat()
    with get_db(db_path) as conn:
        conn.execute(
            "UPDATE participantes SET ultimo_visto_em = ? WHERE id = ?",
            (agora, participante_id),
        )
        conn.commit()


async def atualizar_ultimo_visto(db_path: str, participante_id: str) -> None:
    await asyncio.to_thread(atualizar_ultimo_visto_sync, db_path, participante_id)
