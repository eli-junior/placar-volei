---
date: 2026-09-14T10:00:00Z
author: Antigravity (Driver)
kind: milestone
related:
  - CV1.DS1
  - CV1.DS1.TS3
verification:
  - uv run pytest (45 testes verdes em 3.26s)
  - uv run ruff check . ; uv run ruff format --check . (100% limpo)
  - npm --prefix web run build (sucesso em 468ms)
  - rota de validacao executada e aprovada pelo Navigator
---

# Fixtures e Persistência Declarativa de Arenas e Quadras (CV1.DS1.TS3)

## What changed

- **Arquivo `defaultArenas.json`:**
  - Criado na raiz do projeto contendo as arenas existentes ("T9 Beach Club" e "Tio Cleo") e suas quadras.
- **Módulo `app/fixtures.py`:**
  - Funções de carga e normalização de JSON, gravação atômica via arquivo temporário e substituição segura (`os.replace`).
  - Sincronização automática e idempotente de fixtures com o SQLite (`sincronizar_fixtures_para_db_sync`).
  - Funções de registro contínuo ao criar arenas ou quadras via API.
- **Ciclo de Vida do Banco (`app/db.py`, `app/quadras.py`):**
  - `init_db_sync` agora popula as fixtures automaticamente na inicialização do servidor quando o banco for novo ou estiver sem arenas.
  - `criar_arena_sync` e `criar_quadra_sync` atualizam `defaultArenas.json` no disco imediatamente.
  - Refatoração de `get_db` com `@contextmanager` e fechamento garantido no `finally: conn.close()`, eliminando descritores de arquivo abertos e bloqueios no Windows.
- **Empacotamento Docker (`Dockerfile`):**
  - Inclusão do arquivo `defaultArenas.json` no estágio de runtime do contêiner.
- **Ambiente de Testes (`tests/conftest.py`, `tests/test_fixtures.py`):**
  - Isolamento de fixtures em testes via `conftest.py`.
  - 7 novos testes automatizados cobrindo carga, salvamento, idempotência e recriação do banco a partir do arquivo JSON.

## Why it matters

- Permite que o operador da instância descarte e recrie o banco SQLite a qualquer momento sem perder os cadastros de clubes e quadras físicas.
- Mantém o arquivo versionado no Git para sincronização com o repositório no GitHub.
- Elimina vazamentos de descritores de conexões SQLite e simplifica a operação doméstica.

## Verification

- `uv run pytest`: 45 testes passando (100% verdes).
- `uv run ruff check .` e `uv run ruff format --check .`: 0 erros, código formatado.
- `npm --prefix web run build`: 0 erros, 0 avisos.
- Validado pelo Navigator conforme rotas do guia de teste.
