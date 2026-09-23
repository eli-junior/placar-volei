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

CREATE TABLE IF NOT EXISTS quadras (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    criado_em TEXT NOT NULL,
    atualizado_em TEXT NOT NULL,
    controle_id TEXT,
    controle_versao INTEGER NOT NULL DEFAULT 0,
    codigo_mestre TEXT
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

CREATE INDEX IF NOT EXISTS idx_quadras_atualizado ON quadras (atualizado_em);
CREATE INDEX IF NOT EXISTS idx_eventos_partida_seq ON eventos (partida_id, seq);
CREATE INDEX IF NOT EXISTS idx_partidas_quadra ON partidas (quadra_id);
CREATE INDEX IF NOT EXISTS idx_participantes_quadra ON participantes (quadra_id);

CREATE TABLE IF NOT EXISTS watch_grants (
    participant_id TEXT PRIMARY KEY REFERENCES participantes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS watch_devices (
    id TEXT PRIMARY KEY,
    token_hash TEXT NOT NULL UNIQUE,
    device_name TEXT NOT NULL DEFAULT 'eli-smartwatch',
    code_hash TEXT UNIQUE,
    expires_at TEXT NOT NULL,
    participant_id TEXT REFERENCES participantes(id) ON DELETE CASCADE,
    owner_id TEXT REFERENCES participantes(id) ON DELETE CASCADE,
    revoked INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    approved_at TEXT,
    substitui_id TEXT
);

-- Recibo de cada lance do relógio, gravado na mesma transação do evento.
-- Recusas também geram recibo: o resultado de um id é sempre o mesmo.
CREATE TABLE IF NOT EXISTS watch_recibos (
    device_id TEXT NOT NULL,
    comando_id TEXT NOT NULL,
    quadra_id TEXT NOT NULL,
    partida_id TEXT NOT NULL,
    acao TEXT NOT NULL,
    equipe TEXT,
    alvo TEXT,
    controle_versao INTEGER NOT NULL,
    status TEXT NOT NULL,
    detalhe TEXT,
    evento_seq INTEGER,
    criado_em TEXT NOT NULL,
    PRIMARY KEY (device_id, comando_id)
);
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


def init_db_sync(db_path: str | None = None, *args, **kwargs) -> None:
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
        if "codigo_mestre" not in colunas:
            cursor.execute("ALTER TABLE quadras ADD COLUMN codigo_mestre TEXT;")
        cursor.execute("PRAGMA table_info(watch_devices);")
        if "owner_id" not in [row["name"] for row in cursor.fetchall()]:
            # Dono do relógio (CV3.DS1.US2): participant_id passa a ser o
            # participante próprio "<dono> (Relógio)".
            cursor.execute(
                "ALTER TABLE watch_devices ADD COLUMN owner_id TEXT REFERENCES participantes(id) ON DELETE CASCADE;"
            )
        cursor.execute("PRAGMA table_info(watch_devices);")
        if "substitui_id" not in [row["name"] for row in cursor.fetchall()]:
            # Vínculo que o código novo substitui (CV3.DS1.US5): revogado só
            # quando o código novo é aprovado.
            cursor.execute("ALTER TABLE watch_devices ADD COLUMN substitui_id TEXT;")
        cursor.execute("PRAGMA table_info(watch_recibos);")
        if "alvo" not in [row["name"] for row in cursor.fetchall()]:
            # Alvo do desfazer pelo relógio (CV3.DS1.US3): "seq:<n>" ou "comando:<id>".
            cursor.execute("ALTER TABLE watch_recibos ADD COLUMN alvo TEXT;")

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


async def init_db(db_path: str | None = None, *args, **kwargs) -> None:
    await asyncio.to_thread(init_db_sync, db_path, *args, **kwargs)
