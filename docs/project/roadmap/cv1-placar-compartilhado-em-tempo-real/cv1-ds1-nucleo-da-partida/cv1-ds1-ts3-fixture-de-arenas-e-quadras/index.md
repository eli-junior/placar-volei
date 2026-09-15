---
code: CV1.DS1.TS3
level: Technical Story
status: Superseded
status_reason: Aposentada na v0.4.2; fixtures e arenas foram removidas em definitivo com o modelo de salas efêmeras por PIN
updated: 2026-09-15
related:
  - CV1.DS1
  - CV1.DS1.US1
  - 2026-09-15T1730Z-remocao-de-arenas-e-banco-limpo-no-versionamento.md
---

# CV1.DS1.TS3 — Fixture e Persistência Declarativa de Arenas e Quadras

## Intent

Preservar os nomes de arenas e suas respectivas quadras em arquivo declarativo (`defaultArenas.json`), permitindo que a cada recriação ou reinício do banco de dados SQLite esses dados sejam restaurados automaticamente sem perda, enquanto os demais registros (partidas encerradas, participantes, histórico descartável) possam ser resetados.

## Scope

- Definição do arquivo declarativo `defaultArenas.json` na raiz do repositório, versionável no Git.
- Módulo `app/fixtures.py` para carga, salvamento atômico e sincronização idempotente com o SQLite.
- Execução automática da população das fixtures durante a inicialização do banco (`init_db_sync`).
- Atualização contínua de `defaultArenas.json` no disco a cada nova arena ou quadra cadastrada via API.
- Configuração `default_arenas_file` em `app/config.py`.
- Inclusão do `defaultArenas.json` no `Dockerfile` multi-estágio para disponibilidade no ambiente containerizado.
- Cobertura com testes automatizados e isolamento via `conftest.py`.

## Acceptance / Done Condition

Given que o arquivo `data/placar.db` foi removido ou reinicializado do zero
When o servidor inicia e executa `init_db`
Then as arenas e quadras contidas em `defaultArenas.json` são criadas automaticamente no banco
And cada quadra inicializada possui sua partida ativa com regra padrão e evento inicial
And ao cadastrar uma nova arena ou quadra em tempo de execução, `defaultArenas.json` é atualizado no disco.

## Validation Route

1. Executar `uv run pytest` e validar os 45 testes verdes (incluindo `tests/test_fixtures.py`).
2. Testar recriação manual do banco de dados e verificar restauração automática das arenas.
3. Cadastrar uma nova arena via UI ou API e inspecionar a atualização de `defaultArenas.json`.

## Out of Scope

- Persistência de participantes antigos ou cookies de sessão.
- Scripts com push não autorizado para o Git no runtime da API.
