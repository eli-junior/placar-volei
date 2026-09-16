"""Testes da CV2.DS2.US6 — Unicidade de apelidos na mesma quadra.

A linha do tempo e a lista de presentes identificam pessoas por apelido. Dois
"Bruno" na mesma sala permitem personificação e tornam a auditoria da partida
ambígua — esta é a parte A5 do débito `debt-apelidos-e-transferencia-de-controle`.

A recusa usa o contrato de erro da CV2.DS1: `detail` string legível + `erros`
campo a campo.
"""

import pytest
from starlette.testclient import TestClient

from app.config import settings
from app.db import init_db_sync
from app.main import app


@pytest.fixture(autouse=True)
def banco(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "db_path", str(tmp_path / "apelidos.db"))
    init_db_sync()


class Cliente:
    def __init__(self, base, token):
        self._base = base
        self.token = token

    def post(self, url, **kwargs):
        headers = {**kwargs.pop("headers", {}), "x-session-id": self.token}
        return self._base.post(url, headers=headers, **kwargs)


def test_apelido_ja_em_uso_na_quadra_e_recusado():
    with TestClient(app) as base:
        primeiro = Cliente(base, "sessao-1")
        segundo = Cliente(base, "sessao-2")

        quadra_id = primeiro.post("/api/quadras", json={"apelido": "Bruno"}).json()["id"]

        recusado = segundo.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Bruno"}
        )
        assert recusado.status_code == 409
        corpo = recusado.json()
        assert isinstance(corpo["detail"], str)
        assert "Bruno" in corpo["detail"]
        assert corpo["erros"] == [
            {
                "campo": "apelido",
                "rotulo": "Apelido",
                "mensagem": "já está em uso nesta quadra",
                "tipo": "apelido_em_uso",
            }
        ]


def test_recusa_ignora_caixa_e_espacos():
    """"bruno ", "BRUNO" e "Bruno" são a mesma pessoa a três metros da quadra."""
    with TestClient(app) as base:
        primeiro = Cliente(base, "sessao-1")
        segundo = Cliente(base, "sessao-2")

        quadra_id = primeiro.post("/api/quadras", json={"apelido": "Bruno"}).json()["id"]

        for variacao in ("bruno", "  BRUNO  ", "BrUnO"):
            resposta = segundo.post(
                f"/api/quadras/{quadra_id}/entrar", json={"apelido": variacao}
            )
            assert resposta.status_code == 409, variacao


def test_apelido_livre_entra_normalmente():
    with TestClient(app) as base:
        primeiro = Cliente(base, "sessao-1")
        segundo = Cliente(base, "sessao-2")

        quadra_id = primeiro.post("/api/quadras", json={"apelido": "Bruno"}).json()["id"]

        aceito = segundo.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Bruninho"}
        )
        assert aceito.status_code == 200
        assert aceito.json()["participante"]["apelido"] == "Bruninho"


def test_mesma_sessao_reentra_com_o_proprio_apelido():
    """Recarregar a página não pode virar 'apelido em uso' contra si mesmo."""
    with TestClient(app) as base:
        pessoa = Cliente(base, "sessao-1")
        outra = Cliente(base, "sessao-2")

        quadra_id = outra.post("/api/quadras", json={"apelido": "Admin"}).json()["id"]
        pessoa.post(f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Bruno"})

        de_novo = pessoa.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Bruno"}
        )
        assert de_novo.status_code == 200
        assert de_novo.json()["participante"]["apelido"] == "Bruno"


def test_troca_de_apelido_para_um_ja_ocupado_e_recusada():
    with TestClient(app) as base:
        admin = Cliente(base, "sessao-admin")
        pessoa = Cliente(base, "sessao-1")

        quadra_id = admin.post("/api/quadras", json={"apelido": "Bruno"}).json()["id"]
        pessoa.post(f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Carla"})

        recusado = pessoa.post(
            f"/api/quadras/{quadra_id}/entrar", json={"apelido": "Bruno"}
        )
        assert recusado.status_code == 409


def test_mesmo_apelido_em_quadras_diferentes_continua_permitido():
    """A unicidade é por quadra. Duas peladas podem ter cada uma o seu Bruno."""
    with TestClient(app) as base:
        primeiro = Cliente(base, "sessao-1")
        segundo = Cliente(base, "sessao-2")

        primeiro.post("/api/quadras", json={"apelido": "Bruno"})
        outra = segundo.post("/api/quadras", json={"apelido": "Bruno"})
        assert outra.status_code == 201
