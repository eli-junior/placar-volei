"""Rotas e operações da rodada (CV8.DS2.US3, DS3.US5/US6), num lugar só.

A rodada sempre sai junto do estado da sessão: cada operação devolve o estado
novo (que também é publicado aos outros aparelhos). As regras estão em
`app.rodada`; a ponte com o placar, em `app.ponte`.
"""

from typing import Any

from fastapi import APIRouter, Request, status
from pydantic import BaseModel

from app import rodada as regras_rodada
from app.api import autenticar_owner
from app.gerenciador_db import escrita
from app.ponte import chamar_partida, encerrar_partida
from app.sessao import _estado, _executar, _responder
from app.sincronia import publicar


def _rodada_op(acao):
    def op(conn):
        with escrita(conn):
            acao(conn)
        return _estado(conn)

    return _executar(op)


def sortear_sync(alvo: Any) -> dict:
    return _rodada_op(lambda conn: regras_rodada.criar_proposta(conn, alvo))


def resortear_sync(alvo: Any = None) -> dict:
    return _rodada_op(lambda conn: regras_rodada.resortear(conn, alvo))


def confirmar_sync() -> dict:
    return _rodada_op(regras_rodada.confirmar)


def descartar_sync() -> dict:
    return _rodada_op(regras_rodada.descartar)


def cancelar_sync() -> dict:
    return _rodada_op(regras_rodada.cancelar)


class AlvoBody(BaseModel):
    alvo: Any = None


router = APIRouter(prefix="/api/rodada", tags=["rodada"])


@router.post("/sorteio", status_code=status.HTTP_201_CREATED)
async def post_sorteio(body: AlvoBody, request: Request):
    autenticar_owner(request)
    return await _responder(sortear_sync, body.alvo)


@router.post("/resortear")
async def post_resortear(body: AlvoBody, request: Request):
    autenticar_owner(request)
    return await _responder(resortear_sync, body.alvo)


@router.post("/confirmar")
async def post_confirmar(request: Request):
    autenticar_owner(request)
    return await _responder(confirmar_sync)


@router.post("/descartar")
async def post_descartar(request: Request):
    autenticar_owner(request)
    return await _responder(descartar_sync)


@router.post("/cancelar")
async def post_cancelar(request: Request):
    autenticar_owner(request)
    return await _responder(cancelar_sync)


@router.post("/chamar-partida", status_code=status.HTTP_201_CREATED)
async def post_chamar_partida(request: Request):
    autenticar_owner(request)
    estado = await chamar_partida()
    await publicar(estado)
    return estado


@router.post("/encerrar-partida")
async def post_encerrar_partida(request: Request):
    autenticar_owner(request)
    estado = await encerrar_partida()
    await publicar(estado)
    return estado
