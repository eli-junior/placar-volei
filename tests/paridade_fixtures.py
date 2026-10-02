"""Fixtures de paridade Python ↔ JS das regras da partida (CV7.TS2).

O Python é a referência. Este módulo roda cenários no backend de verdade (pela
API) e projeções de logs montados à mão, e grava o resultado em
`web/tests/fixtures/paridade.json`. O teste do JS (`web/tests/paridade.test.js`)
refaz os mesmos cenários em `web/src/lib/partida.js` e exige resultado igual.
`tests/test_paridade_fixtures.py` falha se o arquivo versionado ficou para trás.

Regerar:  uv run python -m tests.paridade_fixtures
"""

import asyncio
import json
import random
import tempfile
from dataclasses import asdict
from pathlib import Path
from typing import Any

import httpx
from httpx import ASGITransport

from app.config import settings
from app.db import init_db
from app.eventos import Evento, TipoEvento
from app.main import app
from app.projecao import projetar_estado, projetar_linha_do_tempo
from app.rate_limit import entrada_rate_limiter

CAMINHO = Path(__file__).resolve().parent.parent / "web/tests/fixtures/paridade.json"
APELIDO = "Eli"
T = TipoEvento


def evento(seq: int, tipo: str, payload: dict[str, Any], autor: str | None = "u1"):
    return Evento(
        id=f"e{seq}",
        quadra_id="q1",
        partida_id="p1",
        seq=seq,
        tipo=tipo,
        payload=payload,
        autor_id=autor,
        criado_em=f"2026-10-01T12:00:{seq:02d}+00:00",
    )


def _projecao(nome: str, eventos: list[Evento], apelidos: dict[str, str] | None = None):
    apelidos = apelidos or {"u1": APELIDO, "u2": "Bia"}
    return {
        "nome": nome,
        "eventos": [asdict(e) for e in eventos],
        "apelidos": apelidos,
        "estado": asdict(projetar_estado(eventos)),
        "linha_do_tempo": projetar_linha_do_tempo(eventos, apelidos),
    }


def projecoes() -> list[dict[str, Any]]:
    """Logs montados à mão, inclusive os eventos de governança e bordas."""
    ini = (1, T.PARTIDA_INICIADA, {"alvo": 3, "vantagem": True, "teto": None})
    pontos = [(i + 2, T.PONTO_MARCADO, {"equipe": "AB"[i % 2]}) for i in range(6)]
    casos = [
        ("vazio", []),
        ("so-iniciada", [evento(*ini)]),
        ("sem-iniciada: padrões", [evento(1, T.PONTO_MARCADO, {"equipe": "a"})]),
        (
            "equipe minúscula e inválida",
            [
                evento(*ini),
                evento(2, T.PONTO_MARCADO, {"equipe": "b"}),
                evento(3, T.PONTO_MARCADO, {"equipe": "X"}),
                evento(4, T.PONTO_MARCADO, {}),
            ],
        ),
        (
            "alternados com desfazer em cadeia",
            [evento(*ini)]
            + [evento(*p) for p in pontos]
            + [
                evento(8, T.PONTO_DESFEITO, {"ref_seq": 7}),
                evento(9, T.PONTO_DESFEITO, {"ref_seq": 6}),
                evento(10, T.PONTO_DESFEITO, {"ref_seq": 6}),
                evento(11, T.PONTO_DESFEITO, {"ref_seq": 99}),
                evento(12, T.PONTO_DESFEITO, {}),
            ],
        ),
        (
            "vitória com vantagem e teto",
            [evento(1, T.PARTIDA_INICIADA, {"alvo": 3, "vantagem": True, "teto": 5})]
            + [evento(i + 2, T.PONTO_MARCADO, {"equipe": "A"}) for i in range(5)]
            + [
                evento(7, T.PARTIDA_ENCERRADA, {"vencedor": "A"}),
            ],
        ),
        (
            "sem vantagem",
            [evento(1, T.PARTIDA_INICIADA, {"alvo": 2, "vantagem": False})]
            + [evento(i + 2, T.PONTO_MARCADO, {"equipe": "B"}) for i in range(2)]
            + [evento(4, T.PARTIDA_ENCERRADA, {"vencedor": "B"})],
        ),
        (
            "regras e nomes alterados no meio",
            [
                evento(*ini),
                evento(2, T.PONTO_MARCADO, {"equipe": "A"}),
                evento(
                    3,
                    T.REGRA_ALTERADA,
                    {
                        "alvo": 15,
                        "vantagem": False,
                        "teto": 20,
                        "equipe_a": "Ana / Bia",
                        "equipe_b": "Cris",
                        "jogadores_a": ["Ana", "Bia"],
                        "jogadores_b": ["Cris"],
                    },
                ),
                evento(4, T.REGRA_ALTERADA, {"teto": None}),
                evento(5, T.REGRA_ALTERADA, {}),
                evento(6, T.REGRA_ALTERADA, {"equipe_b": "Dani"}),
                evento(7, T.PONTO_MARCADO, {"equipe": "B"}),
            ],
        ),
        (
            "governança e autores",
            [
                evento(*ini),
                evento(2, T.CONTROLE_ASSUMIDO, {}, "u2"),
                evento(3, T.CONTROLE_TRANSFERIDO, {"apelido": "Bia"}),
                evento(4, T.CONTROLE_TRANSFERIDO, {}),
                evento(
                    5,
                    T.CONTROLE_DEVOLVIDO,
                    {"anterior_apelido": "Bia", "apelido": "Eli"},
                    None,
                ),
                evento(6, T.CONTROLE_DEVOLVIDO, {"motivo": "relogio_trocou_de_quadra"}),
                evento(7, T.CONTROLE_DEVOLVIDO, {"motivo": "relogio_revogado"}),
                evento(8, T.CONTROLE_DEVOLVIDO, {"motivo": "relogio_desabilitado"}),
                evento(9, T.CONTROLE_DEVOLVIDO, {}),
                evento(
                    10, T.PAPEL_ALTERADO, {"papel": "CONTROLADOR", "apelido": "Bia"}
                ),
                evento(11, T.PAPEL_ALTERADO, {"papel": "ESPECTADOR", "apelido": "Bia"}),
                evento(12, T.PAPEL_ALTERADO, {"papel": "ADMIN", "apelido": "Bia"}),
                evento(13, T.PAPEL_ALTERADO, {"papel": "OUTRO"}),
                evento(
                    14,
                    T.ADMIN_SUCEDIDO,
                    {"novo_admin_apelido": "Bia", "antigo_admin_apelido": "Eli"},
                ),
                evento(15, T.ADMIN_SUCEDIDO, {"antigo_admin_apelido": "Eli"}),
                evento(16, T.ADMIN_ASSUMIDO, {}, "desconhecido"),
                evento(17, T.PARTIDA_ENCERRADA, {"vencedor": "B"}),
                evento(18, T.PARTIDA_ENCERRADA, {"vencedor": "?"}),
            ],
        ),
    ]
    return [_projecao(nome, eventos) for nome, eventos in casos]


# --- Cenários de comando, pelo backend de verdade ---------------------------


def _passos_fixos() -> list[tuple[str, list[dict[str, Any]], dict[str, Any]]]:
    A = {"acao": "pontos", "equipe": "A"}
    B = {"acao": "pontos", "equipe": "B"}
    D = {"acao": "desfazer"}
    reiniciar = {"acao": "reiniciar", "campos": {}}
    return [
        (
            "até 3, vitória direta e bloqueio",
            [A, B, A, A, A, B, D, D, D, D, D, D, D],
            {"alvo": 3},
        ),
        (
            "vantagem de 2 e reabertura ao desfazer",
            [A, A, B, B, A, B, A, A, B, B, A, A, D, D, B, B, B],
            {"alvo": 3, "vantagem": True},
        ),
        ("teto encerra a vantagem", [A, B] * 4 + [A, A, A], {"alvo": 2, "teto": 4}),
        (
            "sem vantagem",
            [A, B, A, B, A, A, D],
            {"alvo": 3, "vantagem": False},
        ),
        ("desfazer sem pontos", [D, A, D, D], {"alvo": 3}),
        (
            "equipe inválida e ponto depois do fim",
            [
                {"acao": "pontos", "equipe": "C"},
                {"acao": "pontos", "equipe": " b "},
                {"acao": "pontos", "equipe": "A"},
                A,
                B,
                A,
                A,
            ],
            {"alvo": 2, "vantagem": False},
        ),
        (
            "reiniciar antes do fim e depois do fim herdando regras",
            [reiniciar, A, A, reiniciar, A, B, D, reiniciar],
            {"alvo": 2, "vantagem": False, "equipe_a": "Azuis", "equipe_b": "Verdes"},
        ),
        (
            "reiniciar com regras e nomes novos",
            [
                A,
                A,
                {
                    "acao": "reiniciar",
                    "campos": {
                        "time_a_jogador1": "Ana",
                        "time_a_jogador2": "Bia",
                        "equipe_b": "Cris",
                        "alvo": 5,
                        "vantagem": False,
                        "teto": 7,
                    },
                },
                B,
                A,
                {"acao": "reiniciar", "campos": {"teto": 9, "alvo": 1}},
            ],
            {"alvo": 2, "vantagem": False},
        ),
        (
            "configurar no meio e inválidos",
            [
                A,
                {"acao": "configurar", "campos": {"equipe_a": "Rubros", "alvo": 4}},
                {"acao": "configurar", "campos": {}},
                {"acao": "configurar", "campos": {"alvo": 0}},
                {"acao": "configurar", "campos": {"alvo": 101}},
                {"acao": "configurar", "campos": {"teto": 201}},
                {"acao": "configurar", "campos": {"equipe_a": "x" * 61}},
                {"acao": "configurar", "campos": {"time_b_jogador1": "y" * 31}},
                {"acao": "configurar", "campos": {"vantagem": False}},
                {
                    "acao": "configurar",
                    "campos": {"time_b_jogador1": " Edu ", "time_b_jogador2": "Fê"},
                },
                {"acao": "configurar", "campos": {"equipe_b": "   "}},
                {"acao": "configurar", "campos": {"alvo": 1, "teto": 1}},
                B,
                A,
            ],
            {"alvo": 3},
        ),
        (
            "configurar muda a regra e encerra ou reabre",
            [
                A,
                A,
                {"acao": "configurar", "campos": {"alvo": 2, "vantagem": False}},
                {"acao": "configurar", "campos": {"alvo": 5}},
                A,
            ],
            {"alvo": 3, "vantagem": False},
        ),
    ]


def _passos_aleatorios(semente: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rng = random.Random(semente)
    criar = {
        "alvo": rng.choice([1, 2, 3, 5, 11]),
        "vantagem": rng.choice([True, False]),
        "teto": rng.choice([None, None, 6, 9]),
    }
    if criar["teto"] is not None and criar["teto"] < criar["alvo"]:
        criar["teto"] = None
    passos: list[dict[str, Any]] = []
    for _ in range(70):
        sorte = rng.random()
        if sorte < 0.55:
            passos.append({"acao": "pontos", "equipe": rng.choice("AB")})
        elif sorte < 0.75:
            passos.append({"acao": "desfazer"})
        elif sorte < 0.88:
            passos.append({"acao": "reiniciar", "campos": _campos(rng)})
        else:
            passos.append({"acao": "configurar", "campos": _campos(rng)})
    return passos, criar


def _campos(rng: random.Random) -> dict[str, Any]:
    campos: dict[str, Any] = {}
    if rng.random() < 0.4:
        campos["alvo"] = rng.choice([0, 1, 2, 3, 6, 101])
    if rng.random() < 0.3:
        campos["vantagem"] = rng.choice([True, False])
    if rng.random() < 0.3:
        campos["teto"] = rng.choice([1, 3, 8, 201])
    if rng.random() < 0.3:
        campos["equipe_a"] = rng.choice(["Azuis", "  ", "Rubros", "z" * 61])
    if rng.random() < 0.2:
        campos["time_b_jogador1"] = rng.choice(["Edu", " ", "w" * 31])
        campos["time_b_jogador2"] = rng.choice(["Fê", "", None])
    return campos


def _normalizar(snapshot: dict[str, Any], ordinais: dict[str, str]) -> dict[str, Any]:
    """Tira o que varia a cada execução: ids, horários e o id de cada partida."""

    def partida(id_: str | None) -> str | None:
        if id_ is None:
            return None
        return ordinais.setdefault(id_, f"P{len(ordinais) + 1}")

    estado = dict(snapshot["estado_partida"])
    estado["partida_id"] = partida(estado["partida_id"])
    itens = [
        {k: v for k, v in item.items() if k not in ("id", "criado_em", "autor_id")}
        for item in snapshot["linha_do_tempo"]
    ]
    return {
        "partida_id": partida(snapshot["partida_id"]),
        "seq": snapshot["seq"],
        "estado_partida": estado,
        "linha_do_tempo": itens,
    }


async def _rodar(
    nome: str, passos: list[dict[str, Any]], criar: dict[str, Any]
) -> dict[str, Any]:
    entrada_rate_limiter.resetar()
    ordinais: dict[str, str] = {}
    resultados: list[dict[str, Any]] = []
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.post("/api/quadras", json={"apelido": APELIDO, **criar})
        assert resp.status_code == 201, resp.text
        quadra = resp.json()
        qid = quadra["id"]
        headers = {"x-control-version": "1"}
        estado = (await client.get(f"/api/quadras/{qid}/partida")).json()
        linha = (await client.get(f"/api/quadras/{qid}/linha-do-tempo")).json()
        inicial = _normalizar(
            {
                "partida_id": estado["partida_id"],
                "seq": linha["itens"][-1]["seq"],
                "estado_partida": estado["estado_partida"],
                "linha_do_tempo": linha["itens"],
            },
            ordinais,
        )
        for passo in passos:
            acao = passo["acao"]
            if acao == "pontos":
                r = await client.post(
                    f"/api/quadras/{qid}/pontos",
                    headers=headers,
                    json={"equipe": passo["equipe"]},
                )
            elif acao == "desfazer":
                r = await client.post(f"/api/quadras/{qid}/desfazer", headers=headers)
            else:
                r = await client.post(
                    f"/api/quadras/{qid}/{acao}",
                    headers=headers,
                    json=passo["campos"],
                )
            if r.status_code < 400:
                resultados.append(
                    {
                        "status": r.status_code,
                        "snapshot": _normalizar(r.json(), ordinais),
                    }
                )
            else:
                # O 422 do Pydantic descreve campos; só o status importa.
                detalhe = None if r.status_code == 422 else r.json()["detail"]
                resultados.append({"status": r.status_code, "detalhe": detalhe})
    return {
        "nome": nome,
        "criar": criar,
        "apelido": APELIDO,
        "inicial": inicial,
        "passos": passos,
        "resultados": resultados,
    }


async def _cenarios() -> list[dict[str, Any]]:
    cenarios = []
    for nome, passos, criar in _passos_fixos():
        cenarios.append(await _rodar(nome, passos, criar))
    for semente in range(1, 9):
        passos, criar = _passos_aleatorios(semente)
        cenarios.append(await _rodar(f"aleatório {semente}", passos, criar))
    return cenarios


async def _gerar_async() -> dict[str, Any]:
    # O .env local não pode mudar o resultado (cookie seguro exige https).
    ajustes = {
        "db_path": None,
        "max_quadras": 500,
        "cookie_secure": False,
        "trust_cloudflare": False,
        "producao": False,
    }
    original = {k: getattr(settings, k) for k in ajustes}
    with tempfile.TemporaryDirectory() as pasta:
        ajustes["db_path"] = str(Path(pasta) / "paridade.db")
        for k, v in ajustes.items():
            setattr(settings, k, v)
        try:
            await init_db(settings.db_path)
            cenarios = await _cenarios()
        finally:
            for k, v in original.items():
                setattr(settings, k, v)
    return {"projecoes": projecoes(), "cenarios": cenarios}


def gerar() -> str:
    return json.dumps(asyncio.run(_gerar_async()), ensure_ascii=False, indent=1) + "\n"


if __name__ == "__main__":
    CAMINHO.parent.mkdir(parents=True, exist_ok=True)
    CAMINHO.write_text(gerar(), encoding="utf-8")
    print(f"Gravado {CAMINHO}")
