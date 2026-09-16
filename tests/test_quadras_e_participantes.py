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
        assert "placar_session_v3" in client_eli.cookies

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
        assert "placar_session_v3" in client_carlos.cookies

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
    """Verifica bloqueio quando os limites de quadras ou participantes são atingidos."""
    # Configura limites baixos para teste
    settings.max_quadras = 2
    settings.max_participantes_por_quadra = 2

    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # 1. Limite de Quadras (máx 2)
        r_q1 = await client.post("/api/quadras", json={"nome": "Quadra 1"})
        assert r_q1.status_code == 201
        quadra1_id = r_q1.json()["id"]

        r_q2 = await client.post("/api/quadras", json={"nome": "Quadra 2"})
        assert r_q2.status_code == 201

        r_q3 = await client.post("/api/quadras", json={"nome": "Quadra 3"})
        assert r_q3.status_code == 400
        assert "limite máximo" in r_q3.json()["detail"].lower()

        # 2. Limite de Participantes por Quadra (máx 2)
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


@pytest.mark.asyncio
async def test_listagem_quadras_inclui_resumo_partida():
    """GET /api/quadras deve incluir dados da partida ativa para a Home."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Cria quadra com duplas e pontuação
        r_cria = await client.post(
            "/api/quadras",
            json={
                "nome": "Arena Central",
                "apelido": "Carlos",
                "time_a_jogador1": "Carlos",
                "time_a_jogador2": "Daniel",
                "time_b_jogador1": "Roberto",
                "time_b_jogador2": "Eduardo",
                "alvo": 21,
            },
        )
        assert r_cria.status_code == 201
        dados_quadra = r_cria.json()
        quadra_id = dados_quadra["id"]
        controle_versao = dados_quadra["controle_versao"]

        # Marca ponto para equipe A
        r_ponto = await client.post(
            f"/api/quadras/{quadra_id}/pontos",
            json={"equipe": "A"},
            headers={"x-control-version": str(controle_versao)},
        )
        assert r_ponto.status_code == 201

        # Lista quadras públicas
        r_lista = await client.get("/api/quadras")
        assert r_lista.status_code == 200
        lista = r_lista.json()["quadras"]
        quadra_encontrada = next((q for q in lista if q["id"] == quadra_id), None)
        assert quadra_encontrada is not None
        assert "partida" in quadra_encontrada
        p = quadra_encontrada["partida"]
        assert p is not None
        assert p["pontos_a"] == 1
        assert p["pontos_b"] == 0
        assert "Carlos / Daniel" in p["equipe_a"]
        assert "Roberto / Eduardo" in p["equipe_b"]
        assert p["alvo"] == 21
        assert p["encerrada"] is False
