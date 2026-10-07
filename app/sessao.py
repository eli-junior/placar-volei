"""Sessão do dia, presença e ordem de chegada (CV8.DS1.US2).

Vive no mesmo `gerenciador.db` da base de jogadores. Uma sessão aberta por
vez (garantido por índice único parcial). A ordem de chegada é 1..N: marcar
presença entra no fim, desmarcar recompacta e o operador pode reordenar (RN-13,
RN-15). Quem decide quando a ordem trava é o sorteio (US-03).
"""

import asyncio
import sqlite3
import uuid
from contextlib import contextmanager
from typing import Any

from fastapi import APIRouter, Request, status
from pydantic import BaseModel

from app.api import autenticar_owner
from app.config import settings
from app.jogadores import (
    JogadorBody,
    _agora,
    _conectar,
    _erro,
    _linha,
    _obter,
    criar_sync,
    recompactar_presencas,
)

MINIMO_PARA_SORTEAR = 4


@contextmanager
def _escrita(conn):
    """Transação que já nasce com a trava de escrita: dois operadores marcando
    ao mesmo tempo não recebem a mesma posição."""
    conn.isolation_level = None
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise


def _aberta(conn):
    return conn.execute("SELECT * FROM sessoes WHERE encerrada_em IS NULL").fetchone()


def _exigir_aberta(conn):
    sessao = _aberta(conn)
    if sessao is None:
        raise _erro(409, "sessao", "não está aberta", "sem_sessao")
    return sessao


def _estado(conn) -> dict:
    sessao = _aberta(conn)
    if sessao is None:
        return {
            "sessao": None,
            "presentes": [],
            "ausentes": [],
            "minimo": MINIMO_PARA_SORTEAR,
        }
    base = (
        "SELECT j.*, EXISTS(SELECT 1 FROM jogador_fotos f WHERE f.jogador_id = j.id) "
        "AS tem_foto FROM jogadores j"
    )
    presentes = []
    for r in conn.execute(
        f"{base} JOIN presencas p ON p.jogador_id = j.id WHERE p.sessao_id = ? "
        "ORDER BY p.ordem",
        (sessao["id"],),
    ):
        presentes.append(_linha(r))
    for i, p in enumerate(presentes, start=1):
        p["ordem"] = i
    ausentes = [
        _linha(r)
        for r in conn.execute(
            f"{base} WHERE j.ativo = 1 AND j.id NOT IN "
            "(SELECT jogador_id FROM presencas WHERE sessao_id = ?) "
            "ORDER BY j.nome_chave",
            (sessao["id"],),
        )
    ]
    return {
        "sessao": {"id": sessao["id"], "aberta_em": sessao["aberta_em"]},
        "presentes": presentes,
        "ausentes": ausentes,
        "minimo": MINIMO_PARA_SORTEAR,
    }


def _executar(operacao):
    conn = _conectar(settings.gerenciador_db_path)
    try:
        return operacao(conn)
    finally:
        conn.close()


def estado_sync() -> dict:
    return _executar(_estado)


def abrir_sync() -> dict:
    def op(conn):
        try:
            with _escrita(conn):
                conn.execute(
                    "INSERT INTO sessoes (id, aberta_em) VALUES (?, ?)",
                    (uuid.uuid4().hex, _agora()),
                )
        except sqlite3.IntegrityError:
            raise _erro(
                409, "sessao", "já existe uma sessão aberta", "ja_aberta"
            ) from None
        return _estado(conn)

    return _executar(op)


def encerrar_sync() -> dict:
    def op(conn):
        with _escrita(conn):
            sessao = _exigir_aberta(conn)
            conn.execute(
                "UPDATE sessoes SET encerrada_em = ? WHERE id = ?",
                (_agora(), sessao["id"]),
            )
        return _estado(conn)

    return _executar(op)


def _marcar(conn, jogador_id: str) -> None:
    sessao = _exigir_aberta(conn)
    jogador = _obter(conn, jogador_id)
    if not jogador["ativo"]:
        raise _erro(409, "jogador", "está inativo", "inativo")
    ja = conn.execute(
        "SELECT 1 FROM presencas WHERE sessao_id = ? AND jogador_id = ?",
        (sessao["id"], jogador_id),
    ).fetchone()
    if ja:
        return  # idempotente: mantém a posição
    proxima = conn.execute(
        "SELECT COALESCE(MAX(ordem), 0) + 1 FROM presencas WHERE sessao_id = ?",
        (sessao["id"],),
    ).fetchone()[0]
    conn.execute(
        "INSERT INTO presencas (sessao_id, jogador_id, ordem, marcado_em) "
        "VALUES (?, ?, ?, ?)",
        (sessao["id"], jogador_id, proxima, _agora()),
    )


def marcar_sync(jogador_id: str) -> dict:
    def op(conn):
        with _escrita(conn):
            _marcar(conn, jogador_id)
        return _estado(conn)

    return _executar(op)


def desmarcar_sync(jogador_id: str) -> dict:
    def op(conn):
        with _escrita(conn):
            sessao = _exigir_aberta(conn)
            _obter(conn, jogador_id)
            conn.execute(
                "DELETE FROM presencas WHERE sessao_id = ? AND jogador_id = ?",
                (sessao["id"], jogador_id),
            )
            recompactar_presencas(conn, sessao["id"])
        return _estado(conn)

    return _executar(op)


def reordenar_sync(jogador_ids: Any) -> dict:
    def op(conn):
        with _escrita(conn):
            sessao = _exigir_aberta(conn)
            atuais = {
                r["jogador_id"]
                for r in conn.execute(
                    "SELECT jogador_id FROM presencas WHERE sessao_id = ?",
                    (sessao["id"],),
                )
            }
            if (
                not isinstance(jogador_ids, list)
                or not all(isinstance(i, str) for i in jogador_ids)
                or len(set(jogador_ids)) != len(jogador_ids)
                or set(jogador_ids) != atuais
            ):
                raise _erro(
                    422,
                    "jogador_ids",
                    "deve listar exatamente os jogadores presentes, sem repetir",
                    "ordem_invalida",
                )
            for ordem, jogador_id in enumerate(jogador_ids, start=1):
                conn.execute(
                    "UPDATE presencas SET ordem = ? WHERE sessao_id = ? AND jogador_id = ?",
                    (ordem, sessao["id"], jogador_id),
                )
        return _estado(conn)

    return _executar(op)


def rapido_sync(nome, genero, nota) -> dict:
    # Confere a sessão antes de criar, para não deixar jogador órfão.
    _executar(lambda conn: _exigir_aberta(conn))
    jogador = criar_sync(nome, genero, nota)
    estado = marcar_sync(jogador["id"])
    return {"jogador": jogador, **estado}


class OrdemBody(BaseModel):
    jogador_ids: Any = None


router = APIRouter(prefix="/api/sessao", tags=["sessao"])


@router.get("")
async def get_sessao(request: Request):
    autenticar_owner(request)
    return await asyncio.to_thread(estado_sync)


@router.post("", status_code=status.HTTP_201_CREATED)
async def post_abrir(request: Request):
    autenticar_owner(request)
    return await asyncio.to_thread(abrir_sync)


@router.post("/encerrar")
async def post_encerrar(request: Request):
    autenticar_owner(request)
    return await asyncio.to_thread(encerrar_sync)


@router.put("/presencas/{jogador_id}")
async def put_presenca(jogador_id: str, request: Request):
    autenticar_owner(request)
    return await asyncio.to_thread(marcar_sync, jogador_id)


@router.delete("/presencas/{jogador_id}")
async def delete_presenca(jogador_id: str, request: Request):
    autenticar_owner(request)
    return await asyncio.to_thread(desmarcar_sync, jogador_id)


@router.put("/ordem")
async def put_ordem(body: OrdemBody, request: Request):
    autenticar_owner(request)
    return await asyncio.to_thread(reordenar_sync, body.jogador_ids)


@router.post("/presencas/rapido", status_code=status.HTTP_201_CREATED)
async def post_rapido(body: JogadorBody, request: Request):
    autenticar_owner(request)
    return await asyncio.to_thread(rapido_sync, body.nome, body.genero, body.nota)
