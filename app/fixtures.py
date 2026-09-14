import asyncio
import json
import logging
import os
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.db import get_db

logger = logging.getLogger(__name__)


def resolver_caminho_fixture(caminho: str) -> str | None:
    """
    Localiza o arquivo de fixture buscando em múltiplos caminhos:
    1. Caminho exato/absoluto
    2. Relativo ao diretório atual de trabalho (CWD)
    3. Relativo à raiz do projeto (diretório pai do módulo app/)
    4. Diretório padrão do container Docker (/srv)
    5. Diretório de dados configurado no DB_PATH
    """
    if not caminho:
        return None

    # 1. Caminho absoluto
    if os.path.isabs(caminho) and os.path.exists(caminho):
        return caminho

    # 2. Relativo ao CWD
    if os.path.exists(caminho):
        return os.path.abspath(caminho)

    # 3. Raiz do projeto (diretório pai de app/)
    raiz_projeto = Path(__file__).resolve().parent.parent / caminho
    if raiz_projeto.exists():
        return str(raiz_projeto)

    # 4. Diretório /srv (Docker)
    srv_path = Path("/srv") / caminho
    if srv_path.exists():
        return str(srv_path)

    # 5. Diretório do banco de dados (ex: /data)
    from app.config import settings

    if settings.db_path and settings.db_path != ":memory:":
        dir_banco = Path(settings.db_path).parent / caminho
        if dir_banco.exists():
            return str(dir_banco)

    return None


def carregar_fixtures_arenas(caminho: str) -> list[dict[str, Any]]:
    """Carrega a lista de arenas e quadras a partir do arquivo JSON de fixture."""
    caminho_real = resolver_caminho_fixture(caminho) or caminho
    if not os.path.exists(caminho_real):
        logger.warning("Arquivo de fixture não encontrado: %s", caminho_real)
        return []

    try:
        with open(caminho_real, encoding="utf-8") as f:
            conteudo = f.read().strip()
            if not conteudo:
                return []
            dados = json.loads(conteudo)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Falha ao ler fixture de arenas em %s: %s", caminho_real, e)
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
    caminho_real = resolver_caminho_fixture(caminho) or caminho
    diretorio = os.path.dirname(caminho_real) or "."
    os.makedirs(diretorio, exist_ok=True)

    conteudo = json.dumps(arenas, indent=2, ensure_ascii=False) + "\n"

    # Escrita atômica usando arquivo temporário no mesmo diretório
    with tempfile.NamedTemporaryFile(
        "w", dir=diretorio, delete=False, encoding="utf-8"
    ) as tf:
        tf.write(conteudo)
        temp_name = tf.name

    os.replace(temp_name, caminho_real)


def adicionar_arena_fixture_sync(caminho: str, arena_nome: str) -> None:
    """Adiciona uma nova arena ao arquivo de fixtures se ainda não existir."""
    nome_limpo = arena_nome.strip()
    if not nome_limpo:
        return

    caminho_real = resolver_caminho_fixture(caminho) or caminho
    arenas = carregar_fixtures_arenas(caminho_real)
    for a in arenas:
        if a["nome"].lower() == nome_limpo.lower():
            return  # Já existe

    arenas.append({"nome": nome_limpo, "quadras": []})
    salvar_fixtures_arenas(caminho_real, arenas)


def adicionar_quadra_fixture_sync(
    caminho: str, arena_nome: str, quadra_nome: str
) -> None:
    """Adiciona uma quadra à arena especificada no arquivo de fixtures."""
    arena_limpa = arena_nome.strip()
    quadra_limpa = quadra_nome.strip()
    if not arena_limpa or not quadra_limpa:
        return

    caminho_real = resolver_caminho_fixture(caminho) or caminho
    arenas = carregar_fixtures_arenas(caminho_real)
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
        salvar_fixtures_arenas(caminho_real, arenas)


def sincronizar_fixtures_para_db_sync(db_path: str, fixture_path: str) -> None:
    """
    Popula arenas e quadras do arquivo de fixture para o banco SQLite.
    Operação idempotente e segura contra locks de conexão aninhadas.
    """
    arenas_fixture = carregar_fixtures_arenas(fixture_path)
    if not arenas_fixture:
        logger.warning(
            "Nenhuma arena para sincronizar do arquivo de fixture: %s", fixture_path
        )
        return

    from app.quadras import criar_quadra_sync

    # 1. Carrega todas as arenas existentes no SQLite (fecha a conexão em seguida)
    arenas_existentes: dict[str, str] = {}
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM arenas")
        for r in cursor.fetchall():
            arenas_existentes[r["nome"].strip().lower()] = r["id"]

    # 2. Garante que todas as arenas da fixture existam no SQLite
    for a_item in arenas_fixture:
        a_nome = a_item["nome"].strip()
        if a_nome.lower() not in arenas_existentes:
            arena_id = str(uuid.uuid4())
            agora = datetime.now(UTC).isoformat()
            with get_db(db_path) as conn:
                conn.execute(
                    "INSERT INTO arenas (id, nome, criado_em) VALUES (?, ?, ?)",
                    (arena_id, a_nome, agora),
                )
                conn.commit()
            arenas_existentes[a_nome.lower()] = arena_id
            logger.info("Arena criada a partir da fixture: %s (%s)", a_nome, arena_id)

    # 3. Carrega todas as quadras existentes no SQLite (fecha a conexão em seguida)
    quadras_existentes: set[tuple[str, str]] = set()
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT arena_id, nome FROM quadras")
        for r in cursor.fetchall():
            quadras_existentes.add((r["arena_id"], r["nome"].strip().lower()))

    # 4. Cria cada quadra faltante de forma independente (sem locks abertos)
    for a_item in arenas_fixture:
        a_nome = a_item["nome"].strip()
        arena_id = arenas_existentes[a_nome.lower()]

        for q_nome in a_item.get("quadras", []):
            q_nome_limpo = q_nome.strip()
            chave = (arena_id, q_nome_limpo.lower())
            if chave not in quadras_existentes:
                criar_quadra_sync(db_path, arena_id=arena_id, nome=q_nome_limpo)
                quadras_existentes.add(chave)
                logger.info(
                    "Quadra criada a partir da fixture: %s na arena %s",
                    q_nome_limpo,
                    a_nome,
                )


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
