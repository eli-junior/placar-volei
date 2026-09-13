import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.db import init_db


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

# Monta arquivos estáticos do frontend caso a pasta exista
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "version": "0.1.0",
        "db": settings.db_path,
    }
