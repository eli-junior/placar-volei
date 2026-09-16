from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.db import init_db
from app.main import app
from app.quadras import criar_quadra_sync


@pytest.fixture(autouse=True)
async def setup_test_db(tmp_path: Path):
    db_file = str(tmp_path / "test_regras.db")
    settings.db_path = db_file
    await init_db(db_file)
    yield


@pytest.mark.asyncio
async def test_criar_quadra_com_regras_padrao():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.post(
            "/api/quadras",
            json={
                "apelido": "Criador",
                "time_a_jogador1": "Alice",
                "time_b_jogador1": "Bob",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        quadra_id = data["id"]

        resp_p = await ac.get(f"/api/quadras/{quadra_id}/partida")
        assert resp_p.status_code == 200
        estado = resp_p.json()["estado_partida"]
        assert estado["alvo"] == 12
        assert estado["vantagem"] is True
        assert estado["teto"] is None


@pytest.mark.asyncio
async def test_criar_quadra_com_regras_customizadas_sem_vantagem():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.post(
            "/api/quadras",
            json={
                "apelido": "Juiz",
                "time_a_jogador1": "Jogador A",
                "time_b_jogador1": "Jogador B",
                "alvo": 15,
                "vantagem": False,
            },
        )
        assert resp.status_code == 201
        quadra_id = resp.json()["id"]

        resp_p = await ac.get(f"/api/quadras/{quadra_id}/partida")
        estado = resp_p.json()["estado_partida"]
        assert estado["alvo"] == 15
        assert estado["vantagem"] is False
        assert estado["teto"] is None

        resp_lt = await ac.get(f"/api/quadras/{quadra_id}/linha-do-tempo")
        assert resp_lt.status_code == 200
        lt = resp_lt.json()["itens"]
        assert lt[0]["descricao"] == "Partida iniciada até 15 pts"


@pytest.mark.asyncio
async def test_vitoria_sem_vantagem_ao_atingir_alvo_exato():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.post(
            "/api/quadras",
            json={
                "apelido": "Juiz",
                "time_a_jogador1": "Time A",
                "time_b_jogador1": "Time B",
                "alvo": 3,
                "vantagem": False,
            },
        )
        quadra_id = resp.json()["id"]
        headers = {"x-control-version": "1"}

        # 2 x 2
        await ac.post(
            f"/api/quadras/{quadra_id}/pontos", headers=headers, json={"equipe": "A"}
        )
        await ac.post(
            f"/api/quadras/{quadra_id}/pontos", headers=headers, json={"equipe": "B"}
        )
        await ac.post(
            f"/api/quadras/{quadra_id}/pontos", headers=headers, json={"equipe": "A"}
        )
        await ac.post(
            f"/api/quadras/{quadra_id}/pontos", headers=headers, json={"equipe": "B"}
        )

        # Ponto decisivo para A: 3 x 2
        resp_ponto = await ac.post(
            f"/api/quadras/{quadra_id}/pontos", headers=headers, json={"equipe": "A"}
        )
        assert resp_ponto.status_code == 201
        estado = resp_ponto.json()["estado_partida"]
        assert estado["pontos_a"] == 3
        assert estado["pontos_b"] == 2
        assert estado["encerrada"] is True
        assert estado["vencedor"] == "A"


@pytest.mark.asyncio
async def test_criar_quadra_com_teto_e_encerramento_por_teto():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.post(
            "/api/quadras",
            json={
                "apelido": "Juiz",
                "time_a_jogador1": "A1",
                "time_b_jogador1": "B1",
                "alvo": 3,
                "vantagem": True,
                "teto": 4,
            },
        )
        assert resp.status_code == 201
        quadra_id = resp.json()["id"]
        headers = {"x-control-version": "1"}

        resp_lt = await ac.get(f"/api/quadras/{quadra_id}/linha-do-tempo")
        assert resp_lt.status_code == 200
        lt = resp_lt.json()["itens"]
        assert (
            lt[0]["descricao"]
            == "Partida iniciada até 3 pts com vantagem de 2 (teto 4)"
        )

        # 2 x 2
        await ac.post(
            f"/api/quadras/{quadra_id}/pontos", headers=headers, json={"equipe": "A"}
        )
        await ac.post(
            f"/api/quadras/{quadra_id}/pontos", headers=headers, json={"equipe": "B"}
        )
        await ac.post(
            f"/api/quadras/{quadra_id}/pontos", headers=headers, json={"equipe": "A"}
        )
        await ac.post(
            f"/api/quadras/{quadra_id}/pontos", headers=headers, json={"equipe": "B"}
        )

        # 3 x 2 (atingiu o alvo, mas tem vantagem e diferença é 1 -> não encerra)
        resp_3_2 = await ac.post(
            f"/api/quadras/{quadra_id}/pontos", headers=headers, json={"equipe": "A"}
        )
        assert resp_3_2.json()["estado_partida"]["encerrada"] is False

        # 3 x 3
        await ac.post(
            f"/api/quadras/{quadra_id}/pontos", headers=headers, json={"equipe": "B"}
        )

        # 4 x 3 (atingiu o teto 4 com 1 ponto de vantagem -> encerra imediatamente!)
        resp_4_3 = await ac.post(
            f"/api/quadras/{quadra_id}/pontos", headers=headers, json={"equipe": "A"}
        )
        estado = resp_4_3.json()["estado_partida"]
        assert estado["pontos_a"] == 4
        assert estado["pontos_b"] == 3
        assert estado["encerrada"] is True
        assert estado["vencedor"] == "A"


@pytest.mark.asyncio
async def test_rejeicao_quando_teto_menor_que_alvo():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.post(
            "/api/quadras",
            json={
                "apelido": "Juiz",
                "time_a_jogador1": "A1",
                "time_b_jogador1": "B1",
                "alvo": 15,
                "vantagem": True,
                "teto": 12,
            },
        )
        assert resp.status_code == 422
        assert (
            resp.json()["detail"]
            == "O teto da vantagem não pode ser menor que a pontuação-alvo."
        )


def test_criar_quadra_sync_valida_teto_menor_que_alvo():
    with pytest.raises(
        ValueError, match="O teto da vantagem não pode ser menor que a pontuação-alvo."
    ):
        criar_quadra_sync(settings.db_path, alvo=21, teto=20)


@pytest.mark.asyncio
async def test_preservacao_de_regras_ao_reiniciar():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.post(
            "/api/quadras",
            json={
                "apelido": "Juiz",
                "time_a_jogador1": "Time A",
                "time_b_jogador1": "Time B",
                "alvo": 2,
                "vantagem": False,
            },
        )
        quadra_id = resp.json()["id"]
        headers = {"x-control-version": "1"}

        # Encerrar partida 2 x 0
        await ac.post(
            f"/api/quadras/{quadra_id}/pontos", headers=headers, json={"equipe": "A"}
        )
        resp_fim = await ac.post(
            f"/api/quadras/{quadra_id}/pontos", headers=headers, json={"equipe": "A"}
        )
        assert resp_fim.json()["estado_partida"]["encerrada"] is True

        # Reiniciar partida
        resp_reinicio = await ac.post(
            f"/api/quadras/{quadra_id}/reiniciar", headers=headers
        )
        assert resp_reinicio.status_code == 200
        novo_estado = resp_reinicio.json()["estado_partida"]
        assert novo_estado["alvo"] == 2
        assert novo_estado["vantagem"] is False
        assert novo_estado["teto"] is None
        assert novo_estado["pontos_a"] == 0
        assert novo_estado["pontos_b"] == 0
        assert novo_estado["encerrada"] is False


@pytest.mark.asyncio
async def test_admin_configura_duplas_e_regras_em_andamento():
    """Admin cria sala limpa e configura as duplas e regras depois de entrar."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Onboarding ultralight: apenas apelido do criador
        resp = await ac.post("/api/quadras", json={"apelido": "Admin"})
        assert resp.status_code == 201
        quadra_id = resp.json()["id"]

        # Admin ajusta as duplas e a pontuação-alvo
        resp_conf = await ac.post(
            f"/api/quadras/{quadra_id}/configurar",
            json={
                "time_a_jogador1": "Carlos",
                "time_a_jogador2": "Daniel",
                "time_b_jogador1": "Roberto",
                "time_b_jogador2": "Eduardo",
                "alvo": 15,
                "vantagem": True,
            },
        )
        assert resp_conf.status_code == 200
        estado = resp_conf.json()["estado_partida"]
        assert estado["equipe_a"] == "Carlos / Daniel"
        assert estado["equipe_b"] == "Roberto / Eduardo"
        assert list(estado["jogadores_a"]) == ["Carlos", "Daniel"]
        assert list(estado["jogadores_b"]) == ["Roberto", "Eduardo"]
        assert estado["alvo"] == 15
        assert estado["vantagem"] is True


@pytest.mark.asyncio
async def test_reiniciar_com_novas_duplas_e_regras():
    """Ao reiniciar uma partida encerrada, permite definir as próximas duplas na mesma sala."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.post(
            "/api/quadras",
            json={"apelido": "Juiz", "alvo": 1, "vantagem": False},
        )
        quadra_id = resp.json()["id"]

        # Encerra partida
        await ac.post(
            f"/api/quadras/{quadra_id}/pontos",
            headers={"x-control-version": "1"},
            json={"equipe": "A"},
        )

        # Reinicia informando as duplas da próxima rodada e novo alvo
        resp_reinicio = await ac.post(
            f"/api/quadras/{quadra_id}/reiniciar",
            json={
                "time_a_jogador1": "Fernanda",
                "time_b_jogador1": "Gabriela",
                "alvo": 21,
                "vantagem": True,
            },
        )
        assert resp_reinicio.status_code == 200
        novo_estado = resp_reinicio.json()["estado_partida"]
        assert novo_estado["equipe_a"] == "Fernanda"
        assert novo_estado["equipe_b"] == "Gabriela"
        assert novo_estado["alvo"] == 21
        assert novo_estado["vantagem"] is True
        assert novo_estado["pontos_a"] == 0
        assert novo_estado["pontos_b"] == 0
        assert novo_estado["encerrada"] is False
