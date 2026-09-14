import asyncio
import json
from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.comandos import executar_sync
from app.config import settings
from app.db import get_db, init_db_sync
from app.eventos import carregar_eventos_sync
from app.fixtures import sincronizar_fixtures_para_db_sync
from app.identidade import SESSION_COOKIE
from app.main import app
from app.quadras import criar_quadra_sync, limpar_quadras_expiradas_sync


@pytest.fixture(autouse=True)
def banco(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "db_path", str(tmp_path / "review.db"))
    monkeypatch.setattr(settings, "default_arenas_file", "")
    monkeypatch.setattr(settings, "max_quadras", 20)
    monkeypatch.setattr(settings, "max_participantes_por_quadra", 20)
    init_db_sync()


def sala(client):
    response = client.post("/api/quadras", json={"apelido": "Admin"})
    assert response.status_code == 201
    return response.json()


def ponto(client, q, versao=1):
    return client.post(
        f"/api/quadras/{q}/pontos",
        json={"equipe": "A"},
        headers={"x-control-version": str(versao)},
    )


def expirar(q):
    with get_db() as conn:
        conn.execute(
            "UPDATE quadras SET atualizado_em = '2000-01-01T00:00:00+00:00' WHERE id = ?",
            (q,),
        )


@pytest.mark.parametrize(
    "url", ["/%2e%2e/config.py", "/%2e%2e/%2e%2e/pyproject.toml", "/..%5cconfig.py"]
)
def test_static_nao_escapa_da_raiz(url, tmp_path, monkeypatch):
    from app import main

    raiz = tmp_path / "static"
    raiz.mkdir()
    (raiz / "index.html").write_text("publico")
    (tmp_path / "config.py").write_text("privado")
    monkeypatch.setattr(main, "static_dir", str(raiz))
    with TestClient(app) as client:
        res = client.get(url)
        assert res.status_code == 404
        assert "privado" not in res.text
        assert client.get("/").text == "publico"
        assert client.get("/quadra/12345").text == "publico"


def test_credencial_nao_aparece_em_superficies_publicas():
    with TestClient(app) as admin, TestClient(app) as visitante:
        q = sala(admin)
        token = admin.cookies.get(SESSION_COOKIE)
        assert token not in json.dumps(q)
        assert ponto(admin, q["id"]).status_code == 201
        for rota in ["participantes", "linha-do-tempo", "partida", "eu"]:
            assert token not in admin.get(f"/api/quadras/{q['id']}/{rota}").text
        with admin.websocket_connect(f"/ws/{q['id']}") as ws:
            assert token not in json.dumps(ws.receive_json())
        # Nem ID público nem cookie legado autenticam o atacante.
        visitante.cookies.set("session_id", token)
        assert ponto(visitante, q["id"]).status_code == 401
        atacante = {"x-session-id": q["participante"]["id"], "x-control-version": "1"}
        res = visitante.post(
            f"/api/quadras/{q['id']}/pontos", json={"equipe": "A"}, headers=atacante
        )
        assert res.status_code == 403


def test_cookie_legado_nao_e_reutilizado_ao_criar_sala():
    with TestClient(app) as client:
        client.cookies.set("session_id", "credencial-exposta")
        q = sala(client)
        assert client.cookies.get(SESSION_COOKIE) != "credencial-exposta"
        res = client.get(
            f"/api/quadras/{q['id']}/eu", headers={"x-session-id": "credencial-exposta"}
        )
        assert res.json()["participante"] is None


def test_transferencia_exclusiva_auditavel_e_mandato_antigo_rejeitado():
    with TestClient(app) as a:
        # Um único servidor/event loop, três identidades de navegador.
        class Cliente:
            def __init__(self, token):
                self.token = token

            def post(self, url, **kwargs):
                headers = {**kwargs.pop("headers", {}), "x-session-id": self.token}
                return a.post(url, headers=headers, **kwargs)

            def websocket_connect(self, url):
                return a.websocket_connect(
                    url, headers={"cookie": f"{SESSION_COOKIE}={self.token}"}
                )

        b, c = Cliente("sessao-b"), Cliente("sessao-c")
        q = sala(a)["id"]
        bid = b.post(f"/api/quadras/{q}/entrar", json={"apelido": "B"}).json()[
            "participante"
        ]["id"]
        cid = c.post(f"/api/quadras/{q}/entrar", json={"apelido": "C"}).json()[
            "participante"
        ]["id"]
        assert b.post(f"/api/quadras/{q}/controle/assumir").status_code == 403
        assert c.post(f"/api/quadras/{q}/participantes/{cid}/admin").status_code == 403
        with a.websocket_connect(f"/ws/{q}") as wa:
            wa.receive_json()
            wa.receive_json()
            with b.websocket_connect(f"/ws/{q}") as wb:
                wb.receive_json()
                wb.receive_json()
                wa.receive_json()
                promoted = a.post(f"/api/quadras/{q}/participantes/{bid}/admin")
                assert promoted.status_code == 200
                assert (
                    wa.receive_json()["payload"]["evento"]["tipo"] == "PAPEL_ALTERADO"
                )
                assert (
                    wb.receive_json()["payload"]["participantes"][1]["papel"] == "ADMIN"
                )
                assert ponto(b, q).status_code == 403
                transfer = b.post(f"/api/quadras/{q}/controle/assumir").json()
                assert transfer["quadra"]["controle_id"] == bid
                assert transfer["quadra"]["controle_versao"] == 2
                assert (
                    wa.receive_json()["payload"]["evento"]["tipo"]
                    == "CONTROLE_ASSUMIDO"
                )
                assert wb.receive_json()["payload"]["quadra"]["controle_id"] == bid
                assert ponto(a, q).status_code == 403
                assert ponto(b, q, 1).status_code == 409
                assert ponto(b, q, 2).status_code == 201
                assert (
                    c.post(
                        f"/api/quadras/{q}/desfazer", headers={"x-control-version": "2"}
                    ).status_code
                    == 403
                )
                assert a.post(f"/api/quadras/{q}/controle/assumir").status_code == 200
                assert ponto(a, q, 1).status_code == 409
                assert ponto(a, q, 3).status_code == 201
                assert (
                    b.post(
                        f"/api/quadras/{q}/desfazer", headers={"x-control-version": "2"}
                    ).status_code
                    == 403
                )
        eventos = a.get(f"/api/quadras/{q}/linha-do-tempo").json()["itens"]
        assert sum(e["tipo"] == "CONTROLE_ASSUMIDO" for e in eventos) == 2


def test_controle_exige_versao_e_persiste_apos_restart():
    with TestClient(app) as client:
        q = sala(client)["id"]
        assert (
            client.post(f"/api/quadras/{q}/pontos", json={"equipe": "A"}).status_code
            == 428
        )
        assert ponto(client, q).status_code == 201
        antes = client.get(f"/api/quadras/{q}/eu").json()
        init_db_sync()
        assert client.get(f"/api/quadras/{q}/eu").json() == antes
        with client.websocket_connect(f"/ws/{q}") as ws:
            data = ws.receive_json()["payload"]
            assert data["estado_partida"]["pontos_a"] == 1
            assert data["quadra"]["controle_id"] == antes["participante"]["id"]


def test_comandos_concorrentes_no_banco_nao_perdem_pontos_nem_repetem_desfazer():
    q = criar_quadra_sync(settings.db_path, apelido="Admin", session_id="privado")

    def operar(acao):
        return executar_sync(
            settings.db_path, q["id"], "privado", acao, equipe="A", versao="1"
        )

    with ThreadPoolExecutor(max_workers=8) as pool:
        pontos = list(pool.map(operar, ["pontos"] * 8))
        assert sorted(p["estado_partida"]["pontos_a"] for p in pontos) == list(
            range(1, 9)
        )
        desfeitos = list(pool.map(operar, ["desfazer"] * 8))
    assert len({r["evento"]["payload"]["ref_seq"] for r in desfeitos}) == 8
    assert sorted(r["estado_partida"]["pontos_a"] for r in desfeitos) == list(range(8))
    eventos = carregar_eventos_sync(settings.db_path, q["partida_id"])
    assert [e.seq for e in eventos] == list(range(1, 18))


async def test_capacidade_concorrente_de_salas_e_participantes(monkeypatch):
    monkeypatch.setattr(settings, "max_quadras", 1)
    monkeypatch.setattr(settings, "max_participantes_por_quadra", 2)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        respostas = await asyncio.gather(
            *[client.post("/api/quadras", json={"apelido": "Admin"}) for _ in range(8)]
        )
        assert sorted(r.status_code for r in respostas) == [201] + [400] * 7
        q = next(r.json()["id"] for r in respostas if r.status_code == 201)
        entradas = await asyncio.gather(
            *[
                client.post(
                    f"/api/quadras/{q}/entrar",
                    json={"apelido": str(i)},
                    headers={"x-session-id": f"s{i}"},
                )
                for i in range(8)
            ]
        )
        assert sorted(r.status_code for r in entradas) == [200] + [400] * 7


def test_sala_expirada_notifica_conexao_aberta_e_recusa_reconexao():
    with TestClient(app) as client:
        q = sala(client)["id"]
        with client.websocket_connect(f"/ws/{q}") as ws:
            ws.receive_json()
            ws.receive_json()
            expirar(q)
            ws.send_text("verificar")
            assert ws.receive_json()["tipo"] == "SALA_EXPIRADA"
            with pytest.raises(WebSocketDisconnect):
                ws.receive_json()
        assert ponto(client, q).status_code == 404
        with client.websocket_connect(f"/ws/{q}") as ws:
            assert ws.receive_json()["tipo"] == "SALA_EXPIRADA"


def test_restart_com_salas_ativas_nao_falha_por_fixture(monkeypatch, tmp_path):
    arquivo = tmp_path / "fixture.json"
    arquivo.write_text(json.dumps([{"nome": "Arena", "quadras": ["Quadra"]}]))
    monkeypatch.setattr(settings, "default_arenas_file", str(arquivo))
    monkeypatch.setattr(settings, "max_quadras", 1)
    sincronizar_fixtures_para_db_sync(settings.db_path, str(arquivo))
    with get_db() as conn:
        antigo = conn.execute("SELECT id FROM quadras").fetchone()["id"]
    expirar(antigo)
    limpar_quadras_expiradas_sync(settings.db_path)
    atual = criar_quadra_sync(settings.db_path, apelido="Admin", session_id="privado")
    init_db_sync()
    with get_db() as conn:
        assert [r["id"] for r in conn.execute("SELECT id FROM quadras")] == [
            atual["id"]
        ]


def test_erro_de_escrita_da_fixture_nao_deixa_criacao_parcial(monkeypatch, tmp_path):
    from app import fixtures

    arquivo = tmp_path / "fixtures" / "defaultArenas.json"
    arquivo.parent.mkdir()
    monkeypatch.setattr(settings, "default_arenas_file", str(arquivo))
    with TestClient(app) as client:
        arena = client.post("/api/arenas", json={"nome": "Arena"}).json()

        def falhar(*args):
            raise PermissionError("sem acesso")

        monkeypatch.setattr(fixtures.os, "replace", falhar)
        assert (
            client.post(
                f"/api/arenas/{arena['id']}/quadras", json={"nome": "Quadra"}
            ).status_code
            == 503
        )
        assert client.post("/api/arenas", json={"nome": "Outra"}).status_code == 503
        assert client.get("/api/quadras").json()["quadras"] == []
        assert len(client.get("/api/arenas").json()["arenas"]) == 1
        assert list(arquivo.parent.iterdir()) == [arquivo]


async def test_transferencias_concorrentes_deixam_um_unico_operador():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        q = (
            await client.post(
                "/api/quadras", json={"apelido": "A"}, headers={"x-session-id": "a"}
            )
        ).json()["id"]
        b = (
            await client.post(
                f"/api/quadras/{q}/entrar",
                json={"apelido": "B"},
                headers={"x-session-id": "b"},
            )
        ).json()["participante"]["id"]
        assert (
            await client.post(
                f"/api/quadras/{q}/participantes/{b}/admin",
                headers={"x-session-id": "a"},
            )
        ).status_code == 200
        await client.post(
            f"/api/quadras/{q}/controle/assumir", headers={"x-session-id": "b"}
        )
        await asyncio.gather(
            *[
                client.post(
                    f"/api/quadras/{q}/controle/assumir", headers={"x-session-id": s}
                )
                for s in ["a", "b"]
            ]
        )
        atual = (await client.get(f"/api/quadras/{q}")).json()
        respostas = await asyncio.gather(
            *[
                client.post(
                    f"/api/quadras/{q}/pontos",
                    json={"equipe": "A"},
                    headers={
                        "x-session-id": s,
                        "x-control-version": str(atual["controle_versao"]),
                    },
                )
                for s in ["a", "b"]
            ]
        )
        assert sorted(r.status_code for r in respostas) == [201, 403]


def test_pontos_concorrentes_nao_ultrapassam_vitoria():
    q = criar_quadra_sync(settings.db_path, apelido="Admin", session_id="privado")

    def marcar(_):
        try:
            executar_sync(
                settings.db_path, q["id"], "privado", "pontos", equipe="A", versao="1"
            )
            return 201
        except Exception as exc:
            from fastapi import HTTPException

            if not isinstance(exc, HTTPException):
                raise
            return exc.status_code

    for i in range(11):
        assert marcar(i) == 201
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(marcar, range(2))) == [201, 400]
