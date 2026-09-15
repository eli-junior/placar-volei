from pathlib import Path

import httpx
import pytest
from httpx import ASGITransport

from app.config import settings
from app.db import init_db
from app.main import app


@pytest.fixture(autouse=True)
async def setup_test_db(tmp_path: Path):
    db_file = str(tmp_path / "test_jogadores.db")
    settings.db_path = db_file
    await init_db(db_file)
    yield


@pytest.mark.asyncio
async def test_criar_quadra_com_jogadores_individuais():
    """Testa criação de quadra com 1 jogador por equipe."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.post(
            "/api/quadras",
            json={
                "nome": "Quadra de Praia 1",
                "apelido": "Juiz",
                "time_a_jogador1": "Carlos",
                "time_b_jogador1": "Daniel",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        quadra_id = data["id"]

        resp_partida = await client.get(f"/api/quadras/{quadra_id}/partida")
        assert resp_partida.status_code == 200
        estado = resp_partida.json()["estado_partida"]

        assert estado["equipe_a"] == "Carlos"
        assert estado["equipe_b"] == "Daniel"
        assert estado["jogadores_a"] == ["Carlos"]
        assert estado["jogadores_b"] == ["Daniel"]


@pytest.mark.asyncio
async def test_criar_quadra_com_duplas():
    """Testa criação de quadra com duplas (2 jogadores por equipe)."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.post(
            "/api/quadras",
            json={
                "nome": "Quadra Central",
                "apelido": "Organizador",
                "time_a_jogador1": "Carlos",
                "time_a_jogador2": "Beto",
                "time_b_jogador1": "Daniel",
                "time_b_jogador2": "Edu",
            },
        )
        assert resp.status_code == 201
        quadra_id = resp.json()["id"]

        resp_partida = await client.get(f"/api/quadras/{quadra_id}/partida")
        estado = resp_partida.json()["estado_partida"]

        assert estado["equipe_a"] == "Carlos / Beto"
        assert estado["equipe_b"] == "Daniel / Edu"
        assert estado["jogadores_a"] == ["Carlos", "Beto"]
        assert estado["jogadores_b"] == ["Daniel", "Edu"]


@pytest.mark.asyncio
async def test_linha_do_tempo_com_nomes_dos_jogadores():
    """Testa se a linha do tempo e o encerramento usam o nome dos jogadores/equipe."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.post(
            "/api/quadras",
            json={
                "nome": "Quadra de Praia 2",
                "apelido": "Anotador",
                "time_a_jogador1": "Ana",
                "time_b_jogador1": "Bia",
            },
        )
        quadra_id = resp.json()["id"]

        # Marca ponto para equipe A
        resp_ponto = await client.post(
            f"/api/quadras/{quadra_id}/pontos",
            headers={"x-control-version": "1"},
            json={"equipe": "A"},
        )
        assert resp_ponto.status_code == 201
        resultado = resp_ponto.json()
        assert any("Ana" in item["descricao"] for item in resultado["linha_do_tempo"])

        # Equipe A vence a partida (12 pontos direto)
        for _ in range(11):
            await client.post(
                f"/api/quadras/{quadra_id}/pontos",
                headers={"x-control-version": "1"},
                json={"equipe": "A"},
            )

        resp_partida = await client.get(f"/api/quadras/{quadra_id}/partida")
        estado = resp_partida.json()["estado_partida"]
        assert estado["encerrada"] is True
        assert estado["vencedor"] == "A"


@pytest.mark.asyncio
async def test_reiniciar_partida_com_novos_jogadores_ou_mantendo():
    """Testa reinício mantendo os jogadores anteriores e reinício trocando os jogadores."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.post(
            "/api/quadras",
            json={
                "nome": "Quadra Final",
                "apelido": "Juiz",
                "time_a_jogador1": "Jogador 1",
                "time_b_jogador1": "Jogador 2",
            },
        )
        quadra_id = resp.json()["id"]

        # Marca 12 pontos para A
        for _ in range(12):
            await client.post(
                f"/api/quadras/{quadra_id}/pontos",
                headers={"x-control-version": "1"},
                json={"equipe": "A"},
            )

        # Reinicia sem body -> mantém Jogador 1 e Jogador 2
        resp_reinicio_1 = await client.post(f"/api/quadras/{quadra_id}/reiniciar")
        assert resp_reinicio_1.status_code == 200
        estado_1 = resp_reinicio_1.json()["estado_partida"]
        assert estado_1["equipe_a"] == "Jogador 1"
        assert estado_1["equipe_b"] == "Jogador 2"
        assert estado_1["pontos_a"] == 0
        assert estado_1["pontos_b"] == 0

        # Marca 12 pontos para B
        for _ in range(12):
            await client.post(
                f"/api/quadras/{quadra_id}/pontos",
                headers={"x-control-version": "1"},
                json={"equipe": "B"},
            )

        # Reinicia com novos jogadores (duplas)
        resp_reinicio_2 = await client.post(
            f"/api/quadras/{quadra_id}/reiniciar",
            json={
                "time_a_jogador1": "Novo A1",
                "time_a_jogador2": "Novo A2",
                "time_b_jogador1": "Novo B1",
            },
        )
        assert resp_reinicio_2.status_code == 200
        estado_2 = resp_reinicio_2.json()["estado_partida"]
        assert estado_2["equipe_a"] == "Novo A1 / Novo A2"
        assert estado_2["equipe_b"] == "Novo B1"
        assert estado_2["jogadores_a"] == ["Novo A1", "Novo A2"]
        assert estado_2["jogadores_b"] == ["Novo B1"]
