"""Base persistente de jogadores (CV8.DS1.US1).

Mora em um SQLite próprio (`gerenciador_db_path`), fora do ciclo efêmero do
banco das quadras: nem `RESET_DB_ON_STARTUP` nem a mudança de schema das
quadras apagam este arquivo. Mudanças de schema aqui são migrações aditivas
guiadas por `PRAGMA user_version`.
"""

import asyncio
import hashlib
import os
import sqlite3
import unicodedata
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Request, Response, status
from pydantic import BaseModel

from app.api import ErroDeCampo, autenticar_owner
from app.config import settings

NOME_MAXIMO = 40
GENEROS = ("H", "M")
NOTA_PADRAO = 60
FOTO_MAXIMA = 256 * 1024
_ROTULOS = {"nome": "Nome", "genero": "Gênero", "nota": "Nota", "foto": "Foto"}

SCHEMA_VERSAO = 2
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
    if len(nome.split()) < 2:
        raise _erro(422, "nome", "deve ter nome e sobrenome", "sobrenome")
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


def _nota_valida(bruta: Any, padrao: int | None = NOTA_PADRAO) -> int:
    if bruta is None or bruta == "":
        if padrao is None:
            raise _erro(422, "nota", "é obrigatória", "missing")
        return padrao
    # bool é int em Python; 7.5 e "abc" não valem. 8.0 vindo do JSON vale como 8.
    if isinstance(bruta, bool) or not isinstance(bruta, int | float):
        raise _erro(422, "nota", "deve ser um número de 1 a 100", "int_type")
    if isinstance(bruta, float) and not bruta.is_integer():
        raise _erro(422, "nota", "deve ser um número inteiro de 1 a 100", "int_type")
    nota = int(bruta)
    if not 1 <= nota <= 100:
        raise _erro(422, "nota", "deve ser de 1 a 100", "range")
    return nota


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
        # Migração aditiva 1 -> 2: nota 60 para quem já estava na base.
        colunas = [r["name"] for r in conn.execute("PRAGMA table_info(jogadores)")]
        if "nota" not in colunas:
            conn.execute(
                "ALTER TABLE jogadores ADD COLUMN nota INTEGER NOT NULL DEFAULT 60"
            )
        conn.execute(f"PRAGMA user_version = {SCHEMA_VERSAO}")
        conn.commit()
    finally:
        conn.close()


def _linha(r: sqlite3.Row) -> dict:
    return {
        "id": r["id"],
        "nome": r["nome"],
        "genero": r["genero"],
        "nota": r["nota"],
        "tem_foto": bool(r["tem_foto"]),
        "ativo": bool(r["ativo"]),
    }


_SELECT = (
    "SELECT j.*, EXISTS(SELECT 1 FROM jogador_fotos f WHERE f.jogador_id = j.id) "
    "AS tem_foto FROM jogadores j"
)


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
        filtro = "" if incluir_inativos else "WHERE j.ativo = 1"
        rows = conn.execute(
            f"{_SELECT} {filtro} ORDER BY ativo DESC, nome_chave"
        ).fetchall()
        return [_linha(r) for r in rows]
    finally:
        conn.close()


def _obter(conn, jogador_id: str) -> sqlite3.Row:
    r = conn.execute(f"{_SELECT} WHERE j.id = ?", (jogador_id,)).fetchone()
    if r is None:
        raise _erro(404, "jogador", "não encontrado", "not_found")
    return r


def criar_sync(nome: str | None, genero: str | None, nota: Any = None) -> dict:
    nome, genero, nota = _nome_valido(nome), _genero_valido(genero), _nota_valida(nota)
    chave = chave_do_nome(nome)
    conn = _conectar(settings.gerenciador_db_path)
    try:
        if _em_uso(conn, chave):
            raise _recusar_nome_em_uso(nome)
        jogador_id, agora = uuid.uuid4().hex, _agora()
        try:
            with conn:
                conn.execute(
                    "INSERT INTO jogadores (id, nome, nome_chave, genero, nota, ativo, "
                    "criado_em, atualizado_em) VALUES (?, ?, ?, ?, ?, 1, ?, ?)",
                    (jogador_id, nome, chave, genero, nota, agora, agora),
                )
        except sqlite3.IntegrityError:
            raise _recusar_nome_em_uso(nome) from None
        return _linha(_obter(conn, jogador_id))
    finally:
        conn.close()


def editar_sync(
    jogador_id: str, nome: str | None, genero: str | None, nota: Any = None
) -> dict:
    nome, genero = _nome_valido(nome), _genero_valido(genero)
    chave = chave_do_nome(nome)
    conn = _conectar(settings.gerenciador_db_path)
    try:
        atual = _obter(conn, jogador_id)
        # Nota omitida na edição mantém a atual.
        nota = _nota_valida(nota, padrao=atual["nota"])
        if atual["ativo"] and _em_uso(conn, chave, jogador_id):
            raise _recusar_nome_em_uso(nome)
        try:
            with conn:
                conn.execute(
                    "UPDATE jogadores SET nome = ?, nome_chave = ?, genero = ?, nota = ?, "
                    "atualizado_em = ? WHERE id = ?",
                    (nome, chave, genero, nota, _agora(), jogador_id),
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


def salvar_foto_sync(jogador_id: str, imagem: bytes) -> dict:
    if not imagem.startswith(b"\xff\xd8\xff"):
        raise _erro(422, "foto", "deve ser uma imagem JPEG", "formato")
    if len(imagem) > FOTO_MAXIMA:
        raise _erro(
            413, "foto", f"deve ter no máximo {FOTO_MAXIMA // 1024} KB", "tamanho"
        )
    conn = _conectar(settings.gerenciador_db_path)
    try:
        _obter(conn, jogador_id)
        with conn:
            conn.execute(
                "INSERT INTO jogador_fotos (jogador_id, imagem, atualizado_em) "
                "VALUES (?, ?, ?) ON CONFLICT(jogador_id) DO UPDATE SET "
                "imagem = excluded.imagem, atualizado_em = excluded.atualizado_em",
                (jogador_id, imagem, _agora()),
            )
        return _linha(_obter(conn, jogador_id))
    finally:
        conn.close()


def remover_foto_sync(jogador_id: str) -> dict:
    conn = _conectar(settings.gerenciador_db_path)
    try:
        _obter(conn, jogador_id)
        with conn:
            conn.execute(
                "DELETE FROM jogador_fotos WHERE jogador_id = ?", (jogador_id,)
            )
        return _linha(_obter(conn, jogador_id))
    finally:
        conn.close()


def obter_foto_sync(jogador_id: str) -> tuple[bytes, str] | None:
    conn = _conectar(settings.gerenciador_db_path)
    try:
        r = conn.execute(
            "SELECT imagem, atualizado_em FROM jogador_fotos WHERE jogador_id = ?",
            (jogador_id,),
        ).fetchone()
        return (bytes(r["imagem"]), r["atualizado_em"]) if r else None
    finally:
        conn.close()


class JogadorBody(BaseModel):
    nome: str | None = None
    genero: str | None = None
    nota: Any = None


router = APIRouter(prefix="/api/jogadores", tags=["jogadores"])


@router.get("")
async def get_jogadores(request: Request, incluir_inativos: bool = False):
    autenticar_owner(request)
    return {"jogadores": await asyncio.to_thread(listar_sync, incluir_inativos)}


@router.post("", status_code=status.HTTP_201_CREATED)
async def post_jogador(body: JogadorBody, request: Request):
    autenticar_owner(request)
    return await asyncio.to_thread(criar_sync, body.nome, body.genero, body.nota)


@router.patch("/{jogador_id}")
async def patch_jogador(jogador_id: str, body: JogadorBody, request: Request):
    autenticar_owner(request)
    return await asyncio.to_thread(
        editar_sync, jogador_id, body.nome, body.genero, body.nota
    )


@router.post("/{jogador_id}/inativar")
async def post_inativar(jogador_id: str, request: Request):
    autenticar_owner(request)
    return await asyncio.to_thread(definir_ativo_sync, jogador_id, False)


@router.post("/{jogador_id}/reativar")
async def post_reativar(jogador_id: str, request: Request):
    autenticar_owner(request)
    return await asyncio.to_thread(definir_ativo_sync, jogador_id, True)


@router.put("/{jogador_id}/foto")
async def put_foto(jogador_id: str, request: Request):
    autenticar_owner(request)
    # Recusa antes de ler o corpo inteiro quando o tamanho já é anunciado.
    anunciado = request.headers.get("content-length", "0")
    if anunciado.isdigit() and int(anunciado) > FOTO_MAXIMA:
        raise _erro(
            413, "foto", f"deve ter no máximo {FOTO_MAXIMA // 1024} KB", "tamanho"
        )
    imagem = await request.body()
    return await asyncio.to_thread(salvar_foto_sync, jogador_id, imagem)


@router.get("/{jogador_id}/foto")
async def get_foto(jogador_id: str, request: Request):
    autenticar_owner(request)
    achada = await asyncio.to_thread(obter_foto_sync, jogador_id)
    if achada is None:
        raise _erro(404, "foto", "não encontrada", "not_found")
    imagem, versao = achada
    etag = '"' + hashlib.sha256(versao.encode()).hexdigest()[:16] + '"'
    cabecalhos = {"ETag": etag, "Cache-Control": "private, no-cache"}
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers=cabecalhos)
    return Response(content=imagem, media_type="image/jpeg", headers=cabecalhos)


@router.delete("/{jogador_id}/foto")
async def delete_foto(jogador_id: str, request: Request):
    autenticar_owner(request)
    return await asyncio.to_thread(remover_foto_sync, jogador_id)
