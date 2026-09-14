import asyncio
import uuid
from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel, Field

from app.comandos import executar_sync
from app.config import settings
from app.eventos import carregar_eventos, get_quadra_lock
from app.hub import hub
from app.identidade import SESSION_COOKIE
from app.projecao import projetar_estado, projetar_linha_do_tempo
from app.quadras import (
    criar_arena,
    criar_quadra,
    listar_arenas,
    listar_participantes,
    listar_quadras,
    obter_arena,
    obter_participante,
    obter_quadra,
    registrar_participante,
)

router = APIRouter(prefix="/api", tags=["arenas_e_quadras"])


class CriarArenaBody(BaseModel):
    nome: str = Field(..., min_length=1, max_length=50)


class MarcarPontoBody(BaseModel):
    equipe: str = Field(..., description="Equipe que marcou ponto: 'A' ou 'B'")


class CriarQuadraBody(BaseModel):
    apelido: str | None = Field(default=None, max_length=30)
    nome: str | None = Field(default=None, max_length=50)
    arena_id: str | None = None


class EntrarQuadraBody(BaseModel):
    apelido: str = Field(..., min_length=1, max_length=30)


def extrair_ou_gerar_session_id(request: Request) -> tuple[str, bool]:
    session_id = request.headers.get("x-session-id") or request.cookies.get(
        SESSION_COOKIE
    )
    if session_id:
        return session_id, False
    return str(uuid.uuid4()), True


# --- ROTAS DE ARENAS ---


@router.get("/arenas")
async def get_arenas():
    arenas = await listar_arenas(settings.db_path)
    return {"arenas": arenas}


@router.post("/arenas", status_code=status.HTTP_201_CREATED)
async def post_arenas(body: CriarArenaBody):
    nome = body.nome.strip()
    if not nome:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Nome da arena não pode ser vazio.",
        )
    try:
        arena = await criar_arena(settings.db_path, nome)
    except OSError:
        raise HTTPException(
            503, "Não foi possível salvar a configuração. Tente novamente."
        ) from None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return arena


@router.get("/arenas/{arena_id}")
async def get_arena(arena_id: str):
    arena = await obter_arena(settings.db_path, arena_id)
    if not arena:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arena não encontrada.",
        )
    return arena


@router.get("/arenas/{arena_id}/quadras")
async def get_arena_quadras(arena_id: str):
    arena = await obter_arena(settings.db_path, arena_id)
    if not arena:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arena não encontrada.",
        )
    quadras = await listar_quadras(settings.db_path, arena_id=arena_id)
    return {"arena": arena, "quadras": quadras}


@router.post("/arenas/{arena_id}/quadras", status_code=status.HTTP_201_CREATED)
async def post_arena_quadra(arena_id: str, body: CriarQuadraBody):
    arena = await obter_arena(settings.db_path, arena_id)
    if not arena:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arena não encontrada.",
        )
    nome = (
        body.nome.strip()
        if body.nome and body.nome.strip()
        else f"Quadra {arena_id[:4]}"
    )
    try:
        quadra = await criar_quadra(settings.db_path, arena_id=arena_id, nome=nome)
    except OSError:
        raise HTTPException(
            503, "Não foi possível salvar a configuração. Tente novamente."
        ) from None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return quadra


# --- ROTAS DE QUADRAS E PARTICIPANTES ---


@router.get("/quadras")
async def get_quadras(arena_id: str | None = None):
    quadras = await listar_quadras(settings.db_path, arena_id=arena_id)
    return {"quadras": quadras}


@router.post("/quadras", status_code=status.HTTP_201_CREATED)
async def post_quadras(
    body: CriarQuadraBody,
    request: Request,
    response: Response,
):
    apelido = body.apelido.strip() if body.apelido and body.apelido.strip() else None
    nome = body.nome.strip() if body.nome and body.nome.strip() else None

    session_id = None
    if apelido:
        session_id, is_new = extrair_ou_gerar_session_id(request)
        if is_new:
            response.set_cookie(
                key=SESSION_COOKIE,
                value=session_id,
                httponly=True,
                samesite="lax",
                path="/",
                max_age=86400 * 30,
            )

    try:
        quadra = await criar_quadra(
            settings.db_path,
            arena_id=body.arena_id,
            nome=nome,
            session_id=session_id,
            apelido=apelido,
        )
    except OSError:
        raise HTTPException(
            503, "Não foi possível salvar a configuração. Tente novamente."
        ) from None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return quadra


@router.get("/quadras/{quadra_id}")
async def get_quadra(quadra_id: str):
    quadra = await obter_quadra(settings.db_path, quadra_id)
    if not quadra:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quadra não encontrada.",
        )
    return quadra


@router.post("/quadras/{quadra_id}/entrar")
async def post_entrar_quadra(
    quadra_id: str,
    body: EntrarQuadraBody,
    request: Request,
    response: Response,
):
    quadra = await obter_quadra(settings.db_path, quadra_id)
    if not quadra:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quadra não encontrada.",
        )

    apelido = body.apelido.strip()
    if not apelido:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Apelido não pode ser vazio.",
        )

    session_id, is_new = extrair_ou_gerar_session_id(request)
    if is_new:
        response.set_cookie(
            key=SESSION_COOKIE,
            value=session_id,
            httponly=True,
            samesite="lax",
            path="/",
            max_age=86400 * 30,
        )

    try:
        participante = await registrar_participante(
            settings.db_path,
            quadra_id=quadra_id,
            session_id=session_id,
            apelido=apelido,
        )
    except OSError:
        raise HTTPException(
            503, "Não foi possível salvar a configuração. Tente novamente."
        ) from None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Notifica outros participantes da presença atualizada
    participantes = await listar_participantes(settings.db_path, quadra_id)
    online_set = await hub.participantes_online(quadra_id)
    for p in participantes:
        p["online"] = p["id"] in online_set or p["id"] == participante["id"]

    await hub.broadcast(
        quadra_id,
        {
            "tipo": "PRESENCA_ATUALIZADA",
            "payload": {"participantes": participantes},
        },
    )

    return {
        "participante": participante,
        "quadra": quadra,
    }


@router.get("/quadras/{quadra_id}/eu")
async def get_eu(quadra_id: str, request: Request):
    session_id = request.headers.get("x-session-id") or request.cookies.get(
        SESSION_COOKIE
    )
    if not session_id:
        return {"participante": None, "quadra": None}

    quadra = await obter_quadra(settings.db_path, quadra_id)
    if not quadra:
        return {"participante": None, "quadra": None}

    participante = await obter_participante(settings.db_path, quadra_id, session_id)
    return {
        "participante": participante,
        "quadra": quadra,
    }


@router.get("/quadras/{quadra_id}/participantes")
async def get_participantes(quadra_id: str):
    quadra = await obter_quadra(settings.db_path, quadra_id)
    if not quadra:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quadra não encontrada.",
        )

    participantes = await listar_participantes(settings.db_path, quadra_id)
    online_set = await hub.participantes_online(quadra_id)
    for p in participantes:
        p["online"] = p["id"] in online_set

    return {"participantes": participantes}


@router.get("/quadras/{quadra_id}/partida")
async def get_partida_quadra(quadra_id: str):
    quadra = await obter_quadra(settings.db_path, quadra_id)
    if not quadra:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quadra não encontrada.",
        )
    partida_id = quadra.get("partida_id")
    if not partida_id:
        return {"partida_id": None, "estado_partida": None}

    eventos = await carregar_eventos(settings.db_path, partida_id)
    estado_partida = projetar_estado(eventos)
    return {
        "partida_id": partida_id,
        "estado_partida": asdict(estado_partida),
    }


async def executar_comando(quadra_id: str, request: Request, acao: str, **kwargs):
    session_id = request.headers.get("x-session-id") or request.cookies.get(
        SESSION_COOKIE
    )
    async with get_quadra_lock(quadra_id):
        resultado = await asyncio.to_thread(
            executar_sync,
            settings.db_path,
            quadra_id,
            session_id,
            acao,
            versao=request.headers.get("x-control-version"),
            **kwargs,
        )
        online = await hub.participantes_online(quadra_id)
        for p in resultado["participantes"]:
            p["online"] = p["id"] in online
        await hub.broadcast(
            quadra_id, {"tipo": "PLACAR_ATUALIZADO", "payload": resultado}
        )
        return resultado


@router.post("/quadras/{quadra_id}/pontos", status_code=201)
async def post_marcar_ponto(quadra_id: str, body: MarcarPontoBody, request: Request):
    return await executar_comando(quadra_id, request, "pontos", equipe=body.equipe)


@router.post("/quadras/{quadra_id}/desfazer")
async def post_desfazer_ponto(quadra_id: str, request: Request):
    return await executar_comando(quadra_id, request, "desfazer")


@router.post("/quadras/{quadra_id}/reiniciar")
async def post_reiniciar_partida(quadra_id: str, request: Request):
    return await executar_comando(quadra_id, request, "reiniciar")


@router.post("/quadras/{quadra_id}/controle/assumir")
async def post_assumir_controle(quadra_id: str, request: Request):
    return await executar_comando(quadra_id, request, "assumir")


@router.post("/quadras/{quadra_id}/participantes/{participante_id}/admin")
async def post_autorizar_admin(quadra_id: str, participante_id: str, request: Request):
    return await executar_comando(
        quadra_id, request, "autorizar", alvo_id=participante_id
    )


@router.get("/quadras/{quadra_id}/linha-do-tempo", status_code=status.HTTP_200_OK)
async def get_linha_do_tempo(quadra_id: str):
    quadra = await obter_quadra(settings.db_path, quadra_id)
    if not quadra:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quadra não encontrada.",
        )

    partida_id = quadra.get("partida_id")
    if not partida_id:
        return {"itens": []}

    eventos = await carregar_eventos(settings.db_path, partida_id)
    participantes = await listar_participantes(settings.db_path, quadra_id)
    apelidos_map = {p["id"]: p["apelido"] for p in participantes}

    itens = projetar_linha_do_tempo(eventos, apelidos_map)
    return {"itens": itens}
