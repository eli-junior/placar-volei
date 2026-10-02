"""As fixtures de paridade versionadas precisam refletir a regra atual (CV7.TS2).

Se este teste falhar, a regra em Python mudou: regere com
`uv run python -m tests.paridade_fixtures`, confira o diff e ajuste
`web/src/lib/partida.js` até `npm test` passar de novo.
"""

from tests.paridade_fixtures import CAMINHO, gerar


def test_fixtures_de_paridade_estao_em_dia():
    assert CAMINHO.read_text(encoding="utf-8") == gerar(), (
        "web/tests/fixtures/paridade.json está desatualizado: "
        "rode `uv run python -m tests.paridade_fixtures` e porte a mudança para o JS."
    )
