from pathlib import Path

import httpx
import pytest
from httpx import ASGITransport

from app.config import settings
from app.db import init_db
from app.eventos import TipoEvento, carregar_eventos
from app.main import app


@pytest.fixture(autouse=True)
async def setup_test_db(tmp_path: Path):
    db_file = str(tmp_path / "test_us1.db")
    settings.db_path = db_file
    await init_db(db_file)
    yield


@pytest.mark.asyncio
async def test_criar_e_listar_arenas_e_quadras():
    """Criação de Arena (ex: T9 Beach Club) e criação de quadras vinculadas."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Cria Arena
        resp_arena = await client.post("/api/arenas", json={"nome": "T9 Beach Club"})
        assert resp_arena.status_code == 201
        arena = resp_arena.json()
        assert arena["nome"] == "T9 Beach Club"
        arena_id = arena["id"]

        # Lista Arenas
        resp_arenas = await client.get("/api/arenas")
        assert resp_arenas.status_code == 200
        arenas = resp_arenas.json()["arenas"]
        assert len(arenas) == 1
        assert arenas[0]["nome"] == "T9 Beach Club"

        # Cria quadras dentro da Arena
        resp_q1 = await client.post(
            f"/api/arenas/{arena_id}/quadras", json={"nome": "Quadra 1 (Areia)"}
        )
        assert resp_q1.status_code == 201
        assert resp_q1.json()["arena_id"] == arena_id

        resp_q2 = await client.post(
            f"/api/arenas/{arena_id}/quadras", json={"nome": "Quadra 2 (Central)"}
        )
        assert resp_q2.status_code == 201

        # Lista quadras daquela arena
        resp_quadras = await client.get(f"/api/arenas/{arena_id}/quadras")
        assert resp_quadras.status_code == 200
        data = resp_quadras.json()
        assert data["arena"]["nome"] == "T9 Beach Club"
        assert len(data["quadras"]) == 2
        nomes_quadras = [q["nome"] for q in data["quadras"]]
        assert "Quadra 1 (Areia)" in nomes_quadras
        assert "Quadra 2 (Central)" in nomes_quadras


@pytest.mark.asyncio
async def test_criar_e_listar_quadras():
    """POST /api/quadras cria quadra e grava PARTIDA_INICIADA; GET lista com contagem."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Cria primeira quadra
        resp = await client.post("/api/quadras", json={"nome": "Quadra Central"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["nome"] == "Quadra Central"
        quadra_id = data["id"]
        partida_id = data["partida_id"]

        # Confere que o evento PARTIDA_INICIADA foi gravado
        eventos = await carregar_eventos(settings.db_path, partida_id)
        assert len(eventos) == 1
        assert eventos[0].tipo == TipoEvento.PARTIDA_INICIADA
        assert eventos[0].payload["alvo"] == 12

        # Listagem de quadras
        resp_list = await client.get("/api/quadras")
        assert resp_list.status_code == 200
        quadras = resp_list.json()["quadras"]
        assert len(quadras) == 1
        assert quadras[0]["id"] == quadra_id
        assert quadras[0]["participantes_count"] == 0


@pytest.mark.asyncio
async def test_primeiro_participante_vira_admin_segundo_espectador():
    """Primeiro participante registrado na quadra vira ADMIN; o segundo vira ESPECTADOR."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client_eli:
        # Eli cria a quadra
        resp_q = await client_eli.post("/api/quadras", json={"nome": "Quadra Areia"})
        quadra_id = resp_q.json()["id"]

        # Eli entra com seu apelido
        resp_entrar_eli = await client_eli.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Eli"}
        )
        assert resp_entrar_eli.status_code == 200
        part_eli = resp_entrar_eli.json()["participante"]
        assert part_eli["apelido"] == "Eli"
        assert part_eli["papel"] == "ADMIN"
        assert "session_id" in client_eli.cookies

    # Segundo cliente (sessão isolada, como segundo celular)
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client_carlos:
        resp_entrar_carlos = await client_carlos.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Carlos"}
        )
        assert resp_entrar_carlos.status_code == 200
        part_carlos = resp_entrar_carlos.json()["participante"]
        assert part_carlos["apelido"] == "Carlos"
        assert part_carlos["papel"] == "ESPECTADOR"
        assert "session_id" in client_carlos.cookies

        # Lista participantes da quadra
        resp_parts = await client_carlos.get(f"/api/quadras/{quadra_id}/participantes")
        assert resp_parts.status_code == 200
        participantes = resp_parts.json()["participantes"]
        assert len(participantes) == 2
        papeis = {p["apelido"]: p["papel"] for p in participantes}
        assert papeis["Eli"] == "ADMIN"
        assert papeis["Carlos"] == "ESPECTADOR"


@pytest.mark.asyncio
async def test_persistencia_da_sessao_no_f5():
    """GET /api/quadras/{id}/eu restaura participante a partir do cookie sem pedir apelido."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Cria quadra e entra
        resp_q = await client.post("/api/quadras", json={"nome": "Quadra 1"})
        quadra_id = resp_q.json()["id"]

        await client.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Renata"}
        )

        # Simula F5 / recarregar página consultando /eu com o cookie existente
        resp_eu = await client.get(f"/api/quadras/{quadra_id}/eu")
        assert resp_eu.status_code == 200
        data = resp_eu.json()
        assert data["participante"] is not None
        assert data["participante"]["apelido"] == "Renata"
        assert data["participante"]["papel"] == "ADMIN"
        assert data["quadra"]["id"] == quadra_id


@pytest.mark.asyncio
async def test_recuperacao_sem_sessao_retorna_null():
    """GET /api/quadras/{id}/eu sem cookie retorna participante: null."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp_q = await client.post("/api/quadras", json={"nome": "Quadra 2"})
        quadra_id = resp_q.json()["id"]

        resp_eu = await client.get(f"/api/quadras/{quadra_id}/eu")
        assert resp_eu.status_code == 200
        data = resp_eu.json()
        assert data["participante"] is None


def test_websocket_presenca_estado_inicial():
    """Conexão WebSocket recebe ESTADO_INICIAL com quadra e lista de participantes."""
    from starlette.testclient import TestClient

    with TestClient(app) as client:
        # Cria quadra
        resp_q = client.post("/api/quadras", json={"nome": "Quadra WS"})
        assert resp_q.status_code == 201
        quadra_id = resp_q.json()["id"]

        # Entra na quadra
        resp_entrar = client.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Marina"}
        )
        assert resp_entrar.status_code == 200

        # Conecta no WebSocket da quadra
        with client.websocket_connect(f"/ws/{quadra_id}") as ws:
            msg = ws.receive_json()
            assert msg["tipo"] == "ESTADO_INICIAL"
            assert msg["payload"]["quadra"]["nome"] == "Quadra WS"
            participantes = msg["payload"]["participantes"]
            assert len(participantes) == 1
            assert participantes[0]["apelido"] == "Marina"
            assert participantes[0]["papel"] == "ADMIN"
            assert participantes[0]["online"] is True


@pytest.mark.asyncio
async def test_limites_capacidade():
    """Verifica bloqueio quando os limites de arenas, quadras ou participantes são atingidos."""
    # Configura limites baixos para teste
    settings.max_arenas = 2
    settings.max_quadras_por_arena = 2
    settings.max_participantes_por_quadra = 2

    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # 1. Limite de Arenas (máx 2)
        r_a1 = await client.post("/api/arenas", json={"nome": "Arena 1"})
        assert r_a1.status_code == 201
        arena1_id = r_a1.json()["id"]

        r_a2 = await client.post("/api/arenas", json={"nome": "Arena 2"})
        assert r_a2.status_code == 201

        r_a3 = await client.post("/api/arenas", json={"nome": "Arena 3"})
        assert r_a3.status_code == 400
        assert "limite máximo" in r_a3.json()["detail"].lower()

        # 2. Limite de Quadras por Arena (máx 2)
        r_q1 = await client.post(
            f"/api/arenas/{arena1_id}/quadras", json={"nome": "Quadra 1"}
        )
        assert r_q1.status_code == 201
        quadra1_id = r_q1.json()["id"]

        r_q2 = await client.post(
            f"/api/arenas/{arena1_id}/quadras", json={"nome": "Quadra 2"}
        )
        assert r_q2.status_code == 201

        r_q3 = await client.post(
            f"/api/arenas/{arena1_id}/quadras", json={"nome": "Quadra 3"}
        )
        assert r_q3.status_code == 400
        assert "limite máximo" in r_q3.json()["detail"].lower()

        # 3. Limite de Participantes por Quadra (máx 2)
        r_p1 = await client.post(
            f"/api/quadras/{quadra1_id}/entrar",
            json={"apelido": "User 1"},
            headers={"x-session-id": "s1"},
        )
        assert r_p1.status_code == 200

        r_p2 = await client.post(
            f"/api/quadras/{quadra1_id}/entrar",
            json={"apelido": "User 2"},
            headers={"x-session-id": "s2"},
        )
        assert r_p2.status_code == 200

        r_p3 = await client.post(
            f"/api/quadras/{quadra1_id}/entrar",
            json={"apelido": "User 3"},
            headers={"x-session-id": "s3"},
        )
        assert r_p3.status_code == 400
        assert "limite máximo" in r_p3.json()["detail"].lower()

        # Restaura limites padrão
        settings.max_arenas = 50
        settings.max_quadras_por_arena = 20
        settings.max_participantes_por_quadra = 50
