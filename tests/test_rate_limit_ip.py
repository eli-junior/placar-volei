"""CV5.DS1.TS1: limites de tentativa pelo IP real, nunca por X-Forwarded-For."""

import pytest

from app.config import settings
from app.identidade import SESSION_COOKIE
from app.quadras import gerar_codigo_quadra_sync
from app.rate_limit import owner_rate_limiter
from app.watch import approval_limit
from tests.watch_support import prepare


@pytest.fixture(autouse=True)
def limpar():
    owner_rate_limiter.resetar()
    yield
    owner_rate_limiter.resetar()


def test_owner_bloqueia_mesmo_trocando_x_forwarded_for(client):
    for n in range(5):
        r = client.get(
            "/api/owner/quadras",
            headers={"x-owner-secret": "errado", "x-forwarded-for": f"10.0.0.{n}"},
        )
        assert r.status_code == 404
    r = client.get(
        "/api/owner/quadras",
        headers={"x-owner-secret": "errado", "x-forwarded-for": "10.9.9.9"},
    )
    assert r.status_code == 429


def test_cf_connecting_ip_separa_clientes_quando_confiavel(client):
    settings.trust_cloudflare = True
    for _ in range(5):
        client.get(
            "/api/owner/quadras",
            headers={"x-owner-secret": "errado", "cf-connecting-ip": "1.1.1.1"},
        )
    bloqueado = client.get(
        "/api/owner/quadras",
        headers={"x-owner-secret": "errado", "cf-connecting-ip": "1.1.1.1"},
    )
    outro = client.get(
        "/api/owner/quadras",
        headers={"x-owner-secret": "errado", "cf-connecting-ip": "2.2.2.2"},
    )
    assert bloqueado.status_code == 429
    assert outro.status_code == 404


def test_cf_connecting_ip_ignorado_sem_confianca(client):
    settings.trust_cloudflare = False
    for n in range(5):
        client.get(
            "/api/owner/quadras",
            headers={"x-owner-secret": "errado", "cf-connecting-ip": f"3.3.3.{n}"},
        )
    r = client.get(
        "/api/owner/quadras",
        headers={"x-owner-secret": "errado", "cf-connecting-ip": "4.4.4.4"},
    )
    assert r.status_code == 429


def test_codigos_de_sala_errados_sao_limitados_por_ip(client):
    court = prepare(client)
    for n in range(20):
        r = client.post(
            f"/api/quadras/{99999 - n}/entrar",
            json={"apelido": "Curioso"},
            headers={"x-forwarded-for": f"10.1.1.{n}"},
        )
        assert r.status_code == 404
    r = client.post(f"/api/quadras/{court['id']}/entrar", json={"apelido": "Ana"})
    assert r.status_code == 429
    assert int(r.headers["Retry-After"]) > 0


def test_codigo_certo_nao_gasta_tentativa(client):
    court = prepare(client)
    for n in range(25):
        r = client.post(
            f"/api/quadras/{court['id']}/entrar",
            json={"apelido": f"J{n}"},
            headers={"x-session-id": f"sessao-{n}"},
        )
        assert r.status_code != 429


def test_aprovacao_do_relogio_limitada_tambem_por_ip_na_quadra(client):
    court = prepare(client)
    url = f"/api/quadras/{court['id']}/watch/approve"
    for _ in range(5):
        assert client.post(url, json={"code": "00000000"}).status_code == 400
    # Simula a sessão nova: o contador do participante zera, o do IP não.
    approval_limit.registrar_sucesso(court["participante"]["id"])
    assert client.post(url, json={"code": "00000000"}).status_code == 429


def test_session_id_fora_do_formato_gera_sessao_nova(client):
    court = prepare(client)
    r = client.post(
        f"/api/quadras/{court['id']}/entrar",
        json={"apelido": "Bia"},
        headers={"x-session-id": "x" * 500},
    )
    assert r.status_code == 200
    cookie = r.cookies.get(SESSION_COOKIE)
    assert cookie and len(cookie) == 36


def test_pin_tem_cinco_digitos(tmp_path):
    from app.db import get_db, init_db_sync

    db = str(tmp_path / "pin.db")
    init_db_sync(db)
    with get_db(db) as conn:
        codigos = {gerar_codigo_quadra_sync(conn) for _ in range(50)}
    assert all(c.isdigit() and 10000 <= int(c) <= 99999 for c in codigos)
