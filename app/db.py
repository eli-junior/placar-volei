import asyncio
import os
import sqlite3

from app.config import settings

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS arenas (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    criado_em TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS quadras (
    id TEXT PRIMARY KEY,
    arena_id TEXT REFERENCES arenas(id),
    nome TEXT NOT NULL,
    criado_em TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS partidas (
    id TEXT PRIMARY KEY,
    quadra_id TEXT NOT NULL REFERENCES quadras(id),
    status TEXT NOT NULL,
    criado_em TEXT NOT NULL,
    encerrado_em TEXT
);

CREATE TABLE IF NOT EXISTS participantes (
    id TEXT PRIMARY KEY,
    quadra_id TEXT NOT NULL REFERENCES quadras(id),
    apelido TEXT NOT NULL,
    papel TEXT NOT NULL,
    criado_em TEXT NOT NULL,
    ultimo_visto_em TEXT NOT NULL
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
CREATE INDEX IF NOT EXISTS idx_eventos_partida_seq ON eventos (partida_id, seq);
CREATE INDEX IF NOT EXISTS idx_partidas_quadra ON partidas (quadra_id);
CREATE INDEX IF NOT EXISTS idx_participantes_quadra ON participantes (quadra_id);
"""


def get_db(db_path: str | None = None) -> sqlite3.Connection:
    target_path = db_path if db_path is not None else settings.db_path
    if target_path != ":memory:":
        parent_dir = os.path.dirname(target_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db_sync(db_path: str | None = None) -> None:
    with get_db(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
        # Migração idempotente se arena_id ainda não existir na tabela quadras
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(quadras);")
        colunas = [row["name"] for row in cursor.fetchall()]
        if "arena_id" not in colunas:
            cursor.execute(
                "ALTER TABLE quadras ADD COLUMN arena_id TEXT REFERENCES arenas(id);"
            )
        conn.commit()


async def init_db(db_path: str | None = None) -> None:
    await asyncio.to_thread(init_db_sync, db_path)
