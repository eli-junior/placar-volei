"""Sessão do dia, presença e ordem de chegada (CV8.DS1.US2).

Vive no mesmo `gerenciador.db` da base de jogadores. Uma sessão aberta por
vez (garantido por índice único parcial). A ordem de chegada é 1..N: marcar
presença entra no fim, desmarcar recompacta e o operador pode reordenar (RN-13,
RN-15). Quem decide quando a ordem trava é o sorteio (US-03).
"""

import asyncio
import sqlite3
import uuid
from typing import Any

from fastapi import APIRouter, Request, status
from pydantic import BaseModel

from app import rodada as regras_rodada
from app.api import autenticar_owner
from app.config import settings
from app.gerenciador_db import (
    agora,
    conectar,
    erro_de_campo,
    escrita,
    exigir_sessao_aberta,
    sessao_aberta,
)
from app.jogadores import (
    JogadorBody,
    criar_sync,
    jogador_json,
    obter_jogador,
    recompactar_presencas,
)
from app.ponte import info_quadra
from app.sincronia import publicar

MINIMO_PARA_SORTEAR = 4


def _estado(conn) -> dict:
    sessao = sessao_aberta(conn)
    if sessao is None:
        return {
            "sessao": None,
            "presentes": [],
            "ausentes": [],
            "minimo": MINIMO_PARA_SORTEAR,
            "rodada": None,
            "quadra": None,
            "conducao": None,
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
        presentes.append(jogador_json(r))
    for i, p in enumerate(presentes, start=1):
        p["ordem"] = i
    ausentes = [
        jogador_json(r)
        for r in conn.execute(
            f"{base} WHERE j.ativo = 1 AND j.id NOT IN "
            "(SELECT jogador_id FROM presencas WHERE sessao_id = ?) "
            "ORDER BY j.nome_chave",
            (sessao["id"],),
        )
    ]
    rodada = regras_rodada.montar(conn, sessao["id"])
    quadra = info_quadra(sessao["quadra_id"])
    conducao = (
        regras_rodada.montar_conducao(conn, rodada, quadra)
        if rodada and rodada["estado"] == "em_andamento"
        else None
    )
    return {
        "sessao": {"id": sessao["id"], "aberta_em": sessao["aberta_em"]},
        "presentes": presentes,
        "ausentes": ausentes,
        "minimo": MINIMO_PARA_SORTEAR,
        "rodada": rodada,
        "quadra": quadra,
        "conducao": conducao,
    }


def _executar(operacao):
    conn = conectar(settings.gerenciador_db_path)
    try:
        return operacao(conn)
    finally:
        conn.close()


def estado_sync() -> dict:
    return _executar(_estado)


def abrir_sync() -> dict:
    def op(conn):
        try:
            with escrita(conn):
                conn.execute(
                    "INSERT INTO sessoes (id, aberta_em) VALUES (?, ?)",
                    (uuid.uuid4().hex, agora()),
                )
        except sqlite3.IntegrityError:
            raise erro_de_campo(
                409, "sessao", "já existe uma sessão aberta", "ja_aberta"
            ) from None
        return _estado(conn)

    return _executar(op)


def encerrar_sync() -> dict:
    def op(conn):
        with escrita(conn):
            sessao = exigir_sessao_aberta(conn)
            if regras_rodada.rodada_ativa(conn, sessao["id"]):
                raise erro_de_campo(
                    409,
                    "rodada",
                    "ativa: descarte a proposta ou cancele a rodada antes de encerrar a sessão",
                    "rodada_ativa",
                )
            conn.execute(
                "UPDATE sessoes SET encerrada_em = ? WHERE id = ?",
                (agora(), sessao["id"]),
            )
        return _estado(conn)

    return _executar(op)


def _marcar(conn, jogador_id: str) -> None:
    sessao = exigir_sessao_aberta(conn)
    regras_rodada.exigir_sem_rodada_ativa(conn, sessao["id"])
    jogador = obter_jogador(conn, jogador_id)
    if not jogador["ativo"]:
        raise erro_de_campo(409, "jogador", "está inativo", "inativo")
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
        (sessao["id"], jogador_id, proxima, agora()),
    )


def marcar_sync(jogador_id: str) -> dict:
    def op(conn):
        with escrita(conn):
            _marcar(conn, jogador_id)
        return _estado(conn)

    return _executar(op)


def desmarcar_sync(jogador_id: str) -> dict:
    def op(conn):
        with escrita(conn):
            sessao = exigir_sessao_aberta(conn)
            regras_rodada.exigir_sem_rodada_ativa(conn, sessao["id"])
            obter_jogador(conn, jogador_id)
            conn.execute(
                "DELETE FROM presencas WHERE sessao_id = ? AND jogador_id = ?",
                (sessao["id"], jogador_id),
            )
            recompactar_presencas(conn, sessao["id"])
        return _estado(conn)

    return _executar(op)


def reordenar_sync(jogador_ids: Any) -> dict:
    def op(conn):
        with escrita(conn):
            sessao = exigir_sessao_aberta(conn)
            regras_rodada.exigir_sem_rodada_ativa(conn, sessao["id"])
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
                raise erro_de_campo(
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
    def conferir(conn):
        sessao = exigir_sessao_aberta(conn)
        regras_rodada.exigir_sem_rodada_ativa(conn, sessao["id"])

    _executar(conferir)
    jogador = criar_sync(nome, genero, nota)
    estado = marcar_sync(jogador["id"])
    return {"jogador": jogador, **estado}


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


class OrdemBody(BaseModel):
    jogador_ids: Any = None


async def _responder(funcao, *args) -> dict:
    """Executa a ação, publica o estado novo aos outros aparelhos e o devolve."""
    resultado = await asyncio.to_thread(funcao, *args)
    await publicar({k: v for k, v in resultado.items() if k != "jogador"})
    return resultado


router = APIRouter(prefix="/api/sessao", tags=["sessao"])


@router.get("")
async def get_sessao(request: Request):
    autenticar_owner(request)
    return await asyncio.to_thread(estado_sync)


@router.post("", status_code=status.HTTP_201_CREATED)
async def post_abrir(request: Request):
    autenticar_owner(request)
    return await _responder(abrir_sync)


@router.post("/encerrar")
async def post_encerrar(request: Request):
    autenticar_owner(request)
    return await _responder(encerrar_sync)


@router.put("/presencas/{jogador_id}")
async def put_presenca(jogador_id: str, request: Request):
    autenticar_owner(request)
    return await _responder(marcar_sync, jogador_id)


@router.delete("/presencas/{jogador_id}")
async def delete_presenca(jogador_id: str, request: Request):
    autenticar_owner(request)
    return await _responder(desmarcar_sync, jogador_id)


@router.put("/ordem")
async def put_ordem(body: OrdemBody, request: Request):
    autenticar_owner(request)
    return await _responder(reordenar_sync, body.jogador_ids)


@router.post("/presencas/rapido", status_code=status.HTTP_201_CREATED)
async def post_rapido(body: JogadorBody, request: Request):
    autenticar_owner(request)
    return await _responder(rapido_sync, body.nome, body.genero, body.nota)


router_rodada = APIRouter(prefix="/api/rodada", tags=["rodada"])


@router_rodada.post("/sorteio", status_code=status.HTTP_201_CREATED)
async def post_sorteio(body: AlvoBody, request: Request):
    autenticar_owner(request)
    return await _responder(sortear_sync, body.alvo)


@router_rodada.post("/resortear")
async def post_resortear(body: AlvoBody, request: Request):
    autenticar_owner(request)
    return await _responder(resortear_sync, body.alvo)


@router_rodada.post("/confirmar")
async def post_confirmar(request: Request):
    autenticar_owner(request)
    return await _responder(confirmar_sync)


@router_rodada.post("/descartar")
async def post_descartar(request: Request):
    autenticar_owner(request)
    return await _responder(descartar_sync)


@router_rodada.post("/cancelar")
async def post_cancelar(request: Request):
    autenticar_owner(request)
    return await _responder(cancelar_sync)
