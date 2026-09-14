from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest
from httpx import ASGITransport

from app.config import settings
from app.db import init_db
from app.eventos import Evento, TipoEvento
from app.main import app
from app.projecao import projetar_linha_do_tempo


@pytest.fixture(autouse=True)
async def setup_test_db(tmp_path: Path):
    db_file = str(tmp_path / "test_timeline.db")
    settings.db_path = db_file
    await init_db(db_file)
    yield


def _criar_evento(
    seq: int,
    tipo: str,
    payload: dict,
    partida_id: str = "partida-1",
    autor_id: str | None = None,
) -> Evento:
    return Evento(
        id=f"evt-{seq}",
        quadra_id="quadra-1",
        partida_id=partida_id,
        seq=seq,
        tipo=tipo,
        payload=payload,
        autor_id=autor_id,
        criado_em=datetime.now(UTC).isoformat(),
    )


def test_projetar_linha_do_tempo_partida_recem_iniciada():
    eventos = [
        _criar_evento(
            1,
            TipoEvento.PARTIDA_INICIADA,
            {
                "alvo": 12,
                "vantagem": True,
                "equipe_a": "Time Alfa",
                "equipe_b": "Time Beta",
            },
        )
    ]
    itens = projetar_linha_do_tempo(eventos)
    assert len(itens) == 1
    assert itens[0]["seq"] == 1
    assert itens[0]["tipo"] == TipoEvento.PARTIDA_INICIADA
    assert itens[0]["pontos_a"] == 0
    assert itens[0]["pontos_b"] == 0
    assert itens[0]["anulado"] is False
    assert "12 pts" in itens[0]["descricao"]
    assert "vantagem de 2" in itens[0]["descricao"]


def test_projetar_linha_do_tempo_pontos_e_anulacao():
    apelidos = {"user-1": "Eli", "user-2": "Bob"}
    eventos = [
        _criar_evento(
            1,
            TipoEvento.PARTIDA_INICIADA,
            {"alvo": 12, "vantagem": True, "equipe_a": "Alfa", "equipe_b": "Beta"},
        ),
        _criar_evento(2, TipoEvento.PONTO_MARCADO, {"equipe": "A"}, autor_id="user-1"),
        _criar_evento(3, TipoEvento.PONTO_MARCADO, {"equipe": "B"}, autor_id="user-2"),
        _criar_evento(4, TipoEvento.PONTO_DESFEITO, {"ref_seq": 3}, autor_id="user-1"),
    ]

    itens = projetar_linha_do_tempo(eventos, apelidos)
    assert len(itens) == 4

    # Item 1: Partida iniciada
    assert itens[0]["pontos_a"] == 0
    assert itens[0]["pontos_b"] == 0

    # Item 2: Ponto A
    assert itens[1]["seq"] == 2
    assert itens[1]["equipe"] == "A"
    assert itens[1]["autor_apelido"] == "Eli"
    assert itens[1]["pontos_a"] == 1
    assert itens[1]["pontos_b"] == 0
    assert itens[1]["anulado"] is False

    # Item 3: Ponto B (que foi desfeito no passo 4)
    assert itens[2]["seq"] == 3
    assert itens[2]["equipe"] == "B"
    assert itens[2]["autor_apelido"] == "Bob"
    assert itens[2]["pontos_a"] == 1
    assert itens[2]["pontos_b"] == 1
    assert itens[2]["anulado"] is True  # Marcado como anulado!

    # Item 4: Desfazer Ponto B
    assert itens[3]["seq"] == 4
    assert itens[3]["tipo"] == TipoEvento.PONTO_DESFEITO
    assert itens[3]["ref_seq"] == 3
    assert itens[3]["autor_apelido"] == "Eli"
    assert itens[3]["pontos_a"] == 1
    assert itens[3]["pontos_b"] == 0  # Revertido de volta para 1 x 0!
    assert "Beta anulado" in itens[3]["descricao"]


@pytest.mark.asyncio
async def test_api_endpoint_linha_do_tempo():
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # 1. Cria arena e quadra
        res_arena = await client.post("/api/arenas", json={"nome": "Arena Timeline"})
        arena_id = res_arena.json()["id"]

        res_quadra = await client.post(
            f"/api/arenas/{arena_id}/quadras", json={"nome": "Quadra Principal"}
        )
        quadra_id = res_quadra.json()["id"]

        # 2. Entra como Admin
        res_entrar = await client.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Eli Admin"}
        )
        assert res_entrar.status_code == 200

        # 3. Consulta linha do tempo inicial
        res_lt = await client.get(f"/api/quadras/{quadra_id}/linha-do-tempo")
        assert res_lt.status_code == 200
        data = res_lt.json()
        assert "itens" in data
        assert len(data["itens"]) == 1
        assert data["itens"][0]["tipo"] == TipoEvento.PARTIDA_INICIADA

        # 4. Marca ponto para A e ponto para B
        await client.post(f"/api/quadras/{quadra_id}/pontos", json={"equipe": "A"})
        await client.post(f"/api/quadras/{quadra_id}/pontos", json={"equipe": "B"})

        # 5. Desfaz último ponto (B)
        res_undo = await client.post(f"/api/quadras/{quadra_id}/desfazer")
        assert res_undo.status_code == 200
        assert "linha_do_tempo" in res_undo.json()

        # 6. Reconsulta linha do tempo
        res_lt2 = await client.get(f"/api/quadras/{quadra_id}/linha-do-tempo")
        assert res_lt2.status_code == 200
        itens = res_lt2.json()["itens"]
        assert len(itens) == 4
        # Ponto B (seq 3) deve constar como anulado
        assert itens[2]["anulado"] is True
        # Último item (desfazer) deve ter placar 1x0
        assert itens[3]["pontos_a"] == 1
        assert itens[3]["pontos_b"] == 0


@pytest.mark.asyncio
async def test_api_linha_do_tempo_quadra_nao_encontrada():
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.get("/api/quadras/quadra-fantasma/linha-do-tempo")
        assert res.status_code == 404
