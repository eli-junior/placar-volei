"""Acesso comum ao `gerenciador.db` (CV8).

Mora em um SQLite próprio (`gerenciador_db_path`), fora do ciclo efêmero do
banco das quadras: nem `RESET_DB_ON_STARTUP` nem a mudança de schema das
quadras apagam este arquivo. Mudanças de schema aqui são migrações aditivas
guiadas por `PRAGMA user_version`. Jogadores, sessão e rodada usam este módulo.
"""

import os
import re
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime

from app.api import ErroDeCampo
from app.config import settings

ROTULOS = {
    "nome": "Nome",
    "genero": "Gênero",
    "nota": "Nota",
    "foto": "Foto",
    "sessao": "Sessão",
    "jogador": "Jogador",
    "jogador_ids": "Ordem",
    "alvo": "Alvo",
    "rodada": "Rodada",
    "quadra": "Quadra",
    "codigo": "Código da quadra",
}

SCHEMA_VERSAO = 11
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS jogadores (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    nome_chave TEXT NOT NULL,
    genero TEXT NOT NULL CHECK (genero IN ('H', 'M')),
    nota INTEGER NOT NULL DEFAULT 60,
    ativo INTEGER NOT NULL DEFAULT 1,
    criado_em TEXT NOT NULL,
    atualizado_em TEXT NOT NULL
);
-- Nome único só entre ativos: inativar libera o nome.
CREATE UNIQUE INDEX IF NOT EXISTS idx_jogadores_nome_ativo
    ON jogadores (nome_chave) WHERE ativo = 1;

CREATE TABLE IF NOT EXISTS jogador_fotos (
    jogador_id TEXT PRIMARY KEY REFERENCES jogadores(id) ON DELETE CASCADE,
    imagem BLOB NOT NULL,
    atualizado_em TEXT NOT NULL
);

-- Sessão do dia (CV8.DS1.US2). O índice por expressão constante garante, no
-- banco, no máximo uma sessão aberta, mesmo com aberturas concorrentes.
CREATE TABLE IF NOT EXISTS sessoes (
    id TEXT PRIMARY KEY,
    aberta_em TEXT NOT NULL,
    encerrada_em TEXT,
    quadra_id TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_sessao_aberta
    ON sessoes ((1)) WHERE encerrada_em IS NULL;

-- Presença e ordem de chegada da sessão (RN-13, RN-15). `ordem` é 1..N.
CREATE TABLE IF NOT EXISTS presencas (
    sessao_id TEXT NOT NULL REFERENCES sessoes(id) ON DELETE CASCADE,
    jogador_id TEXT NOT NULL REFERENCES jogadores(id),
    ordem INTEGER NOT NULL,
    marcado_em TEXT NOT NULL,
    PRIMARY KEY (sessao_id, jogador_id)
);

-- Rodada (CV8.DS2.US3). No máximo uma rodada em proposta ou em andamento por
-- sessão. `tentativa` conta os "resortear" da proposta.
CREATE TABLE IF NOT EXISTS rodadas (
    id TEXT PRIMARY KEY,
    sessao_id TEXT NOT NULL REFERENCES sessoes(id) ON DELETE CASCADE,
    numero INTEGER NOT NULL,
    alvo INTEGER NOT NULL CHECK (alvo BETWEEN 6 AND 25),
    estado TEXT NOT NULL CHECK (estado IN ('proposta', 'em_andamento', 'cancelada', 'encerrada')),
    tentativa INTEGER NOT NULL DEFAULT 0,
    distintas INTEGER NOT NULL DEFAULT 1,
    criado_em TEXT NOT NULL,
    confirmado_em TEXT,
    -- mata-mata (CV8.DS4.US11): quando o operador o iniciou e quem foi campeão
    mata_mata_em TEXT,
    campeao_time_id TEXT REFERENCES times(id),
    -- desfazer a última partida (CV8.DS3.US7): 1 nível só
    desfeito INTEGER NOT NULL DEFAULT 0,
    -- formato do time (CV8.DS6.US15): 'dupla' (2 jogadores) ou 'trio' (3)
    formato TEXT NOT NULL DEFAULT 'dupla' CHECK (formato IN ('dupla', 'trio'))
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_rodada_ativa
    ON rodadas (sessao_id) WHERE estado IN ('proposta', 'em_andamento');

-- Times da rodada na ordem da fila. Guarda a nota e a chegada usadas no
-- sorteio: mudar a nota depois não reescreve a rodada.
CREATE TABLE IF NOT EXISTS times (
    id TEXT PRIMARY KEY,
    rodada_id TEXT NOT NULL REFERENCES rodadas(id) ON DELETE CASCADE,
    fila INTEGER NOT NULL,
    incompleto INTEGER NOT NULL DEFAULT 0,
    -- de onde veio o time incompleto: sobra do sorteio ('impar') ou chegada
    -- no meio da rodada ('atrasado', US9).
    origem TEXT NOT NULL DEFAULT 'impar' CHECK (origem IN ('impar', 'atrasado'))
);
-- Partidas chamadas na quadra do placar (CV8.DS3.US5). O resultado
-- (`placar_*`, `vencedor_time_id`, `encerrada_em`) é preenchido pela US6.
CREATE TABLE IF NOT EXISTS partidas_rodada (
    id TEXT PRIMARY KEY,
    rodada_id TEXT NOT NULL REFERENCES rodadas(id) ON DELETE CASCADE,
    ordem INTEGER NOT NULL,
    time_a_id TEXT NOT NULL REFERENCES times(id),
    time_b_id TEXT NOT NULL REFERENCES times(id),
    estado TEXT NOT NULL CHECK (estado IN ('chamada', 'encerrada')),
    fase TEXT NOT NULL DEFAULT 'fila' CHECK (fase IN ('fila', 'mata_mata')),
    quadra_id TEXT NOT NULL,
    partida_quadra_id TEXT,
    chamada_em TEXT NOT NULL,
    placar_a INTEGER,
    placar_b INTEGER,
    vencedor_time_id TEXT REFERENCES times(id),
    encerrada_em TEXT
);
-- No máximo uma partida chamada (em aberto) por rodada.
CREATE UNIQUE INDEX IF NOT EXISTS idx_partida_chamada
    ON partidas_rodada (rodada_id) WHERE estado = 'chamada';

-- Mudanças da fila no meio da rodada (CV8.DS7.TS3): time que ficou sem
-- jogadores ("remover") ou sem substituto na vez de entrar ("pular").
-- `apos_partidas` é quantas partidas encerradas existiam; ver `conducao.Ajuste`.
CREATE TABLE IF NOT EXISTS ajustes_fila (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rodada_id TEXT NOT NULL REFERENCES rodadas(id) ON DELETE CASCADE,
    apos_partidas INTEGER NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('remover', 'pular')),
    time_id TEXT NOT NULL REFERENCES times(id),
    criado_em TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS time_jogadores (
    time_id TEXT NOT NULL REFERENCES times(id) ON DELETE CASCADE,
    jogador_id TEXT NOT NULL REFERENCES jogadores(id),
    nota INTEGER NOT NULL,
    ordem_chegada INTEGER NOT NULL,
    -- 1 = veio da lista de escalação (joga por um segundo time, RN-07)
    escalado INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (time_id, jogador_id)
);
"""


def agora() -> str:
    return datetime.now(UTC).isoformat()


def erro_de_campo(codigo: int, campo: str, mensagem: str, tipo: str) -> ErroDeCampo:
    rotulo = ROTULOS.get(campo, campo)
    erro = ErroDeCampo(codigo, f"{rotulo} {mensagem}.", campo, mensagem, tipo)
    erro.erros[0]["rotulo"] = rotulo
    return erro


def conectar(caminho: str) -> sqlite3.Connection:
    pasta = os.path.dirname(caminho)
    if pasta:
        os.makedirs(pasta, exist_ok=True)
    conn = sqlite3.connect(caminho, timeout=5.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=5000;")
    # Resultado de partida não pode se perder numa queda de energia (US12): no
    # WAL, `NORMAL` pode perder o último commit; `FULL` o grava antes de responder.
    conn.execute("PRAGMA synchronous=FULL;")
    return conn


@contextmanager
def escrita(conn):
    """Transação que já nasce com a trava de escrita: dois operadores mexendo
    ao mesmo tempo não recebem a mesma posição nem abrem duas rodadas."""
    conn.isolation_level = None
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise


def sessao_aberta(conn):
    return conn.execute("SELECT * FROM sessoes WHERE encerrada_em IS NULL").fetchone()


def exigir_sessao_aberta(conn):
    sessao = sessao_aberta(conn)
    if sessao is None:
        raise erro_de_campo(409, "sessao", "não está aberta", "sem_sessao")
    return sessao


def init_gerenciador_sync(caminho: str | None = None) -> None:
    caminho = caminho or settings.gerenciador_db_path
    conn = conectar(caminho)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.executescript(SCHEMA_SQL)
        # Migração aditiva 1 -> 2: nota 60 para quem já estava na base.
        colunas = [r["name"] for r in conn.execute("PRAGMA table_info(jogadores)")]
        if "nota" not in colunas:
            conn.execute(
                "ALTER TABLE jogadores ADD COLUMN nota INTEGER NOT NULL DEFAULT 60"
            )
        # Migração aditiva 4 -> 5: vínculo da sessão com a quadra do placar.
        colunas_sessao = [r["name"] for r in conn.execute("PRAGMA table_info(sessoes)")]
        if "quadra_id" not in colunas_sessao:
            conn.execute("ALTER TABLE sessoes ADD COLUMN quadra_id TEXT")
        # Migração aditiva 5 -> 6: origem do time incompleto e marca de escalado.
        if "origem" not in [
            r["name"] for r in conn.execute("PRAGMA table_info(times)")
        ]:
            conn.execute(
                "ALTER TABLE times ADD COLUMN origem TEXT NOT NULL DEFAULT 'impar'"
            )
        if "escalado" not in [
            r["name"] for r in conn.execute("PRAGMA table_info(time_jogadores)")
        ]:
            conn.execute(
                "ALTER TABLE time_jogadores ADD COLUMN escalado INTEGER NOT NULL DEFAULT 0"
            )
        # Migração aditiva 6 -> 7: mata-mata e campeão da rodada.
        colunas_rodada = [r["name"] for r in conn.execute("PRAGMA table_info(rodadas)")]
        if "mata_mata_em" not in colunas_rodada:
            conn.execute("ALTER TABLE rodadas ADD COLUMN mata_mata_em TEXT")
            conn.execute("ALTER TABLE rodadas ADD COLUMN campeao_time_id TEXT")
        # Migração aditiva 7 -> 8: marca do desfazer (um nível).
        if "desfeito" not in colunas_rodada:
            conn.execute(
                "ALTER TABLE rodadas ADD COLUMN desfeito INTEGER NOT NULL DEFAULT 0"
            )
        # Migração aditiva 8 -> 9: formato da rodada (dupla ou trio).
        if "formato" not in colunas_rodada:
            conn.execute(
                "ALTER TABLE rodadas ADD COLUMN formato TEXT NOT NULL DEFAULT 'dupla'"
            )
        if "fase" not in [
            r["name"] for r in conn.execute("PRAGMA table_info(partidas_rodada)")
        ]:
            conn.execute(
                "ALTER TABLE partidas_rodada ADD COLUMN fase TEXT NOT NULL DEFAULT 'fila'"
            )
        # Migração 9 -> 10: o alvo da rodada deixa de ser só 10 ou 12 (6 a 25).
        # O SQLite não altera um CHECK: recria a tabela, copiando as linhas.
        _liberar_alvo_da_rodada(conn)
        conn.execute(f"PRAGMA user_version = {SCHEMA_VERSAO}")
        conn.commit()
    finally:
        conn.close()


def _liberar_alvo_da_rodada(conn) -> None:
    antigo = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'rodadas'"
    ).fetchone()
    if antigo is None or "alvo IN (10, 12)" not in antigo["sql"]:
        return
    novo = re.search(
        r"CREATE TABLE IF NOT EXISTS rodadas \(.*?\n\);", SCHEMA_SQL, re.DOTALL
    ).group(0)
    novo = novo.replace("IF NOT EXISTS rodadas (", "rodadas_nova (", 1)
    colunas = ", ".join(
        r["name"]
        for r in conn.execute("PRAGMA table_info(rodadas)")
        if r["name"] != "formato" or "formato" in novo
    )
    conn.isolation_level = None
    conn.execute("BEGIN IMMEDIATE")
    try:
        conn.execute(novo)
        conn.execute(
            f"INSERT INTO rodadas_nova ({colunas}) SELECT {colunas} FROM rodadas"
        )
        conn.execute("DROP TABLE rodadas")
        conn.execute("ALTER TABLE rodadas_nova RENAME TO rodadas")
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_rodada_ativa "
            "ON rodadas (sessao_id) WHERE estado IN ('proposta', 'em_andamento')"
        )
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.isolation_level = ""
