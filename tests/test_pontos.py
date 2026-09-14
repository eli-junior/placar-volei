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
    db_file = str(tmp_path / "test_us2.db")
    settings.db_path = db_file
    await init_db(db_file)
    yield


@pytest.mark.asyncio
async def test_marcar_ponto_equipe_a_e_b():
    """Marcação de pontos incrementa o placar projetado e registra eventos append-only."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Cria quadra
        resp_q = await client.post("/api/quadras", json={"nome": "Quadra Principal"})
        assert resp_q.status_code == 201
        quadra_id = resp_q.json()["id"]

        # Entra na quadra com apelido
        resp_entrar = await client.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Eli"}
        )
        assert resp_entrar.status_code == 200

        # Marca ponto para a Equipe A
        resp_ponto1 = await client.post(
            f"/api/quadras/{quadra_id}/pontos",
            headers={"x-control-version": "1"},
            json={"equipe": "A"},
        )
        assert resp_ponto1.status_code == 201
        data1 = resp_ponto1.json()
        assert data1["evento"]["tipo"] == TipoEvento.PONTO_MARCADO
        assert data1["evento"]["payload"]["equipe"] == "A"
        assert data1["evento"]["seq"] == 2  # seq 1 foi PARTIDA_INICIADA
        assert data1["estado_partida"]["pontos_a"] == 1
        assert data1["estado_partida"]["pontos_b"] == 0

        # Marca ponto para a Equipe B
        resp_ponto2 = await client.post(
            f"/api/quadras/{quadra_id}/pontos",
            headers={"x-control-version": "1"},
            json={"equipe": "b"},  # case-insensitive
        )
        assert resp_ponto2.status_code == 201
        data2 = resp_ponto2.json()
        assert data2["evento"]["payload"]["equipe"] == "B"
        assert data2["evento"]["seq"] == 3
        assert data2["estado_partida"]["pontos_a"] == 1
        assert data2["estado_partida"]["pontos_b"] == 1

        # Verifica persistência no banco
        partida_id = resp_q.json()["partida_id"]
        eventos = await carregar_eventos(settings.db_path, partida_id)
        assert len(eventos) == 3
        assert eventos[0].tipo == TipoEvento.PARTIDA_INICIADA
        assert eventos[1].tipo == TipoEvento.PONTO_MARCADO
        assert eventos[1].payload == {"equipe": "A"}
        assert eventos[2].tipo == TipoEvento.PONTO_MARCADO
        assert eventos[2].payload == {"equipe": "B"}


@pytest.mark.asyncio
async def test_marcar_ponto_validacoes():
    """Validações de segurança: sem autenticação, participante não registrado, equipe inválida."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp_q = await client.post("/api/quadras", json={"nome": "Quadra Teste"})
        quadra_id = resp_q.json()["id"]

        # 1. Sem cookie de sessão
        resp_sem_auth = await client.post(
            f"/api/quadras/{quadra_id}/pontos",
            headers={"x-control-version": "1"},
            json={"equipe": "A"},
        )
        assert resp_sem_auth.status_code == 401

        # 2. Com cookie desconhecido (não registrado nesta quadra)
        resp_nao_reg = await client.post(
            f"/api/quadras/{quadra_id}/pontos",
            json={"equipe": "A"},
            headers={"x-control-version": "1", "x-session-id": "sessao-inexistente"},
        )
        assert resp_nao_reg.status_code == 403

        # 3. Registra participante
        await client.post(
            f"/api/quadras/{quadra_id}/entrar",
            json={"apelido": "Carlos"},
            headers={"x-session-id": "sessao-carlos"},
        )

        # 4. Equipe inválida
        resp_inv = await client.post(
            f"/api/quadras/{quadra_id}/pontos",
            json={"equipe": "Z"},
            headers={"x-control-version": "1", "x-session-id": "sessao-carlos"},
        )
        assert resp_inv.status_code == 422


@pytest.mark.asyncio
async def test_consultar_partida_quadra():
    """GET /api/quadras/{id}/partida retorna o estado atualizado da partida."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp_q = await client.post("/api/quadras", json={"nome": "Quadra Central"})
        quadra_id = resp_q.json()["id"]

        # Consulta antes de qualquer ponto
        resp_partida = await client.get(f"/api/quadras/{quadra_id}/partida")
        assert resp_partida.status_code == 200
        data = resp_partida.json()
        assert data["estado_partida"]["pontos_a"] == 0
        assert data["estado_partida"]["pontos_b"] == 0
        assert data["estado_partida"]["encerrada"] is False

        # Entra e marca ponto
        await client.post(f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Bia"})
        await client.post(
            f"/api/quadras/{quadra_id}/pontos",
            headers={"x-control-version": "1"},
            json={"equipe": "A"},
        )

        # Consulta após o ponto
        resp_pos = await client.get(f"/api/quadras/{quadra_id}/partida")
        assert resp_pos.status_code == 200
        assert resp_pos.json()["estado_partida"]["pontos_a"] == 1


@pytest.mark.asyncio
async def test_marcar_ponto_bloqueado_se_partida_encerrada():
    """Rejeita marcação de ponto quando a partida já atingiu condição de vitória."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp_q = await client.post("/api/quadras", json={"nome": "Quadra Final"})
        quadra_id = resp_q.json()["id"]

        await client.post(f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Juiz"})

        # Regra padrão: alvo = 12, vantagem = True
        # Pontua 12 vezes para Time A
        for _ in range(12):
            resp = await client.post(
                f"/api/quadras/{quadra_id}/pontos",
                headers={"x-control-version": "1"},
                json={"equipe": "A"},
            )
            assert resp.status_code == 201

        # Placar agora é 12 × 0 (encerrada = True, vencedor = A)
        estado = resp.json()["estado_partida"]
        assert estado["encerrada"] is True
        assert estado["vencedor"] == "A"

        # Tentar marcar o 13º ponto deve ser rejeitado com 400
        resp_extra = await client.post(
            f"/api/quadras/{quadra_id}/pontos",
            headers={"x-control-version": "1"},
            json={"equipe": "A"},
        )
        assert resp_extra.status_code == 400
        assert "encerrada" in resp_extra.json()["detail"].lower()


def test_websocket_broadcast_ponto():
    """Conexão WebSocket recebe PLACAR_ATUALIZADO quando um ponto é marcado."""
    with TestClient(app) as client:
        resp_q = client.post("/api/quadras", json={"nome": "Quadra WS Ponto"})
        quadra_id = resp_q.json()["id"]

        # Entra na quadra
        client.post(f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Ana"})

        # Conecta no WebSocket
        with client.websocket_connect(f"/ws/{quadra_id}") as ws:
            msg_init = ws.receive_json()
            assert msg_init["tipo"] == "ESTADO_INICIAL"

            msg_presenca = ws.receive_json()
            assert msg_presenca["tipo"] == "PRESENCA_ATUALIZADA"

            # Marca ponto via REST
            resp_ponto = client.post(
                f"/api/quadras/{quadra_id}/pontos",
                headers={"x-control-version": "1"},
                json={"equipe": "A"},
            )
            assert resp_ponto.status_code == 201

            # Recebe broadcast do placar atualizado
            msg_ponto = ws.receive_json()
            assert msg_ponto["tipo"] == "PLACAR_ATUALIZADO"
            assert msg_ponto["payload"]["estado_partida"]["pontos_a"] == 1
            assert msg_ponto["payload"]["estado_partida"]["pontos_b"] == 0
            assert msg_ponto["payload"]["evento"]["payload"]["equipe"] == "A"
