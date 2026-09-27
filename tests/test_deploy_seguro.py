"""CV5.DS1.TS2: produção não sobe com segredo de exemplo; health e cookie."""

import pytest
from fastapi.testclient import TestClient

from app.config import SEGREDO_PADRAO, settings, validar_producao
from app.identidade import SESSION_COOKIE
from app.main import app


@pytest.mark.parametrize("segredo", ["", "  ", SEGREDO_PADRAO])
def test_producao_recusa_segredo_ausente_ou_de_exemplo(segredo):
    settings.producao = True
    settings.owner_secret = segredo
    with pytest.raises(RuntimeError, match="OWNER_SECRET"):
        validar_producao(settings)


def test_producao_aceita_segredo_proprio():
    settings.producao = True
    settings.owner_secret = "um-segredo-de-verdade"
    validar_producao(settings)


def test_fora_de_producao_segredo_de_exemplo_e_permitido():
    settings.producao = False
    settings.owner_secret = SEGREDO_PADRAO
    validar_producao(settings)


def test_health_nao_expoe_caminho_do_banco(tmp_path):
    settings.db_path = str(tmp_path / "h.db")
    with TestClient(app) as c:
        dados = c.get("/health").json()
    assert "db" not in dados
    assert str(tmp_path) not in str(dados)


@pytest.mark.parametrize("seguro", [True, False])
def test_cookie_de_sessao_segue_cookie_secure(tmp_path, seguro):
    settings.db_path = str(tmp_path / "c.db")
    settings.cookie_secure = seguro
    with TestClient(app) as c:
        r = c.post("/api/quadras", json={"apelido": "Ana"})
    cabecalho = next(
        v
        for k, v in r.headers.multi_items()
        if k == "set-cookie" and SESSION_COOKIE in v
    )
    assert ("secure" in cabecalho.lower()) is seguro
