import asyncio
import json
import logging
import os
import tempfile
import uuid
from datetime import UTC, datetime
from typing import Any

from app.db import get_db

logger = logging.getLogger(__name__)


def carregar_fixtures_arenas(caminho: str) -> list[dict[str, Any]]:
    """Carrega a lista de arenas e quadras a partir do arquivo JSON de fixture."""
    if not os.path.exists(caminho):
        return []

    try:
        with open(caminho, encoding="utf-8") as f:
            conteudo = f.read().strip()
            if not conteudo:
                return []
            dados = json.loads(conteudo)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Falha ao ler fixture de arenas em %s: %s", caminho, e)
        return []

    if not isinstance(dados, list):
        return []

    arenas_limpas = []
    for item in dados:
        if not isinstance(item, dict) or "nome" not in item:
            continue
        nome = str(item["nome"]).strip()
        if not nome:
            continue

        quadras_raw = item.get("quadras", [])
        quadras = []
        if isinstance(quadras_raw, list):
            for q in quadras_raw:
                if isinstance(q, str):
                    q_nome = q.strip()
                elif isinstance(q, dict) and "nome" in q:
                    q_nome = str(q["nome"]).strip()
                else:
                    continue
                if q_nome and q_nome not in quadras:
                    quadras.append(q_nome)

        arenas_limpas.append({"nome": nome, "quadras": quadras})

    return arenas_limpas


def salvar_fixtures_arenas(caminho: str, arenas: list[dict[str, Any]]) -> None:
    """Salva a lista de arenas no arquivo JSON de forma atômica."""
    diretorio = os.path.dirname(caminho) or "."
    os.makedirs(diretorio, exist_ok=True)

    conteudo = json.dumps(arenas, indent=2, ensure_ascii=False) + "\n"

    # Escrita atômica usando arquivo temporário no mesmo diretório
    with tempfile.NamedTemporaryFile(
        "w", dir=diretorio, delete=False, encoding="utf-8"
    ) as tf:
        tf.write(conteudo)
        temp_name = tf.name

    os.replace(temp_name, caminho)


def adicionar_arena_fixture_sync(caminho: str, arena_nome: str) -> None:
    """Adiciona uma nova arena ao arquivo de fixtures se ainda não existir."""
    nome_limpo = arena_nome.strip()
    if not nome_limpo:
        return

    arenas = carregar_fixtures_arenas(caminho)
    for a in arenas:
        if a["nome"].lower() == nome_limpo.lower():
            return  # Já existe

    arenas.append({"nome": nome_limpo, "quadras": []})
    salvar_fixtures_arenas(caminho, arenas)


def adicionar_quadra_fixture_sync(
    caminho: str, arena_nome: str, quadra_nome: str
) -> None:
    """Adiciona uma quadra à arena especificada no arquivo de fixtures."""
    arena_limpa = arena_nome.strip()
    quadra_limpa = quadra_nome.strip()
    if not arena_limpa or not quadra_limpa:
        return

    arenas = carregar_fixtures_arenas(caminho)
    arena_encontrada = None
    for a in arenas:
        if a["nome"].lower() == arena_limpa.lower():
            arena_encontrada = a
            break

    if arena_encontrada is None:
        arena_encontrada = {"nome": arena_limpa, "quadras": []}
        arenas.append(arena_encontrada)

    if quadra_limpa not in arena_encontrada["quadras"]:
        arena_encontrada["quadras"].append(quadra_limpa)
        salvar_fixtures_arenas(caminho, arenas)


def sincronizar_fixtures_para_db_sync(db_path: str, fixture_path: str) -> None:
    """
    Popula arenas e quadras do arquivo de fixture para o banco SQLite.
    Operação idempotente: não duplica arenas nem quadras já existentes.
    """
    arenas_fixture = carregar_fixtures_arenas(fixture_path)
    if not arenas_fixture:
        return

    from app.quadras import criar_quadra_sync

    with get_db(db_path) as conn:
        cursor = conn.cursor()

        for a_item in arenas_fixture:
            a_nome = a_item["nome"]
            cursor.execute("SELECT id FROM arenas WHERE nome = ?", (a_nome,))
            row_arena = cursor.fetchone()

            if row_arena:
                arena_id = row_arena["id"]
            else:
                arena_id = str(uuid.uuid4())
                agora = datetime.now(UTC).isoformat()
                cursor.execute(
                    "INSERT INTO arenas (id, nome, criado_em) VALUES (?, ?, ?)",
                    (arena_id, a_nome, agora),
                )
                conn.commit()

            # Popula quadras da arena
            for q_nome in a_item.get("quadras", []):
                cursor.execute(
                    "SELECT id FROM quadras WHERE arena_id = ? AND nome = ?",
                    (arena_id, q_nome),
                )
                row_quadra = cursor.fetchone()
                if not row_quadra:
                    # Cria a quadra com sua partida ativa e evento inicial
                    criar_quadra_sync(db_path, arena_id=arena_id, nome=q_nome)


async def sincronizar_fixtures_para_db(db_path: str, fixture_path: str) -> None:
    await asyncio.to_thread(sincronizar_fixtures_para_db_sync, db_path, fixture_path)


async def adicionar_arena_fixture(caminho: str, arena_nome: str) -> None:
    await asyncio.to_thread(adicionar_arena_fixture_sync, caminho, arena_nome)


async def adicionar_quadra_fixture(
    caminho: str, arena_nome: str, quadra_nome: str
) -> None:
    await asyncio.to_thread(
        adicionar_quadra_fixture_sync, caminho, arena_nome, quadra_nome
    )
