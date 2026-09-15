import asyncio
import secrets
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
    criar_quadra,
    listar_participantes,
    listar_quadras,
    listar_quadras_owner,
    obter_participante,
    obter_quadra,
    registrar_participante,
)
from app.rate_limit import owner_rate_limiter

router = APIRouter(prefix="/api", tags=["quadras"])


class MarcarPontoBody(BaseModel):
    equipe: str = Field(..., description="Equipe que marcou ponto: 'A' ou 'B'")


def formatar_nome_equipe(
    j1: str | None, j2: str | None, equipe_direta: str | None, padrao: str
) -> tuple[str, list[str]]:
    jogadores: list[str] = []
    if j1 and j1.strip():
        jogadores.append(j1.strip())
    if j2 and j2.strip():
        jogadores.append(j2.strip())

    if jogadores:
        nome = " / ".join(jogadores)
    elif equipe_direta and equipe_direta.strip():
        nome = equipe_direta.strip()
    else:
        nome = padrao

    return nome, jogadores


class CriarQuadraBody(BaseModel):
    apelido: str | None = Field(default=None, max_length=30)
    nome: str | None = Field(default=None, max_length=50)
    time_a_jogador1: str | None = Field(default=None, max_length=30)
    time_a_jogador2: str | None = Field(default=None, max_length=30)
    time_b_jogador1: str | None = Field(default=None, max_length=30)
    time_b_jogador2: str | None = Field(default=None, max_length=30)
    equipe_a: str | None = Field(default=None, max_length=60)
    equipe_b: str | None = Field(default=None, max_length=60)
    alvo: int = Field(
        default=12, ge=1, le=100, description="Pontuação-alvo para vitória"
    )
    vantagem: bool = Field(
        default=True, description="Exigência de 2 pontos de vantagem"
    )
    teto: int | None = Field(
        default=None, ge=1, le=200, description="Teto máximo de pontuação"
    )


class ReiniciarPartidaBody(BaseModel):
    time_a_jogador1: str | None = Field(default=None, max_length=30)
    time_a_jogador2: str | None = Field(default=None, max_length=30)
    time_b_jogador1: str | None = Field(default=None, max_length=30)
    time_b_jogador2: str | None = Field(default=None, max_length=30)
    equipe_a: str | None = Field(default=None, max_length=60)
    equipe_b: str | None = Field(default=None, max_length=60)


class EntrarQuadraBody(BaseModel):
    apelido: str = Field(..., min_length=1, max_length=30)


def extrair_ou_gerar_session_id(request: Request) -> tuple[str, bool]:
    session_id = request.headers.get("x-session-id") or request.cookies.get(
        SESSION_COOKIE
    )
    if session_id:
        return session_id, False
    return str(uuid.uuid4()), True


# --- ROTAS DE QUADRAS E PARTICIPANTES ---


@router.get("/quadras")
async def get_quadras():
    quadras = await listar_quadras(settings.db_path)
    return {"quadras": quadras}


@router.post("/quadras", status_code=status.HTTP_201_CREATED)
async def post_quadras(
    body: CriarQuadraBody,
    request: Request,
    response: Response,
):
    if body.teto is not None and body.teto < body.alvo:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O teto da vantagem não pode ser menor que a pontuação-alvo.",
        )
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

    nome_a, j_a = formatar_nome_equipe(
        body.time_a_jogador1, body.time_a_jogador2, body.equipe_a, "Equipe A"
    )
    nome_b, j_b = formatar_nome_equipe(
        body.time_b_jogador1, body.time_b_jogador2, body.equipe_b, "Equipe B"
    )

    try:
        quadra = await criar_quadra(
            settings.db_path,
            nome=nome,
            session_id=session_id,
            apelido=apelido,
            equipe_a=nome_a,
            equipe_b=nome_b,
            jogadores_a=j_a,
            jogadores_b=j_b,
            alvo=body.alvo,
            vantagem=body.vantagem,
            teto=body.teto,
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
async def post_reiniciar_partida(
    quadra_id: str, request: Request, body: ReiniciarPartidaBody | None = None
):
    kwargs = {}
    if body:
        nome_a, j_a = formatar_nome_equipe(
            body.time_a_jogador1, body.time_a_jogador2, body.equipe_a, ""
        )
        nome_b, j_b = formatar_nome_equipe(
            body.time_b_jogador1, body.time_b_jogador2, body.equipe_b, ""
        )
        if nome_a:
            kwargs["equipe_a"] = nome_a
            kwargs["jogadores_a"] = j_a
        if nome_b:
            kwargs["equipe_b"] = nome_b
            kwargs["jogadores_b"] = j_b

    return await executar_comando(quadra_id, request, "reiniciar", **kwargs)


@router.post("/quadras/{quadra_id}/controle/assumir")
async def post_assumir_controle(quadra_id: str, request: Request):
    return await executar_comando(quadra_id, request, "assumir")


@router.post("/quadras/{quadra_id}/participantes/{participante_id}/admin")
async def post_autorizar_admin(quadra_id: str, participante_id: str, request: Request):
    return await executar_comando(
        quadra_id, request, "autorizar", alvo_id=participante_id
    )


@router.post("/quadras/{quadra_id}/participantes/{participante_id}/promover")
async def post_promover_controlador(
    quadra_id: str, participante_id: str, request: Request
):
    return await executar_comando(
        quadra_id, request, "promover", alvo_id=participante_id
    )


@router.post("/quadras/{quadra_id}/participantes/{participante_id}/revogar")
async def post_revogar_controlador(
    quadra_id: str, participante_id: str, request: Request
):
    return await executar_comando(
        quadra_id, request, "revogar", alvo_id=participante_id
    )


class AlterarPapelBody(BaseModel):
    papel: str


@router.post("/quadras/{quadra_id}/participantes/{participante_id}/papel")
async def post_alterar_papel(
    quadra_id: str, participante_id: str, body: AlterarPapelBody, request: Request
):
    papel_desejado = body.papel.strip().upper()
    if papel_desejado == "CONTROLADOR":
        acao = "promover"
    elif papel_desejado == "ESPECTADOR":
        acao = "revogar"
    elif papel_desejado == "ADMIN":
        acao = "autorizar"
    else:
        raise HTTPException(status_code=422, detail=f"Papel inválido: {body.papel}")
    return await executar_comando(quadra_id, request, acao, alvo_id=participante_id)


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


def extrair_chave_rate_limit(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"


def autenticar_owner(request: Request) -> None:
    chave = extrair_chave_rate_limit(request)

    # 1. Verifica se está bloqueado por rate limit
    bloqueado, restante = owner_rate_limiter.esta_bloqueado(chave)
    if bloqueado:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas tentativas incorretas. Tente novamente mais tarde.",
            headers={"Retry-After": str(restante)},
        )

    # 2. Extrai segredo via header x-owner-secret ou Authorization: Bearer
    secret = request.headers.get("x-owner-secret")
    if not secret:
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            secret = auth_header[7:].strip()

    config_secret = settings.owner_secret
    if (
        not secret
        or not config_secret
        or not secrets.compare_digest(
            secret.encode("utf-8"), config_secret.encode("utf-8")
        )
    ):
        owner_rate_limiter.registrar_falha(chave)
        # Retorna 404 para mascarar a existência do endpoint a não autorizados
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Não encontrado.",
        )

    # 3. Sucesso: limpa tentativas falhas acumuladas
    owner_rate_limiter.registrar_sucesso(chave)


@router.get("/owner/quadras", status_code=status.HTTP_200_OK)
async def get_owner_quadras(request: Request):
    autenticar_owner(request)
    quadras = await listar_quadras_owner(settings.db_path)
    return {"quadras": quadras}
