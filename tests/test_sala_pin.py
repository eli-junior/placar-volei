from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
import pytest
from httpx import ASGITransport

from app.config import settings
from app.db import get_db, init_db
from app.main import app
from app.quadras import limpar_quadras_expiradas


@pytest.fixture(autouse=True)
async def setup_test_db(tmp_path: Path):
    db_file = str(tmp_path / "test_sala_pin.db")
    settings.db_path = db_file
    settings.max_quadras = 20
    settings.max_participantes_por_quadra = 20
    settings.quadra_ttl_seconds = 3600
    await init_db(db_file)
    yield


@pytest.mark.asyncio
async def test_criar_quadra_com_codigo_5_digitos_e_admin():
    """
    Ao criar uma quadra com apelido, gera um código de 5 dígitos (10000 a 99999)
    e o criador é registrado imediatamente como ADMIN.
    """
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.post("/api/quadras", json={"apelido": "Eli"})
        assert resp.status_code == 201
        data = resp.json()

        quadra_id = data["id"]
        assert len(quadra_id) == 5
        assert quadra_id.isdigit()
        assert 10000 <= int(quadra_id) <= 99999

        assert "participante" in data
        assert data["participante"]["apelido"] == "Eli"
        assert data["participante"]["papel"] == "ADMIN"

        # Confirma sessão ativa como ADMIN
        resp_eu = await client.get(f"/api/quadras/{quadra_id}/eu")
        assert resp_eu.status_code == 200
        eu = resp_eu.json()["participante"]
        assert eu is not None
        assert eu["papel"] == "ADMIN"
        assert eu["apelido"] == "Eli"


@pytest.mark.asyncio
async def test_ingressar_quadra_via_codigo_entra_como_espectador():
    """
    Usuário que ingressa com o código da quadra entra automaticamente como ESPECTADOR.
    """
    # 1. Criador (Admin)
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client_admin:
        resp_cria = await client_admin.post("/api/quadras", json={"apelido": "Admin"})
        assert resp_cria.status_code == 201
        quadra_id = resp_cria.json()["id"]

    # 2. Outro usuário ingressa com o código
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client_espectador:
        resp_entra = await client_espectador.post(
            f"/api/quadras/{quadra_id}/entrar",
            json={"apelido": "Torcedor 1"},
        )
        assert resp_entra.status_code == 200
        dados_entra = resp_entra.json()
        assert dados_entra["participante"]["papel"] == "ESPECTADOR"
        assert dados_entra["participante"]["apelido"] == "Torcedor 1"

        # Confere status pelo endpoint /eu
        resp_eu = await client_espectador.get(f"/api/quadras/{quadra_id}/eu")
        assert resp_eu.json()["participante"]["papel"] == "ESPECTADOR"


@pytest.mark.asyncio
async def test_limite_maximo_20_quadras():
    """Não permite criar mais do que o limite configurado de quadras simultâneas."""
    settings.max_quadras = 3
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        for i in range(3):
            r = await client.post("/api/quadras", json={"apelido": f"User {i}"})
            assert r.status_code == 201

        # 4ª quadra deve ser bloqueada
        r_bloqueio = await client.post("/api/quadras", json={"apelido": "User 4"})
        assert r_bloqueio.status_code == 400
        assert "limite máximo" in r_bloqueio.json()["detail"].lower()


@pytest.mark.asyncio
async def test_limite_maximo_20_participantes_por_quadra():
    """Não permite mais do que o limite configurado de participantes por quadra."""
    settings.max_participantes_por_quadra = 3
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Cria quadra com Admin (1 participante)
        r_cria = await client.post("/api/quadras", json={"apelido": "Admin"})
        quadra_id = r_cria.json()["id"]

        # Entra 2º participante
        r_p2 = await client.post(
            f"/api/quadras/{quadra_id}/entrar",
            json={"apelido": "P2"},
            headers={"x-session-id": "s-2"},
        )
        assert r_p2.status_code == 200

        # Entra 3º participante (atinge limite de 3)
        r_p3 = await client.post(
            f"/api/quadras/{quadra_id}/entrar",
            json={"apelido": "P3"},
            headers={"x-session-id": "s-3"},
        )
        assert r_p3.status_code == 200

        # 4º participante é rejeitado
        r_p4 = await client.post(
            f"/api/quadras/{quadra_id}/entrar",
            json={"apelido": "P4"},
            headers={"x-session-id": "s-4"},
        )
        assert r_p4.status_code == 400
        assert "limite máximo" in r_p4.json()["detail"].lower()


@pytest.mark.asyncio
async def test_expiracao_quadras_inatividade_apos_1_hora():
    """Quadras sem atualização há mais de 1 hora (TTL) são removidas automaticamente."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        r_cria = await client.post("/api/quadras", json={"apelido": "Admin Expira"})
        quadra_id = r_cria.json()["id"]

        # Força atualizado_em para 2 horas atrás no banco de dados
        duas_horas_atras = (datetime.now(UTC) - timedelta(hours=2)).isoformat()
        with get_db(settings.db_path) as conn:
            conn.execute(
                "UPDATE quadras SET atualizado_em = ? WHERE id = ?",
                (duas_horas_atras, quadra_id),
            )
            conn.commit()

        # Executa limpeza
        removidas = await limpar_quadras_expiradas(settings.db_path)
        assert removidas >= 1

        # Quadra não deve mais existir
        r_get = await client.get(f"/api/quadras/{quadra_id}")
        assert r_get.status_code == 404
