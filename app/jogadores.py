"""Base persistente de jogadores (CV8.DS1.US1).

Mora em um SQLite próprio (`gerenciador_db_path`), fora do ciclo efêmero do
banco das quadras: nem `RESET_DB_ON_STARTUP` nem a mudança de schema das
quadras apagam este arquivo. Mudanças de schema aqui são migrações aditivas
guiadas por `PRAGMA user_version`.
"""

import asyncio
import os
import sqlite3
import unicodedata
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Request, status
from pydantic import BaseModel

from app.api import ErroDeCampo, autenticar_owner
from app.config import settings

NOME_MAXIMO = 40
GENEROS = ("H", "M")
_ROTULOS = {"nome": "Nome", "genero": "Gênero"}

SCHEMA_VERSAO = 1
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS jogadores (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    nome_chave TEXT NOT NULL,
    genero TEXT NOT NULL CHECK (genero IN ('H', 'M')),
    ativo INTEGER NOT NULL DEFAULT 1,
    criado_em TEXT NOT NULL,
    atualizado_em TEXT NOT NULL
);
-- Nome único só entre ativos: inativar libera o nome.
CREATE UNIQUE INDEX IF NOT EXISTS idx_jogadores_nome_ativo
    ON jogadores (nome_chave) WHERE ativo = 1;
"""


def chave_do_nome(nome: str) -> str:
    """Compara nomes sem diferenciar caixa nem acentos (`João` = `joao`)."""
    decomposto = unicodedata.normalize("NFKD", nome.strip())
    sem_acento = "".join(c for c in decomposto if not unicodedata.combining(c))
    return " ".join(sem_acento.casefold().split())


def _erro(codigo: int, campo: str, mensagem: str, tipo: str) -> ErroDeCampo:
    rotulo = _ROTULOS.get(campo, campo)
    erro = ErroDeCampo(codigo, f"{rotulo} {mensagem}.", campo, mensagem, tipo)
    erro.erros[0]["rotulo"] = rotulo
    return erro


def _nome_valido(bruto: str | None) -> str:
    nome = " ".join((bruto or "").split())
    if not nome:
        raise _erro(422, "nome", "é obrigatório", "missing")
    if len(nome) > NOME_MAXIMO:
        raise _erro(
            422, "nome", f"deve ter no máximo {NOME_MAXIMO} caracteres", "too_long"
        )
    return nome


def _genero_valido(bruto: str | None) -> str:
    genero = (bruto or "").strip().upper()
    if genero not in GENEROS:
        raise _erro(422, "genero", "é obrigatório (H ou M)", "missing")
    return genero


def _conectar(caminho: str) -> sqlite3.Connection:
    pasta = os.path.dirname(caminho)
    if pasta:
        os.makedirs(pasta, exist_ok=True)
    conn = sqlite3.connect(caminho, timeout=5.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=5000;")
    return conn


def init_jogadores_sync(caminho: str | None = None) -> None:
    caminho = caminho or settings.gerenciador_db_path
    conn = _conectar(caminho)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.executescript(SCHEMA_SQL)
        conn.execute(f"PRAGMA user_version = {SCHEMA_VERSAO}")
        conn.commit()
    finally:
        conn.close()


def _linha(r: sqlite3.Row) -> dict:
    return {
        "id": r["id"],
        "nome": r["nome"],
        "genero": r["genero"],
        "ativo": bool(r["ativo"]),
    }


def _agora() -> str:
    return datetime.now(UTC).isoformat()


def _em_uso(conn, chave: str, ignorar_id: str | None = None) -> bool:
    r = conn.execute(
        "SELECT 1 FROM jogadores WHERE ativo = 1 AND nome_chave = ? AND id != ?",
        (chave, ignorar_id or ""),
    ).fetchone()
    return r is not None


def _recusar_nome_em_uso(nome: str) -> ErroDeCampo:
    return _erro(
        409, "nome", f'"{nome}" já está em uso por outro jogador ativo', "duplicate"
    )


def listar_sync(incluir_inativos: bool = False) -> list[dict]:
    conn = _conectar(settings.gerenciador_db_path)
    try:
        filtro = "" if incluir_inativos else "WHERE ativo = 1"
        rows = conn.execute(
            f"SELECT * FROM jogadores {filtro} ORDER BY ativo DESC, nome_chave"
        ).fetchall()
        return [_linha(r) for r in rows]
    finally:
        conn.close()


def _obter(conn, jogador_id: str) -> sqlite3.Row:
    r = conn.execute("SELECT * FROM jogadores WHERE id = ?", (jogador_id,)).fetchone()
    if r is None:
        raise _erro(404, "jogador", "não encontrado", "not_found")
    return r


def criar_sync(nome: str | None, genero: str | None) -> dict:
    nome, genero = _nome_valido(nome), _genero_valido(genero)
    chave = chave_do_nome(nome)
    conn = _conectar(settings.gerenciador_db_path)
    try:
        if _em_uso(conn, chave):
            raise _recusar_nome_em_uso(nome)
        jogador_id, agora = uuid.uuid4().hex, _agora()
        try:
            with conn:
                conn.execute(
                    "INSERT INTO jogadores VALUES (?, ?, ?, ?, 1, ?, ?)",
                    (jogador_id, nome, chave, genero, agora, agora),
                )
        except sqlite3.IntegrityError:
            raise _recusar_nome_em_uso(nome) from None
        return _linha(_obter(conn, jogador_id))
    finally:
        conn.close()


def editar_sync(jogador_id: str, nome: str | None, genero: str | None) -> dict:
    nome, genero = _nome_valido(nome), _genero_valido(genero)
    chave = chave_do_nome(nome)
    conn = _conectar(settings.gerenciador_db_path)
    try:
        atual = _obter(conn, jogador_id)
        if atual["ativo"] and _em_uso(conn, chave, jogador_id):
            raise _recusar_nome_em_uso(nome)
        try:
            with conn:
                conn.execute(
                    "UPDATE jogadores SET nome = ?, nome_chave = ?, genero = ?, "
                    "atualizado_em = ? WHERE id = ?",
                    (nome, chave, genero, _agora(), jogador_id),
                )
        except sqlite3.IntegrityError:
            raise _recusar_nome_em_uso(nome) from None
        return _linha(_obter(conn, jogador_id))
    finally:
        conn.close()


def definir_ativo_sync(jogador_id: str, ativo: bool) -> dict:
    conn = _conectar(settings.gerenciador_db_path)
    try:
        atual = _obter(conn, jogador_id)
        if (
            ativo
            and not atual["ativo"]
            and _em_uso(conn, atual["nome_chave"], jogador_id)
        ):
            raise _recusar_nome_em_uso(atual["nome"])
        try:
            with conn:
                conn.execute(
                    "UPDATE jogadores SET ativo = ?, atualizado_em = ? WHERE id = ?",
                    (int(ativo), _agora(), jogador_id),
                )
        except sqlite3.IntegrityError:
            raise _recusar_nome_em_uso(atual["nome"]) from None
        return _linha(_obter(conn, jogador_id))
    finally:
        conn.close()


class JogadorBody(BaseModel):
    nome: str | None = None
    genero: str | None = None


router = APIRouter(prefix="/api/jogadores", tags=["jogadores"])


@router.get("")
async def get_jogadores(request: Request, incluir_inativos: bool = False):
    autenticar_owner(request)
    return {"jogadores": await asyncio.to_thread(listar_sync, incluir_inativos)}


@router.post("", status_code=status.HTTP_201_CREATED)
async def post_jogador(body: JogadorBody, request: Request):
    autenticar_owner(request)
    return await asyncio.to_thread(criar_sync, body.nome, body.genero)


@router.patch("/{jogador_id}")
async def patch_jogador(jogador_id: str, body: JogadorBody, request: Request):
    autenticar_owner(request)
    return await asyncio.to_thread(editar_sync, jogador_id, body.nome, body.genero)


@router.post("/{jogador_id}/inativar")
async def post_inativar(jogador_id: str, request: Request):
    autenticar_owner(request)
    return await asyncio.to_thread(definir_ativo_sync, jogador_id, False)


@router.post("/{jogador_id}/reativar")
async def post_reativar(jogador_id: str, request: Request):
    autenticar_owner(request)
    return await asyncio.to_thread(definir_ativo_sync, jogador_id, True)
