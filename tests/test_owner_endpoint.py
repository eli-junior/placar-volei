from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.db import init_db
from app.main import app
from app.quadras import gerar_codigo_mestre_sync
from app.rate_limit import RateLimiter, owner_rate_limiter


@pytest.fixture(autouse=True)
async def setup_test_db(tmp_path: Path):
    db_file = str(tmp_path / "test_owner.db")
    settings.db_path = db_file
    owner_rate_limiter.resetar()
    await init_db(db_file)
    yield
    owner_rate_limiter.resetar()


@pytest.mark.asyncio
async def test_owner_endpoint_sem_segredo_retorna_404():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp1 = await ac.get("/api/owner/quadras")
        assert resp1.status_code == 404

        resp2 = await ac.get("/owner/quadras")
        assert resp2.status_code == 404


@pytest.mark.asyncio
async def test_owner_endpoint_segredo_invalido_retorna_404():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp1 = await ac.get(
            "/api/owner/quadras", headers={"x-owner-secret": "segredo-errado"}
        )
        assert resp1.status_code == 404

        resp2 = await ac.get(
            "/api/owner/quadras",
            headers={"Authorization": "Bearer token-incorreto"},
        )
        assert resp2.status_code == 404


@pytest.mark.asyncio
async def test_owner_endpoint_autenticado_com_sucesso():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Cria uma quadra para teste
        resp_cria = await ac.post(
            "/api/quadras",
            json={
                "nome": "Quadra VIP",
                "apelido": "Admin",
                "time_a_jogador1": "Ana",
                "time_b_jogador1": "Beto",
            },
        )
        assert resp_cria.status_code == 201
        quadra_criada = resp_cria.json()
        quadra_id = quadra_criada["id"]

        # 1. Consulta com header x-owner-secret
        resp_owner = await ac.get(
            "/api/owner/quadras",
            headers={"x-owner-secret": settings.owner_secret},
        )
        assert resp_owner.status_code == 200
        dados = resp_owner.json()
        assert "quadras" in dados
        quadras = dados["quadras"]
        assert len(quadras) >= 1

        quadra_alvo = next((q for q in quadras if q["id"] == quadra_id), None)
        assert quadra_alvo is not None
        assert quadra_alvo["nome"] == "Quadra VIP"
        assert "codigo_mestre" in quadra_alvo
        assert len(quadra_alvo["codigo_mestre"]) == 4
        assert quadra_alvo["codigo_mestre"].isdigit()
        assert quadra_alvo["total_participantes"] == 1
        assert quadra_alvo["participantes"][0]["apelido"] == "Admin"
        assert quadra_alvo["estado_partida"]["pontos_a"] == 0

        # 2. Consulta via rota raiz com Authorization: Bearer
        resp_root = await ac.get(
            "/owner/quadras",
            headers={"Authorization": f"Bearer {settings.owner_secret}"},
        )
        assert resp_root.status_code == 200
        dados_root = resp_root.json()
        assert len(dados_root["quadras"]) >= 1


@pytest.mark.asyncio
async def test_owner_endpoint_rate_limit_bloqueia_apos_5_tentativas():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # 5 requisições seguidas com segredo inválido -> devem retornar 404
        for i in range(5):
            resp = await ac.get(
                "/api/owner/quadras",
                headers={"x-owner-secret": f"senha-errada-{i}"},
            )
            assert resp.status_code == 404

        # A 6ª requisição (mesmo com segredo correto) deve ser bloqueada com 429
        resp_bloqueado = await ac.get(
            "/api/owner/quadras",
            headers={"x-owner-secret": settings.owner_secret},
        )
        assert resp_bloqueado.status_code == 429
        assert "Retry-After" in resp_bloqueado.headers
        assert int(resp_bloqueado.headers["Retry-After"]) > 0


@pytest.mark.asyncio
async def test_rotas_publicas_nao_vazam_codigo_mestre():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp_cria = await ac.post(
            "/api/quadras",
            json={
                "nome": "Quadra Pública",
                "apelido": "Criador",
                "time_a_jogador1": "Jogador 1",
                "time_b_jogador1": "Jogador 2",
            },
        )
        assert resp_cria.status_code == 201
        data_cria = resp_cria.json()
        quadra_id = data_cria["id"]

        # Resposta de criação não deve conter codigo_mestre
        assert "codigo_mestre" not in data_cria

        # Listagem pública GET /api/quadras
        resp_list = await ac.get("/api/quadras")
        assert resp_list.status_code == 200
        for q in resp_list.json()["quadras"]:
            assert "codigo_mestre" not in q

        # Consulta de quadra GET /api/quadras/{id}
        resp_q = await ac.get(f"/api/quadras/{quadra_id}")
        assert resp_q.status_code == 200
        assert "codigo_mestre" not in resp_q.json()

        # Consulta de partida GET /api/quadras/{id}/partida
        resp_partida = await ac.get(f"/api/quadras/{quadra_id}/partida")
        assert resp_partida.status_code == 200
        assert "codigo_mestre" not in resp_partida.json()


def test_codigo_mestre_formato_4_digitos():
    for _ in range(50):
        cod = gerar_codigo_mestre_sync()
        assert len(cod) == 4
        assert cod.isdigit()
        assert 0 <= int(cod) <= 9999


def test_rate_limiter_unitario():
    rl = RateLimiter(max_tentativas=3, janela_segundos=10.0, bloqueio_segundos=5.0)
    chave = "teste-ip"

    # Tentativa 1 e 2
    bloqueado, _ = rl.esta_bloqueado(chave, agora=100.0)
    assert not bloqueado
    foi_bloqueado, _ = rl.registrar_falha(chave, agora=100.0)
    assert not foi_bloqueado

    foi_bloqueado, _ = rl.registrar_falha(chave, agora=101.0)
    assert not foi_bloqueado

    # Tentativa 3 atinge o limite
    foi_bloqueado, segundos = rl.registrar_falha(chave, agora=102.0)
    assert foi_bloqueado
    assert segundos == 5

    # Agora está bloqueado
    bloqueado, restante = rl.esta_bloqueado(chave, agora=103.0)
    assert bloqueado
    assert restante == 5  # 107 - 103 + 1 = 5

    # Após expirar o tempo de bloqueio (108.0)
    bloqueado, _ = rl.esta_bloqueado(chave, agora=108.0)
    assert not bloqueado

    # Sucesso limpa as tentativas
    rl.registrar_sucesso(chave)
    bloqueado, _ = rl.esta_bloqueado(chave, agora=109.0)
    assert not bloqueado
