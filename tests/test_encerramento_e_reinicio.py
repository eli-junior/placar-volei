import sqlite3
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
    db_file = str(tmp_path / "test_us4.db")
    settings.db_path = db_file
    await init_db(db_file)
    yield


@pytest.mark.asyncio
async def test_vitoria_direta_e_partida_encerrada():
    """Chegada a 12x10 com alvo 12 grava PARTIDA_ENCERRADA e bloqueia novos pontos."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Cria quadra com apelido Eli
        resp_q = await client.post(
            "/api/quadras", json={"nome": "Quadra Central", "apelido": "Eli"}
        )
        assert resp_q.status_code == 201
        data_q = resp_q.json()
        quadra_id = data_q["id"]
        partida_1_id = data_q["partida_id"]

        # Equipe A marca 11 pontos
        for _ in range(11):
            r = await client.post(
                f"/api/quadras/{quadra_id}/pontos",
                headers={"x-control-version": "1"},
                json={"equipe": "A"},
            )
            assert r.status_code == 201

        # Equipe B marca 10 pontos
        for _ in range(10):
            r = await client.post(
                f"/api/quadras/{quadra_id}/pontos",
                headers={"x-control-version": "1"},
                json={"equipe": "B"},
            )
            assert r.status_code == 201

        # Confere que em 11x10 a partida continua em andamento
        resp_status = await client.get(f"/api/quadras/{quadra_id}/partida")
        assert resp_status.json()["estado_partida"]["encerrada"] is False

        # Equipe A marca o 12º ponto (12x10)
        resp_vitoria = await client.post(
            f"/api/quadras/{quadra_id}/pontos",
            headers={"x-control-version": "1"},
            json={"equipe": "A"},
        )
        assert resp_vitoria.status_code == 201
        data_vitoria = resp_vitoria.json()

        assert data_vitoria["estado_partida"]["pontos_a"] == 12
        assert data_vitoria["estado_partida"]["pontos_b"] == 10
        assert data_vitoria["estado_partida"]["encerrada"] is True
        assert data_vitoria["estado_partida"]["vencedor"] == "A"

        # Confere se o evento PARTIDA_ENCERRADA foi gravado no log
        eventos = await carregar_eventos(settings.db_path, partida_1_id)
        tipos = [e.tipo for e in eventos]
        assert TipoEvento.PARTIDA_ENCERRADA in tipos
        evento_fim = next(e for e in eventos if e.tipo == TipoEvento.PARTIDA_ENCERRADA)
        assert evento_fim.payload["vencedor"] == "A"
        assert evento_fim.payload["pontos_a"] == 12
        assert evento_fim.payload["pontos_b"] == 10

        # Confere status no banco
        with sqlite3.connect(settings.db_path) as conn:
            conn.row_factory = sqlite3.Row
            p_row = conn.execute(
                "SELECT status, encerrado_em FROM partidas WHERE id = ?",
                (partida_1_id,),
            ).fetchone()
            assert p_row["status"] == "ENCERRADA"
            assert p_row["encerrado_em"] is not None

        # Tentar marcar mais pontos deve retornar HTTP 400
        resp_extra = await client.post(
            f"/api/quadras/{quadra_id}/pontos",
            headers={"x-control-version": "1"},
            json={"equipe": "A"},
        )
        assert resp_extra.status_code == 400
        assert "A partida já está encerrada" in resp_extra.json()["detail"]


@pytest.mark.asyncio
async def test_vantagem_apos_empate_e_encerramento():
    """Em 11x11, 12x11 não encerra; encerra apenas com diferença de 2 pontos (14x12)."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp_q = await client.post(
            "/api/quadras", json={"nome": "Quadra Vantagem", "apelido": "Eli"}
        )
        quadra_id = resp_q.json()["id"]

        # 11 pontos alternados para cada equipe (11x11)
        for _ in range(11):
            await client.post(
                f"/api/quadras/{quadra_id}/pontos",
                headers={"x-control-version": "1"},
                json={"equipe": "A"},
            )
            await client.post(
                f"/api/quadras/{quadra_id}/pontos",
                headers={"x-control-version": "1"},
                json={"equipe": "B"},
            )

        # Equipe A faz 12x11 -> NÃO encerra pela exigência de vantagem de 2
        resp_12_11 = await client.post(
            f"/api/quadras/{quadra_id}/pontos",
            headers={"x-control-version": "1"},
            json={"equipe": "A"},
        )
        assert resp_12_11.json()["estado_partida"]["encerrada"] is False

        # Equipe B empata em 12x12
        await client.post(
            f"/api/quadras/{quadra_id}/pontos",
            headers={"x-control-version": "1"},
            json={"equipe": "B"},
        )

        # Equipe A faz 13x12 -> NÃO encerra
        resp_13_12 = await client.post(
            f"/api/quadras/{quadra_id}/pontos",
            headers={"x-control-version": "1"},
            json={"equipe": "A"},
        )
        assert resp_13_12.json()["estado_partida"]["encerrada"] is False

        # Equipe A faz 14x12 -> Diferença de 2 pontos atingida: ENCERRA!
        resp_14_12 = await client.post(
            f"/api/quadras/{quadra_id}/pontos",
            headers={"x-control-version": "1"},
            json={"equipe": "A"},
        )
        data = resp_14_12.json()
        assert data["estado_partida"]["pontos_a"] == 14
        assert data["estado_partida"]["pontos_b"] == 12
        assert data["estado_partida"]["encerrada"] is True
        assert data["estado_partida"]["vencedor"] == "A"


@pytest.mark.asyncio
async def test_desfazer_ponto_da_vitoria_reabre_partida():
    """Desfazer o ponto da vitória reabre a partida, volta para 11x10 e reabilita marcação."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp_q = await client.post(
            "/api/quadras", json={"nome": "Quadra Reversão", "apelido": "Eli"}
        )
        quadra_id = resp_q.json()["id"]
        partida_id = resp_q.json()["partida_id"]

        for _ in range(11):
            await client.post(
                f"/api/quadras/{quadra_id}/pontos",
                headers={"x-control-version": "1"},
                json={"equipe": "A"},
            )
        for _ in range(10):
            await client.post(
                f"/api/quadras/{quadra_id}/pontos",
                headers={"x-control-version": "1"},
                json={"equipe": "B"},
            )

        # Ponto da vitória (12x10)
        await client.post(
            f"/api/quadras/{quadra_id}/pontos",
            headers={"x-control-version": "1"},
            json={"equipe": "A"},
        )

        # Desfaz o ponto da vitória
        resp_desfazer = await client.post(
            f"/api/quadras/{quadra_id}/desfazer",
            headers={"x-control-version": "1"},
        )
        assert resp_desfazer.status_code == 200
        data_desfeito = resp_desfazer.json()
        assert data_desfeito["estado_partida"]["pontos_a"] == 11
        assert data_desfeito["estado_partida"]["pontos_b"] == 10
        assert data_desfeito["estado_partida"]["encerrada"] is False
        assert data_desfeito["estado_partida"]["vencedor"] is None

        # Banco deve refletir status EM_ANDAMENTO novamente
        with sqlite3.connect(settings.db_path) as conn:
            conn.row_factory = sqlite3.Row
            p_row = conn.execute(
                "SELECT status, encerrado_em FROM partidas WHERE id = ?", (partida_id,)
            ).fetchone()
            assert p_row["status"] == "EM_ANDAMENTO"
            assert p_row["encerrado_em"] is None

        # Agora é possível marcar ponto novamente sem erro 400
        resp_novo_ponto = await client.post(
            f"/api/quadras/{quadra_id}/pontos",
            headers={"x-control-version": "1"},
            json={"equipe": "B"},
        )
        assert resp_novo_ponto.status_code == 201
        assert resp_novo_ponto.json()["estado_partida"]["pontos_b"] == 11


@pytest.mark.asyncio
async def test_reiniciar_partida_sob_demanda():
    """Ao encerrar a partida, o admin pode iniciar uma nova partida em 0x0 na mesma quadra."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp_q = await client.post(
            "/api/quadras", json={"nome": "Quadra Reinício", "apelido": "Eli"}
        )
        quadra_id = resp_q.json()["id"]
        partida_1_id = resp_q.json()["partida_id"]

        # Tentar reiniciar com a partida em andamento deve falhar com HTTP 400
        resp_reiniciar_cedo = await client.post(
            f"/api/quadras/{quadra_id}/reiniciar",
            headers={"x-control-version": "1"},
        )
        assert resp_reiniciar_cedo.status_code == 400
        assert "ainda não foi encerrada" in resp_reiniciar_cedo.json()["detail"]

        # Leva a partida até 12x0
        for _ in range(12):
            await client.post(
                f"/api/quadras/{quadra_id}/pontos",
                headers={"x-control-version": "1"},
                json={"equipe": "A"},
            )

        # Confere que a partida 1 encerrou
        resp_partida_1 = await client.get(f"/api/quadras/{quadra_id}/partida")
        assert resp_partida_1.json()["estado_partida"]["encerrada"] is True

        # Reinicia a partida sob demanda
        resp_reinicio = await client.post(
            f"/api/quadras/{quadra_id}/reiniciar",
            headers={"x-control-version": "1"},
        )
        assert resp_reinicio.status_code == 200
        data_reinicio = resp_reinicio.json()

        partida_2_id = data_reinicio["partida_id"]
        assert partida_2_id != partida_1_id
        assert data_reinicio["estado_partida"]["pontos_a"] == 0
        assert data_reinicio["estado_partida"]["pontos_b"] == 0
        assert data_reinicio["estado_partida"]["encerrada"] is False
        assert data_reinicio["estado_partida"]["alvo"] == 12
        assert data_reinicio["estado_partida"]["vantagem"] is True

        # Confere no banco que a partida 1 está arquivada e a partida 2 está ativa
        with sqlite3.connect(settings.db_path) as conn:
            conn.row_factory = sqlite3.Row
            p1 = conn.execute(
                "SELECT status FROM partidas WHERE id = ?", (partida_1_id,)
            ).fetchone()
            p2 = conn.execute(
                "SELECT status FROM partidas WHERE id = ?", (partida_2_id,)
            ).fetchone()
            assert p1["status"] == "ENCERRADA"
            assert p2["status"] == "EM_ANDAMENTO"

        # Segunda chamada a reiniciar com a nova partida em andamento é rejeitada
        resp_reinicio_repetido = await client.post(
            f"/api/quadras/{quadra_id}/reiniciar",
            headers={"x-control-version": "1"},
        )
        assert resp_reinicio_repetido.status_code == 400
        assert "ainda não foi encerrada" in resp_reinicio_repetido.json()["detail"]

        # Novo ponto é marcado na partida 2
        resp_ponto_novo = await client.post(
            f"/api/quadras/{quadra_id}/pontos",
            headers={"x-control-version": "1"},
            json={"equipe": "A"},
        )
        assert resp_ponto_novo.status_code == 201
        assert resp_ponto_novo.json()["estado_partida"]["pontos_a"] == 1
        assert resp_ponto_novo.json()["partida_id"] == partida_2_id


@pytest.mark.asyncio
async def test_encerramento_com_teto_atingido():
    """Com teto configurado em 15, em 14x14 o 15º ponto encerra sem necessidade de 2 pontos de vantagem."""
    from app.eventos import append_evento

    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp_q = await client.post(
            "/api/quadras", json={"nome": "Quadra Teto", "apelido": "Eli"}
        )
        quadra_id = resp_q.json()["id"]
        partida_id = resp_q.json()["partida_id"]

        # Altera regra para definir teto em 15
        await append_evento(
            settings.db_path,
            quadra_id=quadra_id,
            partida_id=partida_id,
            tipo=TipoEvento.REGRA_ALTERADA,
            payload={"alvo": 12, "vantagem": True, "teto": 15},
        )

        # 14 pontos para cada equipe (14x14)
        for _ in range(14):
            await client.post(
                f"/api/quadras/{quadra_id}/pontos",
                headers={"x-control-version": "1"},
                json={"equipe": "A"},
            )
            await client.post(
                f"/api/quadras/{quadra_id}/pontos",
                headers={"x-control-version": "1"},
                json={"equipe": "B"},
            )

        # Equipe A marca o 15º ponto (15x14) -> TETO ATINGIDO: ENCERRA!
        resp_teto = await client.post(
            f"/api/quadras/{quadra_id}/pontos",
            headers={"x-control-version": "1"},
            json={"equipe": "A"},
        )
        data = resp_teto.json()
        assert data["estado_partida"]["pontos_a"] == 15
        assert data["estado_partida"]["pontos_b"] == 14
        assert data["estado_partida"]["encerrada"] is True
        assert data["estado_partida"]["vencedor"] == "A"


@pytest.mark.asyncio
async def test_websocket_continuidade_ao_reiniciar():
    """Conexão WebSocket da quadra permanece viva e recebe o snapshot 0x0 ao reiniciar partida."""
    from starlette.testclient import TestClient

    with TestClient(app) as test_client:
        # Cria quadra com apelido
        res = test_client.post(
            "/api/quadras", json={"nome": "Quadra WS", "apelido": "Eli"}
        )
        assert res.status_code == 201
        data_q = res.json()
        quadra_id = data_q["id"]
        partida_1_id = data_q["partida_id"]

        with test_client.websocket_connect(f"/ws/{quadra_id}") as ws:
            # Recebe ESTADO_INICIAL
            msg_init = ws.receive_json()
            assert msg_init["tipo"] == "ESTADO_INICIAL"
            assert msg_init["payload"]["partida_id"] == partida_1_id

            # Consome a presença inicial
            ws.receive_json()

            # Marca 12 pontos para encerrar
            for i in range(12):
                r = test_client.post(
                    f"/api/quadras/{quadra_id}/pontos",
                    headers={"x-control-version": "1"},
                    json={"equipe": "A"},
                )
                assert r.status_code == 201
                # Consome o broadcast no websocket
                msg_ponto = ws.receive_json()
                assert msg_ponto["tipo"] == "PLACAR_ATUALIZADO"

            # Confere que o último broadcast marcou encerrada=True
            assert msg_ponto["payload"]["estado_partida"]["encerrada"] is True

            # Reinicia a partida
            r_reinicio = test_client.post(
                f"/api/quadras/{quadra_id}/reiniciar",
                headers={"x-control-version": "1"},
            )
            assert r_reinicio.status_code == 200

            # O WebSocket ainda conectado deve receber o broadcast com a nova partida em 0x0
            msg_nova = ws.receive_json()
            assert msg_nova["tipo"] == "PLACAR_ATUALIZADO"
            assert msg_nova["payload"]["partida_id"] != partida_1_id
            assert msg_nova["payload"]["estado_partida"]["pontos_a"] == 0
            assert msg_nova["payload"]["estado_partida"]["pontos_b"] == 0
            assert msg_nova["payload"]["estado_partida"]["encerrada"] is False
