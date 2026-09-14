import asyncio
import logging
import os
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime

from app.config import settings

logger = logging.getLogger(__name__)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS app_meta (
    chave TEXT PRIMARY KEY,
    valor TEXT NOT NULL,
    atualizado_em TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS arenas (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    criado_em TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS quadras (
    id TEXT PRIMARY KEY,
    arena_id TEXT REFERENCES arenas(id),
    nome TEXT NOT NULL,
    criado_em TEXT NOT NULL,
    atualizado_em TEXT NOT NULL,
    controle_id TEXT,
    controle_versao INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS partidas (
    id TEXT PRIMARY KEY,
    quadra_id TEXT NOT NULL REFERENCES quadras(id) ON DELETE CASCADE,
    status TEXT NOT NULL,
    criado_em TEXT NOT NULL,
    encerrado_em TEXT
);

CREATE TABLE IF NOT EXISTS participantes (
    id TEXT PRIMARY KEY,
    quadra_id TEXT NOT NULL REFERENCES quadras(id) ON DELETE CASCADE,
    apelido TEXT NOT NULL,
    papel TEXT NOT NULL,
    criado_em TEXT NOT NULL,
    ultimo_visto_em TEXT NOT NULL,
    session_hash TEXT NOT NULL,
    UNIQUE(quadra_id, session_hash)
);

CREATE TABLE IF NOT EXISTS eventos (
    id TEXT PRIMARY KEY,
    quadra_id TEXT NOT NULL,
    partida_id TEXT NOT NULL,
    seq INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    payload TEXT NOT NULL,
    autor_id TEXT,
    criado_em TEXT NOT NULL,
    UNIQUE(partida_id, seq)
);

CREATE INDEX IF NOT EXISTS idx_quadras_arena ON quadras (arena_id);
CREATE INDEX IF NOT EXISTS idx_quadras_atualizado ON quadras (atualizado_em);
CREATE INDEX IF NOT EXISTS idx_eventos_partida_seq ON eventos (partida_id, seq);
CREATE INDEX IF NOT EXISTS idx_partidas_quadra ON partidas (quadra_id);
CREATE INDEX IF NOT EXISTS idx_participantes_quadra ON participantes (quadra_id);
"""


@contextmanager
def get_db(db_path: str | None = None) -> Generator[sqlite3.Connection, None, None]:
    target_path = db_path if db_path is not None else settings.db_path
    if target_path != ":memory:":
        parent_dir = os.path.dirname(target_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def init_db_sync(db_path: str | None = None, fixture_path: str | None = None) -> None:
    target_path = db_path if db_path is not None else settings.db_path

    # Se o banco está em arquivo e já existe, verifica se precisa ser apagado para recriação
    if target_path != ":memory:" and os.path.exists(target_path):
        precisa_apagar = False

        if settings.reset_db_on_startup:
            logger.info("RESET_DB_ON_STARTUP ativo. Apagando banco de dados...")
            precisa_apagar = True
        else:
            temp_conn = None
            try:
                temp_conn = sqlite3.connect(target_path)
                temp_conn.row_factory = sqlite3.Row
                cursor = temp_conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='app_meta'"
                )
                if cursor.fetchone():
                    cursor.execute("SELECT valor FROM app_meta WHERE chave = 'versao'")
                    row = cursor.fetchone()
                    versao_gravada = row["valor"] if row else None
                    if versao_gravada != settings.version:
                        logger.info(
                            "Nova versão detectada (%s -> %s). Apagando banco de dados anterior...",
                            versao_gravada,
                            settings.version,
                        )
                        precisa_apagar = True
                else:
                    logger.info(
                        "Banco de versão anterior sem app_meta detectado. Recriando para a versão %s...",
                        settings.version,
                    )
                    precisa_apagar = True
            except (sqlite3.Error, OSError) as e:
                logger.warning(
                    "Erro ao verificar versão do banco (%s). Recriando por segurança...",
                    e,
                )
                precisa_apagar = True
            finally:
                if temp_conn is not None:
                    temp_conn.close()

        if precisa_apagar:
            apagou_todos = True
            for sufixo in ["", "-wal", "-shm"]:
                caminho = f"{target_path}{sufixo}"
                if os.path.exists(caminho):
                    try:
                        os.remove(caminho)
                    except OSError as e:
                        apagou_todos = False
                        logger.warning("Falha ao remover arquivo %s: %s", caminho, e)

            # Fallback seguro: se a exclusão no SO falhar por lock momentâneo,
            # limpa as tabelas existentes diretamente
            if not apagou_todos and os.path.exists(target_path):
                try:
                    conn_fallback = sqlite3.connect(target_path)
                    try:
                        cur_fb = conn_fallback.cursor()
                        cur_fb.execute(
                            "SELECT name FROM sqlite_master WHERE type='table'"
                        )
                        tabelas = [
                            r[0]
                            for r in cur_fb.fetchall()
                            if not r[0].startswith("sqlite_")
                        ]
                        for t in tabelas:
                            cur_fb.execute(f"DROP TABLE IF EXISTS {t}")
                        conn_fallback.commit()
                    finally:
                        conn_fallback.close()
                except (sqlite3.Error, OSError) as e:
                    logger.warning("Fallback de limpeza de tabelas falhou: %s", e)

    with get_db(target_path) as conn:
        conn.executescript(SCHEMA_SQL)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(quadras);")
        colunas = [row["name"] for row in cursor.fetchall()]
        if "atualizado_em" not in colunas:
            cursor.execute("ALTER TABLE quadras ADD COLUMN atualizado_em TEXT;")
            cursor.execute(
                "UPDATE quadras SET atualizado_em = criado_em WHERE atualizado_em IS NULL;"
            )
        if "arena_id" not in colunas:
            cursor.execute("ALTER TABLE quadras ADD COLUMN arena_id TEXT;")

        agora = datetime.now(UTC).isoformat()
        cursor.execute(
            """
            INSERT INTO app_meta (chave, valor, atualizado_em)
            VALUES ('versao', ?, ?)
            ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor, atualizado_em = excluded.atualizado_em;
            """,
            (settings.version, agora),
        )
        conn.commit()

    target_fixture = (
        fixture_path if fixture_path is not None else settings.default_arenas_file
    )
    if target_fixture:
        from app.fixtures import (
            resolver_caminho_fixture,
            sincronizar_fixtures_para_db_sync,
        )

        caminho_resolvido = resolver_caminho_fixture(target_fixture)
        if caminho_resolvido:
            sincronizar_fixtures_para_db_sync(target_path, caminho_resolvido)
        else:
            logger.warning(
                "Arquivo de fixture '%s' não foi localizado no sistema de arquivos.",
                target_fixture,
            )


async def init_db(db_path: str | None = None, fixture_path: str | None = None) -> None:
    await asyncio.to_thread(init_db_sync, db_path, fixture_path)
