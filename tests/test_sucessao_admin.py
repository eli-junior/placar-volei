from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.config import settings
from app.db import get_db, init_db
from app.eventos import carregar_eventos_sync
from app.main import app
from app.sucessao import verificar_sucessao_quadra_sync


@pytest.fixture(autouse=True)
async def setup_test_db(tmp_path: Path):
    db_file = str(tmp_path / "test_sucessao.db")
    settings.db_path = db_file
    await init_db(db_file)
    yield


def test_sucessao_promove_controlador_mais_antigo():
    """Admin ausente há mais de 120s: o controlador mais antigo online é promovido a ADMIN."""
    with (
        TestClient(app) as client_a,
        TestClient(app) as client_b,
        TestClient(app) as client_c,
    ):
        # 1. Admin A cria a quadra
        resp_a = client_a.post(
            "/api/quadras", json={"nome": "Quadra Sucessão", "apelido": "Admin A"}
        )
        assert resp_a.status_code == 201
        data_a = resp_a.json()
        quadra_id = data_a["id"]
        a_id = data_a["participante"]["id"]

        # 2. B entra primeiro e é promovido a controlador
        resp_b = client_b.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Controlador B"}
        )
        b_id = resp_b.json()["participante"]["id"]
        client_a.post(f"/api/quadras/{quadra_id}/participantes/{b_id}/promover")

        # 3. C entra depois e é promovido a controlador
        resp_c = client_c.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Controlador C"}
        )
        c_id = resp_c.json()["participante"]["id"]
        client_a.post(f"/api/quadras/{quadra_id}/participantes/{c_id}/promover")

        # Simula que Admin A ficou offline há 130 segundos
        antigo_visto = (datetime.now(UTC) - timedelta(seconds=130)).isoformat()
        with get_db(settings.db_path) as conn:
            conn.execute(
                "UPDATE participantes SET ultimo_visto_em = ? WHERE id = ?",
                (antigo_visto, a_id),
            )
            # Garante que controle estava com A
            conn.execute(
                "UPDATE quadras SET controle_id = ? WHERE id = ?", (a_id, quadra_id)
            )
            conn.commit()

        # 4. Executa verificação com B e C online e A offline
        online_ids = {b_id, c_id}
        snap = verificar_sucessao_quadra_sync(
            settings.db_path, quadra_id, online_ids, timeout_seconds=120
        )

        assert snap is not None
        participantes_map = {p["id"]: p for p in snap["participantes"]}

        # B (mais antigo) virou ADMIN
        assert participantes_map[b_id]["papel"] == "ADMIN"
        # A virou CONTROLADOR
        assert participantes_map[a_id]["papel"] == "CONTROLADOR"
        # C continua CONTROLADOR
        assert participantes_map[c_id]["papel"] == "CONTROLADOR"
        # Controle ativo foi transferido para o novo admin B
        assert snap["quadra"]["controle_id"] == b_id

        # 5. Verifica log de eventos e linha do tempo
        eventos = carregar_eventos_sync(settings.db_path, snap["partida_id"])
        evento_sucessao = eventos[-1]
        assert evento_sucessao.tipo == "ADMIN_SUCEDIDO"
        assert evento_sucessao.payload["antigo_admin_id"] == a_id
        assert evento_sucessao.payload["novo_admin_id"] == b_id
        assert evento_sucessao.payload["novo_admin_apelido"] == "Controlador B"

        # Linha do tempo projeta a narrativa
        ultimo_item_lt = snap["linha_do_tempo"][-1]
        assert (
            "Controlador B assumiu a administração por sucessão (ausência de Admin A)"
            in ultimo_item_lt["descricao"]
        )


def test_sucessao_retorno_admin_original_como_controlador():
    """Admin original reconecta após sucessão e volta estritamente como CONTROLADOR sem poder administrativo."""
    with (
        TestClient(app) as client_a,
        TestClient(app) as client_b,
        TestClient(app) as client_c,
    ):
        # 1. Configura cenário com A, B e C
        resp_a = client_a.post(
            "/api/quadras", json={"nome": "Quadra Retorno", "apelido": "Admin A"}
        )
        quadra_id = resp_a.json()["id"]
        a_id = resp_a.json()["participante"]["id"]

        resp_b = client_b.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Controlador B"}
        )
        b_id = resp_b.json()["participante"]["id"]
        client_a.post(f"/api/quadras/{quadra_id}/participantes/{b_id}/promover")

        resp_c = client_c.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Controlador C"}
        )
        c_id = resp_c.json()["participante"]["id"]
        client_a.post(f"/api/quadras/{quadra_id}/participantes/{c_id}/promover")

        # Simula ausência de A e executa sucessão
        antigo_visto = (datetime.now(UTC) - timedelta(seconds=150)).isoformat()
        with get_db(settings.db_path) as conn:
            conn.execute(
                "UPDATE participantes SET ultimo_visto_em = ? WHERE id = ?",
                (antigo_visto, a_id),
            )
            conn.commit()

        verificar_sucessao_quadra_sync(
            settings.db_path, quadra_id, {b_id, c_id}, timeout_seconds=120
        )

        # 2. Admin A faz nova requisição (reconexão)
        resp_get = client_a.get(f"/api/quadras/{quadra_id}")
        assert resp_get.status_code == 200

        # Participante A agora é CONTROLADOR
        resp_eu_a = client_a.get(f"/api/quadras/{quadra_id}/eu")
        assert resp_eu_a.json()["participante"]["papel"] == "CONTROLADOR"

        # 3. A tenta revogar C -> Rejeitado com HTTP 403 (A não é mais admin!)
        resp_revogar_por_a = client_a.post(
            f"/api/quadras/{quadra_id}/participantes/{c_id}/revogar"
        )
        assert resp_revogar_por_a.status_code == 403

        # 4. Novo admin B consegue revogar C com sucesso
        resp_revogar_por_b = client_b.post(
            f"/api/quadras/{quadra_id}/participantes/{c_id}/revogar"
        )
        assert resp_revogar_por_b.status_code == 200

        # 5. A ainda pode operar como controlador: assume controle e pontua
        client_a.post(f"/api/quadras/{quadra_id}/controle/assumir")
        versao = str(
            client_a.get(f"/api/quadras/{quadra_id}").json()["controle_versao"]
        )
        resp_ponto_a = client_a.post(
            f"/api/quadras/{quadra_id}/pontos",
            json={"equipe": "A"},
            headers={"x-control-version": versao},
        )
        assert resp_ponto_a.status_code == 201
        assert resp_ponto_a.json()["estado_partida"]["pontos_a"] == 1


def test_sucessao_sem_controlador_online():
    """Se nenhum controlador estiver online, quadra segue com posto vago e controladores pontuam."""
    with TestClient(app) as client_a, TestClient(app) as client_b:
        resp_a = client_a.post(
            "/api/quadras", json={"nome": "Quadra Posto Vago", "apelido": "Admin A"}
        )
        quadra_id = resp_a.json()["id"]
        a_id = resp_a.json()["participante"]["id"]

        # B é apenas espectador
        resp_b = client_b.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Espectador B"}
        )
        b_id = resp_b.json()["participante"]["id"]

        antigo_visto = (datetime.now(UTC) - timedelta(seconds=200)).isoformat()
        with get_db(settings.db_path) as conn:
            conn.execute(
                "UPDATE participantes SET ultimo_visto_em = ? WHERE id = ?",
                (antigo_visto, a_id),
            )
            conn.commit()

        # Apenas B (espectador) está online
        snap = verificar_sucessao_quadra_sync(
            settings.db_path, quadra_id, {b_id}, timeout_seconds=120
        )

        assert snap is not None
        # Posto de admin ficou vago (A virou CONTROLADOR, nenhum admin na sala)
        p_map = {p["id"]: p for p in snap["participantes"]}
        assert p_map[a_id]["papel"] == "CONTROLADOR"
        assert p_map[b_id]["papel"] == "ESPECTADOR"
        assert not any(p["papel"] == "ADMIN" for p in snap["participantes"])

        # Evento registra que não houve novo admin
        eventos = carregar_eventos_sync(settings.db_path, snap["partida_id"])
        evento = eventos[-1]
        assert evento.tipo == "ADMIN_SUCEDIDO"
        assert evento.payload["novo_admin_id"] is None

        # Linha do tempo registra posto vago
        assert (
            "Administração vaga por ausência de Admin A"
            in snap["linha_do_tempo"][-1]["descricao"]
        )


def test_sucessao_nao_dispara_antes_do_tempo_ou_com_admin_online():
    """Sucessão não deve ocorrer se o admin estiver online ou se o timeout não expirou."""
    with TestClient(app) as client_a, TestClient(app) as client_b:
        resp_a = client_a.post(
            "/api/quadras", json={"nome": "Quadra Online", "apelido": "Admin A"}
        )
        quadra_id = resp_a.json()["id"]
        a_id = resp_a.json()["participante"]["id"]

        resp_b = client_b.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Controlador B"}
        )
        b_id = resp_b.json()["participante"]["id"]
        client_a.post(f"/api/quadras/{quadra_id}/participantes/{b_id}/promover")

        # 1. Admin A está online: não dispara
        resultado_online = verificar_sucessao_quadra_sync(
            settings.db_path, quadra_id, {a_id, b_id}, timeout_seconds=120
        )
        assert resultado_online is None

        # 2. Admin A está offline, mas há apenas 30 segundos (< 120s): não dispara
        recente_visto = (datetime.now(UTC) - timedelta(seconds=30)).isoformat()
        with get_db(settings.db_path) as conn:
            conn.execute(
                "UPDATE participantes SET ultimo_visto_em = ? WHERE id = ?",
                (recente_visto, a_id),
            )
            conn.commit()

        resultado_recente = verificar_sucessao_quadra_sync(
            settings.db_path, quadra_id, {b_id}, timeout_seconds=120
        )
        assert resultado_recente is None


def test_sucessao_propagacao_websocket():
    """Controlador conectado via WebSocket recebe atualização em tempo real com seu novo papel de ADMIN."""
    settings.admin_timeout_seconds = 1
    with TestClient(app) as client_a, TestClient(app) as client_b:
        resp_a = client_a.post(
            "/api/quadras", json={"nome": "Quadra WS", "apelido": "Admin A"}
        )
        quadra_id = resp_a.json()["id"]
        a_id = resp_a.json()["participante"]["id"]

        resp_b = client_b.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Controlador B"}
        )
        b_id = resp_b.json()["participante"]["id"]
        client_a.post(f"/api/quadras/{quadra_id}/participantes/{b_id}/promover")

        # Conecta B no WebSocket
        with client_b.websocket_connect(f"/ws/{quadra_id}") as ws_b:
            msg_inicial = ws_b.receive_json()
            assert msg_inicial["tipo"] == "ESTADO_INICIAL"

            # Simula que A desconectou há 3 segundos
            antigo_visto = (datetime.now(UTC) - timedelta(seconds=3)).isoformat()
            with get_db(settings.db_path) as conn:
                conn.execute(
                    "UPDATE participantes SET ultimo_visto_em = ? WHERE id = ?",
                    (antigo_visto, a_id),
                )
                conn.commit()

            # Aguarda a rotina de sucessão rodar e transmitir via WebSocket
            import time

            start = time.time()
            recebeu_promocao = False
            while time.time() - start < 5.0:
                try:
                    msg = ws_b.receive_json(mode="text")
                    if msg.get("tipo") == "PLACAR_ATUALIZADO" and msg.get(
                        "payload", {}
                    ).get("participantes"):
                        part_b = next(
                            (
                                p
                                for p in msg["payload"]["participantes"]
                                if p["id"] == b_id
                            ),
                            None,
                        )
                        if part_b and part_b["papel"] == "ADMIN":
                            recebeu_promocao = True
                            break
                except (
                    WebSocketDisconnect,
                    RuntimeError,
                    OSError,
                    TimeoutError,
                    KeyError,
                ):
                    time.sleep(0.2)

            assert recebeu_promocao, (
                "B não recebeu PLACAR_ATUALIZADO promovendo a ADMIN a tempo"
            )

            # Confere se no endpoint REST da quadra B agora é ADMIN
            resp_eu_b = client_b.get(f"/api/quadras/{quadra_id}/eu")
            assert resp_eu_b.json()["participante"]["papel"] == "ADMIN"
