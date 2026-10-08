from pathlib import Path

import pytest
from starlette.testclient import TestClient

from app.config import settings
from app.db import init_db
from app.exibicao import projetar
from app.identidade import SESSION_COOKIE
from app.main import app
from app.rate_limit import owner_rate_limiter

CABECALHO = {"x-owner-secret": "segredo-teste"}


@pytest.fixture(autouse=True)
async def banco(tmp_path: Path):
    settings.db_path = str(tmp_path / "quadras.db")
    settings.gerenciador_db_path = str(tmp_path / "gerenciador.db")
    settings.owner_secret = "segredo-teste"
    settings.gerenciador_backup_dir = ""
    owner_rate_limiter.resetar()
    await init_db(settings.db_path)
    yield
    owner_rate_limiter.resetar()


def preparar(client):
    quadra = client.post("/api/quadras", json={"nome": "Quadra"}).json()["id"]
    client.post(
        f"/api/quadras/{quadra}/entrar",
        json={"apelido": "Admin"},
        headers={"x-session-id": "sessao-admin"},
    )
    client.post(
        f"/api/quadras/{quadra}/entrar",
        json={"apelido": "Visita"},
        headers={"x-session-id": "sessao-visita"},
    )
    dono = {"headers": CABECALHO}
    client.post("/api/sessao", **dono)
    for i, nome in enumerate(["Ana", "Bia", "Caio", "Davi", "Eva", "Fabio", "Gabi", "Hugo"]):
        j = client.post(
            "/api/jogadores",
            json={
                "nome": f"{nome} Teste",
                "genero": "M" if i % 2 == 0 else "H",
                "nota": 50 + i,
            },
            **dono,
        ).json()
        client.put(f"/api/sessao/presencas/{j['id']}", **dono)
    client.post("/api/rodada/sorteio", json={"alvo": 10}, **dono)
    client.post("/api/rodada/confirmar", **dono)
    r = client.put("/api/sessao/quadra", json={"codigo": quadra}, **dono)
    assert r.status_code == 200, r.text
    return quadra


def espectador(client, quadra):
    return client.websocket_connect(
        f"/ws/{quadra}", headers={"cookie": f"{SESSION_COOKIE}=sessao-visita"}
    )


def test_estado_inicial_leva_fila_e_reis_sem_dados_privados():
    with TestClient(app) as client:
        quadra = preparar(client)
        with espectador(client, quadra) as ws:
            inicial = ws.receive_json()
        assert inicial["tipo"] == "ESTADO_INICIAL"
        ex = inicial["payload"]["exibicao"]
        assert ex["fase"] == "fila" and ex["rodada"] == 1
        assert len(ex["em_quadra"]) == 2 and len(ex["fila"]) == 2 and ex["reis"] == []
        assert ex["em_quadra"][0]["nome"].count(" + ") == 1
        texto = str(ex)
        assert "nota" not in texto and "id" not in {k for e in ex["fila"] for k in e}


def test_mudanca_do_gerenciador_chega_ao_espectador():
    with TestClient(app) as client:
        quadra = preparar(client)
        with espectador(client, quadra) as ws:
            assert ws.receive_json()["tipo"] == "ESTADO_INICIAL"
            assert ws.receive_json()["tipo"] == "PRESENCA_ATUALIZADA"
            client.post("/api/rodada/cancelar", headers=CABECALHO)
            msg = ws.receive_json()
            while msg["tipo"] != "EXIBICAO_ATUALIZADA":
                msg = ws.receive_json()
            assert msg["payload"] is None  # rodada cancelada: nada a mostrar


def test_sem_vinculo_nao_ha_exibicao():
    with TestClient(app) as client:
        outra = client.post("/api/quadras", json={"nome": "Outra"}).json()["id"]
        client.post(
            f"/api/quadras/{outra}/entrar",
            json={"apelido": "Visita"},
            headers={"x-session-id": "sessao-visita"},
        )
        quadra = preparar(client)
        assert quadra != outra
        with espectador(client, outra) as ws:
            assert ws.receive_json()["payload"]["exibicao"] is None


def test_projetar_sem_rodada_nem_campeao_e_none():
    assert projetar({"rodada": None, "conducao": None, "ultimo_campeao": None}) is None
    campeao = {"rodada": 1, "time": 3, "jogadores": ["Ana Souza", "Bia Lima"]}
    ex = projetar({"rodada": None, "conducao": None, "ultimo_campeao": campeao})
    assert ex["fase"] == "campeao" and ex["campeao"]["nome"] == "Ana + Bia"
