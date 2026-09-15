import asyncio
import logging
import os
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect

from app.api import normalizar_erros_validacao
from app.api import router as api_router
from app.comandos import snapshot_sync
from app.config import settings
from app.db import init_db
from app.eventos import get_quadra_lock
from app.hub import hub
from app.identidade import SESSION_COOKIE
from app.quadras import (
    atualizar_ultimo_visto,
    limpar_quadras_expiradas,
    listar_participantes,
    obter_participante,
    obter_quadra,
)
from app.sucessao import verificar_sucessao_quadra

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializa o schema e WAL do SQLite na inicialização
    await init_db(settings.db_path)

    async def rotina_limpeza():
        while True:
            try:
                await asyncio.sleep(300)
                await limpar_quadras_expiradas(settings.db_path)
            except asyncio.CancelledError:
                break
            except (sqlite3.Error, OSError, ValueError, RuntimeError) as e:
                logger.warning("Falha na rotina de limpeza de quadras expiradas: %s", e)

    async def rotina_sucessao():
        while True:
            try:
                await asyncio.sleep(2)
                quadras_ativas = await hub.quadras_ativas()
                for quadra_id in quadras_ativas:
                    snapshot_sucessao = await verificar_sucessao_quadra(
                        settings.db_path, quadra_id
                    )
                    if snapshot_sucessao:
                        online = await hub.participantes_online(quadra_id)
                        for p in snapshot_sucessao["participantes"]:
                            p["online"] = p["id"] in online
                        await hub.broadcast(
                            quadra_id,
                            {
                                "tipo": "PLACAR_ATUALIZADO",
                                "payload": snapshot_sucessao,
                            },
                        )
                        await hub.broadcast(
                            quadra_id,
                            {
                                "tipo": "PRESENCA_ATUALIZADA",
                                "payload": {
                                    "participantes": snapshot_sucessao["participantes"]
                                },
                            },
                        )
            except asyncio.CancelledError:
                break
            except (sqlite3.Error, OSError, ValueError, RuntimeError) as e:
                logger.warning("Falha na rotina de sucessao: %s", e)

    tarefa_limpeza = asyncio.create_task(rotina_limpeza())
    tarefa_sucessao = asyncio.create_task(rotina_sucessao())
    try:
        yield
    finally:
        tarefa_limpeza.cancel()
        tarefa_sucessao.cancel()


app = FastAPI(
    title="Placar Vôlei",
    version=settings.version,
    description="Placar de vôlei compartilhado em tempo real para pelada",
    lifespan=lifespan,
)

# Inclui rotas REST da API
app.include_router(api_router)


@app.exception_handler(RequestValidationError)
async def tratar_erro_de_validacao(request: Request, exc: RequestValidationError):
    """Normaliza o 422 do FastAPI para um formato legível e estável.

    O padrão do FastAPI devolve `detail` como lista de dicionários, que o
    frontend renderizava como `"[object Object]"`. Aqui `detail` é sempre uma
    frase em português e `erros` carrega o detalhamento campo a campo para quem
    quiser destacar o campo culpado na interface.
    """
    corpo = normalizar_erros_validacao(exc.errors())
    logger.info("Requisição inválida em %s: %s", request.url.path, corpo["detail"])
    return JSONResponse(status_code=422, content=corpo)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "version": settings.version,
        "db": settings.db_path,
    }


@app.websocket("/ws/{quadra_id}")
async def websocket_quadra(websocket: WebSocket, quadra_id: str):
    session_id = websocket.cookies.get(SESSION_COOKIE)
    conectado = False
    try:
        async with get_quadra_lock(quadra_id):
            quadra = await obter_quadra(settings.db_path, quadra_id)
            if not quadra:
                await websocket.accept()
                await websocket.send_json({"tipo": "SALA_EXPIRADA", "payload": {}})
                await websocket.close(code=4404)
                return
            participante = (
                await obter_participante(settings.db_path, quadra_id, session_id)
                if session_id
                else None
            )
            if not participante:
                await websocket.accept()
                await websocket.close(code=4401)
                return
            await hub.connect(quadra_id, websocket, participante["id"])
            await atualizar_ultimo_visto(settings.db_path, participante["id"])
            conectado = True
            inicial = await asyncio.to_thread(
                snapshot_sync, settings.db_path, quadra_id
            )
            online = await hub.participantes_online(quadra_id)
            for p in inicial["participantes"]:
                p["online"] = p["id"] in online
            await websocket.send_json({"tipo": "ESTADO_INICIAL", "payload": inicial})
            await hub.broadcast(
                quadra_id,
                {
                    "tipo": "PRESENCA_ATUALIZADA",
                    "payload": {"participantes": inicial["participantes"]},
                },
            )

        while True:
            # Verifica expiração mesmo se o cliente não enviar mensagens.
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=5)
            except TimeoutError:
                pass
            atual = await obter_quadra(settings.db_path, quadra_id)
            if not atual:
                await websocket.send_json({"tipo": "SALA_EXPIRADA", "payload": {}})
                await websocket.close(code=4404)
                return
            if atual["partida_id"] != inicial["partida_id"]:
                inicial["partida_id"] = atual["partida_id"]
    except (WebSocketDisconnect, RuntimeError, OSError):
        pass
    finally:
        if conectado:
            await hub.disconnect(quadra_id, websocket)
            if participante:
                await atualizar_ultimo_visto(settings.db_path, participante["id"])
            participantes = await listar_participantes(settings.db_path, quadra_id)
            online = await hub.participantes_online(quadra_id)
            for p in participantes:
                p["online"] = p["id"] in online
            await hub.broadcast(
                quadra_id,
                {
                    "tipo": "PRESENCA_ATUALIZADA",
                    "payload": {"participantes": participantes},
                },
            )


# Rota raiz de conveniência para o endpoint de owner
@app.get("/owner/quadras", status_code=200)
async def get_root_owner_quadras(request: Request):
    from app.api import get_owner_quadras

    return await get_owner_quadras(request)


# Servir estáticos e SPA do frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/") or full_path == "api":
            raise HTTPException(404, "Endpoint não encontrado.")
        # Se for um arquivo existente em static_dir, serve diretamente
        if "\\" in full_path or "\x00" in full_path:
            raise HTTPException(404, "Arquivo não encontrado.")
        public_root = Path(static_dir).resolve()
        target = (public_root / full_path).resolve()
        if not target.is_relative_to(public_root):
            raise HTTPException(404, "Arquivo não encontrado.")
        if full_path and target.is_file():
            return FileResponse(target)
        # Fallback para o index.html da SPA
        index_file = os.path.join(static_dir, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file)
        return {"message": "Placar Vôlei Backend"}
