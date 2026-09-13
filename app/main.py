import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect

from app.api import router as api_router
from app.config import settings
from app.db import init_db
from app.eventos import carregar_eventos
from app.hub import hub
from app.projecao import projetar_estado
from app.quadras import listar_participantes, obter_quadra


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializa o schema e WAL do SQLite na inicialização
    await init_db(settings.db_path)
    yield


app = FastAPI(
    title="Placar Vôlei",
    version="0.1.0",
    description="Placar de vôlei compartilhado em tempo real para pelada",
    lifespan=lifespan,
)

# Inclui rotas REST da API
app.include_router(api_router)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "version": "0.1.0",
        "db": settings.db_path,
    }


@app.websocket("/ws/{quadra_id}")
async def websocket_quadra(websocket: WebSocket, quadra_id: str):
    session_id = websocket.cookies.get("session_id") or websocket.query_params.get(
        "session_id"
    )
    participante_id = f"{quadra_id}:{session_id}" if session_id else None

    await hub.connect(quadra_id, websocket, participante_id)

    try:
        # Carrega estado inicial da quadra
        quadra = await obter_quadra(settings.db_path, quadra_id)
        if quadra and quadra.get("partida_id"):
            eventos = await carregar_eventos(settings.db_path, quadra["partida_id"])
            estado_partida = projetar_estado(eventos)
        else:
            estado_partida = projetar_estado([])

        participantes = await listar_participantes(settings.db_path, quadra_id)
        online_set = await hub.participantes_online(quadra_id)
        for p in participantes:
            p["online"] = p["id"] in online_set

        # Envia estado inicial ao cliente conectado
        await websocket.send_json(
            {
                "tipo": "ESTADO_INICIAL",
                "payload": {
                    "quadra": quadra,
                    "estado_partida": {
                        "pontos_a": estado_partida.pontos_a,
                        "pontos_b": estado_partida.pontos_b,
                        "equipe_a": estado_partida.equipe_a,
                        "equipe_b": estado_partida.equipe_b,
                        "alvo": estado_partida.alvo,
                        "vantagem": estado_partida.vantagem,
                        "teto": estado_partida.teto,
                        "encerrada": estado_partida.encerrada,
                        "vencedor": estado_partida.vencedor,
                    },
                    "participantes": participantes,
                },
            }
        )

        # Notifica a quadra que a lista de presença atualizou
        await hub.broadcast(
            quadra_id,
            {
                "tipo": "PRESENCA_ATUALIZADA",
                "payload": {"participantes": participantes},
            },
        )

        while True:
            # Mantém conexão viva aguardando mensagens (ou ping)
            await websocket.receive_text()

    except (WebSocketDisconnect, RuntimeError, OSError):
        pass
    finally:
        await hub.disconnect(quadra_id, websocket)
        # Notifica a quadra após desconexão
        participantes = await listar_participantes(settings.db_path, quadra_id)
        online_set = await hub.participantes_online(quadra_id)
        for p in participantes:
            p["online"] = p["id"] in online_set

        await hub.broadcast(
            quadra_id,
            {
                "tipo": "PRESENCA_ATUALIZADA",
                "payload": {"participantes": participantes},
            },
        )


# Servir estáticos e SPA do frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Se for um arquivo existente em static_dir, serve diretamente
        target = os.path.join(static_dir, full_path)
        if full_path and os.path.isfile(target):
            return FileResponse(target)
        # Fallback para o index.html da SPA
        index_file = os.path.join(static_dir, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file)
        return {"message": "Placar Vôlei Backend"}
