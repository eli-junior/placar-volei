from pathlib import Path

import httpx
import pytest
from httpx import ASGITransport
from starlette.testclient import TestClient

from app.config import settings
from app.db import init_db
from app.eventos import TipoEvento, carregar_eventos
from app.main import app


@pytest.fixture(autouse=True)
async def setup_test_db(tmp_path: Path):
    db_file = str(tmp_path / "test_us3.db")
    settings.db_path = db_file
    await init_db(db_file)
    yield


@pytest.mark.asyncio
async def test_desfazer_ponto_sucesso():
    """Desfazer ponto reverte a pontuação ponto a ponto e registra evento append-only."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Cria quadra e entra
        resp_q = await client.post("/api/quadras", json={"nome": "Quadra Desfazer"})
        quadra_id = resp_q.json()["id"]
        partida_id = resp_q.json()["partida_id"]
        await client.post(f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Eli"})

        # Marca 2 pontos para A e 1 para B (placar 2x1)
        await client.post(f"/api/quadras/{quadra_id}/pontos", json={"equipe": "A"})
        await client.post(f"/api/quadras/{quadra_id}/pontos", json={"equipe": "B"})
        await client.post(f"/api/quadras/{quadra_id}/pontos", json={"equipe": "A"})

        # Desfaz 1º ponto (deve anular o último ponto de A -> placar 1x1)
        resp_d1 = await client.post(f"/api/quadras/{quadra_id}/desfazer")
        assert resp_d1.status_code == 200
        data1 = resp_d1.json()
        assert data1["evento"]["tipo"] == TipoEvento.PONTO_DESFEITO
        assert data1["estado_partida"]["pontos_a"] == 1
        assert data1["estado_partida"]["pontos_b"] == 1

        # Desfaz 2º ponto (deve anular o ponto de B -> placar 1x0)
        resp_d2 = await client.post(f"/api/quadras/{quadra_id}/desfazer")
        assert resp_d2.status_code == 200
        assert resp_d2.json()["estado_partida"]["pontos_a"] == 1
        assert resp_d2.json()["estado_partida"]["pontos_b"] == 0

        # Desfaz 3º ponto (deve anular o primeiro ponto de A -> placar 0x0)
        resp_d3 = await client.post(f"/api/quadras/{quadra_id}/desfazer")
        assert resp_d3.status_code == 200
        assert resp_d3.json()["estado_partida"]["pontos_a"] == 0
        assert resp_d3.json()["estado_partida"]["pontos_b"] == 0

        # Confere banco append-only: 1 PARTIDA_INICIADA + 3 PONTO_MARCADO + 3 PONTO_DESFEITO = 7 eventos
        eventos = await carregar_eventos(settings.db_path, partida_id)
        assert len(eventos) == 7
        desfeitos = [e for e in eventos if e.tipo == TipoEvento.PONTO_DESFEITO]
        assert len(desfeitos) == 3


@pytest.mark.asyncio
async def test_desfazer_quando_placar_zerado():
    """Tentar desfazer quando o placar já está 0x0 retorna 400."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp_q = await client.post("/api/quadras", json={"nome": "Quadra 0x0"})
        quadra_id = resp_q.json()["id"]
        await client.post(f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Ana"})

        # Placar em 0x0 -> desfazer deve falhar com 400
        resp_desfazer = await client.post(f"/api/quadras/{quadra_id}/desfazer")
        assert resp_desfazer.status_code == 400
        assert "nenhum ponto" in resp_desfazer.json()["detail"].lower()


@pytest.mark.asyncio
async def test_desfazer_reverte_vitoria():
    """Desfazer o ponto da vitória reabre a partida e remove o estado de vitória."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp_q = await client.post("/api/quadras", json={"nome": "Quadra Match Point"})
        quadra_id = resp_q.json()["id"]
        await client.post(f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Juiz"})

        # Pontua 12 vezes para A -> partida encerrada
        for _ in range(12):
            resp = await client.post(
                f"/api/quadras/{quadra_id}/pontos", json={"equipe": "A"}
            )
        assert resp.json()["estado_partida"]["encerrada"] is True
        assert resp.json()["estado_partida"]["vencedor"] == "A"

        # Desfaz o 12º ponto
        resp_desfazer = await client.post(f"/api/quadras/{quadra_id}/desfazer")
        assert resp_desfazer.status_code == 200
        estado = resp_desfazer.json()["estado_partida"]
        assert estado["pontos_a"] == 11
        assert estado["encerrada"] is False
        assert estado["vencedor"] is None

        # Confirma que novos pontos podem ser marcados novamente
        resp_novo_ponto = await client.post(
            f"/api/quadras/{quadra_id}/pontos", json={"equipe": "B"}
        )
        assert resp_novo_ponto.status_code == 201
        assert resp_novo_ponto.json()["estado_partida"]["pontos_b"] == 1


@pytest.mark.asyncio
async def test_desfazer_validacoes_seguranca():
    """Desfazer exige participante autenticado e registrado na quadra."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp_q = await client.post("/api/quadras", json={"nome": "Quadra Auth"})
        quadra_id = resp_q.json()["id"]

        # 1. Sem autenticação
        resp_sem_auth = await client.post(f"/api/quadras/{quadra_id}/desfazer")
        assert resp_sem_auth.status_code == 401

        # 2. Sessão não registrada
        resp_desconhecida = await client.post(
            f"/api/quadras/{quadra_id}/desfazer",
            headers={"x-session-id": "sessao-fantasma"},
        )
        assert resp_desconhecida.status_code == 403


def test_websocket_broadcast_desfazer():
    """Conexão WebSocket recebe PLACAR_ATUALIZADO ao desfazer um ponto."""
    with TestClient(app) as client:
        resp_q = client.post("/api/quadras", json={"nome": "Quadra WS Desfazer"})
        quadra_id = resp_q.json()["id"]

        # Entra na quadra
        client.post(f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Bia"})

        # Conecta no WebSocket
        with client.websocket_connect(f"/ws/{quadra_id}") as ws:
            assert ws.receive_json()["tipo"] == "ESTADO_INICIAL"
            assert ws.receive_json()["tipo"] == "PRESENCA_ATUALIZADA"

            # Marca ponto
            client.post(f"/api/quadras/{quadra_id}/pontos", json={"equipe": "A"})
            msg_ponto = ws.receive_json()
            assert msg_ponto["tipo"] == "PLACAR_ATUALIZADO"
            assert msg_ponto["payload"]["estado_partida"]["pontos_a"] == 1

            # Desfaz ponto
            resp_d = client.post(f"/api/quadras/{quadra_id}/desfazer")
            assert resp_d.status_code == 200

            # Recebe broadcast do placar revertido
            msg_desfeito = ws.receive_json()
            assert msg_desfeito["tipo"] == "PLACAR_ATUALIZADO"
            assert msg_desfeito["payload"]["estado_partida"]["pontos_a"] == 0
            assert (
                msg_desfeito["payload"]["evento"]["tipo"] == TipoEvento.PONTO_DESFEITO
            )


@pytest.mark.asyncio
async def test_espectador_nao_pode_marcar_nem_desfazer_ponto():
    """Espectador é bloqueado com 403 ao tentar marcar ou desfazer ponto."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp_q = await client.post("/api/quadras", json={"nome": "Quadra Papeis"})
        quadra_id = resp_q.json()["id"]

        # 1. Primeiro participante entra -> ADMIN
        await client.post(
            f"/api/quadras/{quadra_id}/entrar",
            json={"apelido": "Eli Admin"},
            headers={"x-session-id": "sessao-admin"},
        )

        # 2. Segundo participante entra -> ESPECTADOR
        await client.post(
            f"/api/quadras/{quadra_id}/entrar",
            json={"apelido": "Carlos Espectador"},
            headers={"x-session-id": "sessao-espectador"},
        )

        # 3. Admin marca ponto com sucesso
        r_admin = await client.post(
            f"/api/quadras/{quadra_id}/pontos",
            json={"equipe": "A"},
            headers={"x-session-id": "sessao-admin"},
        )
        assert r_admin.status_code == 201

        # 4. Espectador tenta marcar ponto -> 403 Forbidden
        r_esp_marca = await client.post(
            f"/api/quadras/{quadra_id}/pontos",
            json={"equipe": "A"},
            headers={"x-session-id": "sessao-espectador"},
        )
        assert r_esp_marca.status_code == 403
        assert "administradores e controladores" in r_esp_marca.json()["detail"].lower()

        # 5. Espectador tenta desfazer ponto -> 403 Forbidden
        r_esp_desfaz = await client.post(
            f"/api/quadras/{quadra_id}/desfazer",
            headers={"x-session-id": "sessao-espectador"},
        )
        assert r_esp_desfaz.status_code == 403
        assert (
            "administradores e controladores" in r_esp_desfaz.json()["detail"].lower()
        )

        # 6. Admin desfaz o ponto com sucesso -> 200 OK
        r_admin_desfaz = await client.post(
            f"/api/quadras/{quadra_id}/desfazer",
            headers={"x-session-id": "sessao-admin"},
        )
        assert r_admin_desfaz.status_code == 200
        assert r_admin_desfaz.json()["estado_partida"]["pontos_a"] == 0
