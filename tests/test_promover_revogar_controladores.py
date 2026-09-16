from pathlib import Path

import pytest
from starlette.testclient import TestClient

from app.config import settings
from app.db import init_db
from app.main import app


@pytest.fixture(autouse=True)
async def setup_test_db(tmp_path: Path):
    db_file = str(tmp_path / "test_us1_permissoes.db")
    settings.db_path = db_file
    await init_db(db_file)
    yield


def test_fluxo_promover_e_revogar_controladores():
    """Admin promove espectador a controlador, que pode pontuar; revogação remove a permissão."""
    with (
        TestClient(app) as client_a,
        TestClient(app) as client_b,
        TestClient(app) as client_c,
    ):
        # 1. Admin A cria a quadra
        resp_a = client_a.post(
            "/api/quadras", json={"nome": "Quadra Teste", "apelido": "Admin A"}
        )
        assert resp_a.status_code == 201
        data_a = resp_a.json()
        quadra_id = data_a["id"]
        admin_id = data_a["participante"]["id"]

        # 2. Espectador B entra
        resp_b = client_b.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Espectador B"}
        )
        assert resp_b.status_code == 200
        b_id = resp_b.json()["participante"]["id"]

        # 3. Espectador C entra
        resp_c = client_c.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Espectador C"}
        )
        assert resp_c.status_code == 200
        c_id = resp_c.json()["participante"]["id"]

        # 4. Espectador B tenta pontuar ou assumir controle -> 403
        r_ponto_b = client_b.post(
            f"/api/quadras/{quadra_id}/pontos",
            json={"equipe": "A"},
            headers={"x-control-version": "1"},
        )
        assert r_ponto_b.status_code == 403

        r_assumir_b = client_b.post(f"/api/quadras/{quadra_id}/controle/assumir")
        assert r_assumir_b.status_code == 403

        # 5. Espectador B tenta promover C -> 403
        r_promover_c = client_b.post(
            f"/api/quadras/{quadra_id}/participantes/{c_id}/promover"
        )
        assert r_promover_c.status_code == 403

        # 6. Admin A promove B a controlador
        r_promover = client_a.post(
            f"/api/quadras/{quadra_id}/participantes/{b_id}/promover"
        )
        assert r_promover.status_code == 200
        dados_promo = r_promover.json()
        participante_b = next(
            p for p in dados_promo["participantes"] if p["id"] == b_id
        )
        assert participante_b["papel"] == "CONTROLADOR"
        # CV2.DS2.US5: Promover concede permissão sem transferir posse do placar automaticamente
        assert dados_promo["quadra"]["controle_id"] == admin_id

        # Controlador B assume o controle do placar
        r_assumir_b = client_b.post(f"/api/quadras/{quadra_id}/controle/assumir")
        assert r_assumir_b.status_code == 200
        dados_assumir_b = r_assumir_b.json()
        assert dados_assumir_b["quadra"]["controle_id"] == b_id
        versao_b = str(dados_assumir_b["quadra"]["controle_versao"])

        # 7. Controlador B marca ponto
        r_ponto_b_ok = client_b.post(
            f"/api/quadras/{quadra_id}/pontos",
            json={"equipe": "A"},
            headers={"x-control-version": versao_b},
        )
        assert r_ponto_b_ok.status_code == 201
        assert r_ponto_b_ok.json()["estado_partida"]["pontos_a"] == 1

        # 8. Espectador C continua não podendo pontuar
        r_ponto_c = client_c.post(
            f"/api/quadras/{quadra_id}/pontos",
            json={"equipe": "B"},
            headers={"x-control-version": versao_b},
        )
        assert r_ponto_c.status_code == 403

        # 9. Admin A pode assumir o controle de volta
        r_assumir_a = client_a.post(f"/api/quadras/{quadra_id}/controle/assumir")
        assert r_assumir_a.status_code == 200
        versao_a = str(r_assumir_a.json()["quadra"]["controle_versao"])
        assert r_assumir_a.json()["quadra"]["controle_id"] == admin_id

        # 10. B tenta pontuar enquanto A está no controle -> 403
        r_ponto_b_bloq = client_b.post(
            f"/api/quadras/{quadra_id}/pontos",
            json={"equipe": "A"},
            headers={"x-control-version": versao_b},
        )
        assert r_ponto_b_bloq.status_code == 409 or r_ponto_b_bloq.status_code == 403

        # 11. Admin A desfaz o ponto
        r_desfazer = client_a.post(
            f"/api/quadras/{quadra_id}/desfazer",
            headers={"x-control-version": versao_a},
        )
        assert r_desfazer.status_code == 200
        assert r_desfazer.json()["estado_partida"]["pontos_a"] == 0

        # 12. Admin A revoga o papel de controlador de B
        r_revogar = client_a.post(
            f"/api/quadras/{quadra_id}/participantes/{b_id}/revogar"
        )
        assert r_revogar.status_code == 200
        dados_revog = r_revogar.json()
        participante_b_revogado = next(
            p for p in dados_revog["participantes"] if p["id"] == b_id
        )
        assert participante_b_revogado["papel"] == "ESPECTADOR"

        # 13. Ex-controlador B tenta pontuar ou assumir -> 403
        r_ponto_b_pos = client_b.post(
            f"/api/quadras/{quadra_id}/pontos",
            json={"equipe": "A"},
            headers={
                "x-control-version": str(dados_revog["quadra"]["controle_versao"])
            },
        )
        assert r_ponto_b_pos.status_code == 403


def test_promover_e_revogar_via_endpoint_papel_e_websocket():
    """Notificações WebSocket e endpoint genérico /papel propagam promoções e revogações."""
    with TestClient(app) as client_a, TestClient(app) as client_b:
        # Cria quadra
        resp_a = client_a.post(
            "/api/quadras", json={"nome": "Quadra WS", "apelido": "Eli"}
        )
        quadra_id = resp_a.json()["id"]

        # B entra
        resp_b = client_b.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Carlos"}
        )
        b_id = resp_b.json()["participante"]["id"]

        with client_a.websocket_connect(f"/ws/{quadra_id}") as ws_a:
            # ws_a recebe ESTADO_INICIAL
            ws_a.receive_json()

            with client_b.websocket_connect(f"/ws/{quadra_id}") as ws_b:
                # ws_b recebe ESTADO_INICIAL
                ws_b.receive_json()
                # ws_a recebe PRESENCA_ATUALIZADA notificando a entrada de b
                ws_a.receive_json()

                # Promove via POST /papel
                resp_promo = client_a.post(
                    f"/api/quadras/{quadra_id}/participantes/{b_id}/papel",
                    json={"papel": "CONTROLADOR"},
                )
                assert resp_promo.status_code == 200

                # Ambos devem receber PLACAR_ATUALIZADO com evento PAPEL_ALTERADO
                def receber_placar(ws):
                    while True:
                        m = ws.receive_json()
                        if m["tipo"] == "PLACAR_ATUALIZADO":
                            return m

                msg_ws_b = receber_placar(ws_b)
                assert msg_ws_b["tipo"] == "PLACAR_ATUALIZADO"
                part_b = next(
                    p for p in msg_ws_b["payload"]["participantes"] if p["id"] == b_id
                )
                assert part_b["papel"] == "CONTROLADOR"

                # Confere linha do tempo projetada
                lt = client_a.get(f"/api/quadras/{quadra_id}/linha-do-tempo").json()[
                    "itens"
                ]
                assert any(
                    "promoveu Carlos a controlador" in item["descricao"] for item in lt
                )

                # Revoga via POST /papel
                resp_revog = client_a.post(
                    f"/api/quadras/{quadra_id}/participantes/{b_id}/papel",
                    json={"papel": "ESPECTADOR"},
                )
                assert resp_revog.status_code == 200

                msg_ws_revog = receber_placar(ws_b)
                assert msg_ws_revog["tipo"] == "PLACAR_ATUALIZADO"
                part_b_revog = next(
                    p
                    for p in msg_ws_revog["payload"]["participantes"]
                    if p["id"] == b_id
                )
                assert part_b_revog["papel"] == "ESPECTADOR"

                lt_revog = client_a.get(
                    f"/api/quadras/{quadra_id}/linha-do-tempo"
                ).json()["itens"]
                assert any(
                    "revogou controlador de Carlos" in item["descricao"]
                    for item in lt_revog
                )
