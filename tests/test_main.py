import httpx
import pytest
from httpx import ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_serve_spa_root():
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert "Placar Vôlei" in response.text
        assert '<div id="app"></div>' in response.text


@pytest.mark.asyncio
async def test_serve_spa_quadra_route():
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/quadra/qualquer-id-de-quadra")
        assert response.status_code == 200
        assert "Placar Vôlei" in response.text
