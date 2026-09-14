import uuid
from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel, Field

from app.config import settings
from app.eventos import TipoEvento, append_evento, carregar_eventos
from app.hub import hub
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
    nome: str = Field(..., min_length=1, max_length=50)
    arena_id: str | None = None


class EntrarQuadraBody(BaseModel):
    apelido: str = Field(..., min_length=1, max_length=30)


def extrair_ou_gerar_session_id(request: Request) -> tuple[str, bool]:
    session_id = request.cookies.get("session_id") or request.headers.get(
        "x-session-id"
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
    nome = body.nome.strip()
    if not nome:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Nome da quadra não pode ser vazio.",
        )
    try:
        quadra = await criar_quadra(settings.db_path, arena_id=arena_id, nome=nome)
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
async def post_quadras(body: CriarQuadraBody):
    nome = body.nome.strip()
    if not nome:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Nome da quadra não pode ser vazio.",
        )
    arena_id = body.arena_id
    try:
        if not arena_id:
            arenas = await listar_arenas(settings.db_path)
            if arenas:
                arena_id = arenas[0]["id"]
            else:
                nova_arena = await criar_arena(settings.db_path, "Arena Principal")
                arena_id = nova_arena["id"]

        quadra = await criar_quadra(settings.db_path, arena_id=arena_id, nome=nome)
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
            key="session_id",
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
    session_id = request.cookies.get("session_id") or request.headers.get(
        "x-session-id"
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


@router.post("/quadras/{quadra_id}/pontos", status_code=status.HTTP_201_CREATED)
async def post_marcar_ponto(
    quadra_id: str,
    body: MarcarPontoBody,
    request: Request,
):
    quadra = await obter_quadra(settings.db_path, quadra_id)
    if not quadra:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quadra não encontrada.",
        )

    partida_id = quadra.get("partida_id")
    if not partida_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma partida ativa encontrada para esta quadra.",
        )

    session_id = request.cookies.get("session_id") or request.headers.get(
        "x-session-id"
    )
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Participante não autenticado.",
        )

    participante = await obter_participante(settings.db_path, quadra_id, session_id)
    if not participante:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Participante não registrado nesta quadra.",
        )

    if participante["papel"] not in ("ADMIN", "CONTROLADOR"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores e controladores podem marcar pontos.",
        )

    equipe = body.equipe.strip().upper()
    if equipe not in ("A", "B"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Equipe deve ser 'A' ou 'B'.",
        )

    eventos_atuais = await carregar_eventos(settings.db_path, partida_id)
    estado_atual = projetar_estado(eventos_atuais)
    if estado_atual.encerrada:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A partida já está encerrada.",
        )

    evento = await append_evento(
        settings.db_path,
        quadra_id=quadra_id,
        partida_id=partida_id,
        tipo=TipoEvento.PONTO_MARCADO,
        payload={"equipe": equipe},
        autor_id=participante["id"],
    )

    novo_estado = projetar_estado([*eventos_atuais, evento])
    estado_dict = asdict(novo_estado)
    evento_dict = asdict(evento)

    participantes = await listar_participantes(settings.db_path, quadra_id)
    apelidos_map = {p["id"]: p["apelido"] for p in participantes}
    todos_eventos = [*eventos_atuais, evento]
    linha_itens = projetar_linha_do_tempo(todos_eventos, apelidos_map)

    # Broadcast para todos os clientes WebSocket conectados na quadra
    await hub.broadcast(
        quadra_id,
        {
            "tipo": "PLACAR_ATUALIZADO",
            "payload": {
                "evento": evento_dict,
                "estado_partida": estado_dict,
                "linha_do_tempo": linha_itens,
            },
        },
    )

    return {
        "evento": evento_dict,
        "estado_partida": estado_dict,
        "linha_do_tempo": linha_itens,
    }


@router.post("/quadras/{quadra_id}/desfazer", status_code=status.HTTP_200_OK)
async def post_desfazer_ponto(
    quadra_id: str,
    request: Request,
):
    quadra = await obter_quadra(settings.db_path, quadra_id)
    if not quadra:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quadra não encontrada.",
        )

    partida_id = quadra.get("partida_id")
    if not partida_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma partida ativa encontrada para esta quadra.",
        )

    session_id = request.cookies.get("session_id") or request.headers.get(
        "x-session-id"
    )
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Participante não autenticado.",
        )

    participante = await obter_participante(settings.db_path, quadra_id, session_id)
    if not participante:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Participante não registrado nesta quadra.",
        )

    if participante["papel"] not in ("ADMIN", "CONTROLADOR"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores e controladores podem desfazer pontos.",
        )

    eventos_atuais = await carregar_eventos(settings.db_path, partida_id)
    estado_atual = projetar_estado(eventos_atuais)

    if not estado_atual.eventos_ativos_seq:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum ponto para desfazer.",
        )

    # O ponto a ser anulado é o último ponto marcado ativo no log
    ref_seq = estado_atual.eventos_ativos_seq[-1]

    evento = await append_evento(
        settings.db_path,
        quadra_id=quadra_id,
        partida_id=partida_id,
        tipo=TipoEvento.PONTO_DESFEITO,
        payload={"ref_seq": ref_seq},
        autor_id=participante["id"],
    )

    novo_estado = projetar_estado([*eventos_atuais, evento])
    estado_dict = asdict(novo_estado)
    evento_dict = asdict(evento)

    participantes = await listar_participantes(settings.db_path, quadra_id)
    apelidos_map = {p["id"]: p["apelido"] for p in participantes}
    todos_eventos = [*eventos_atuais, evento]
    linha_itens = projetar_linha_do_tempo(todos_eventos, apelidos_map)

    # Broadcast para todos os clientes WebSocket conectados na quadra
    await hub.broadcast(
        quadra_id,
        {
            "tipo": "PLACAR_ATUALIZADO",
            "payload": {
                "evento": evento_dict,
                "estado_partida": estado_dict,
                "linha_do_tempo": linha_itens,
            },
        },
    )

    return {
        "evento": evento_dict,
        "estado_partida": estado_dict,
        "linha_do_tempo": linha_itens,
    }


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
