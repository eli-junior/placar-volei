---
date: 2026-09-15T17:30:00Z
author: Antigravity (Driver)
kind: milestone
related:
  - debt-arenas-legadas
verification:
  - uv run pytest (90 testes aprovados)
  - uv run ruff check . (0 erros)
  - npm run check (0 erros)
  - npm run build (sucesso)
---

# Faxina Técnica: Remoção de Arenas, Fixtures e Banco Limpo no Versionamento

## What changed

- Eliminação completa de arquivos de fixture (`fixtures/defaultArenas.json`), módulo de auto-seeding (`app/fixtures.py`) e componentes órfãos no frontend (`ModalCriarArena.svelte`, `ListaArenas.svelte`, `ListaQuadras.svelte`).
- Remoção definitiva da tabela `arenas`, coluna `arena_id` e endpoints `/api/arenas/*`.
- Configuração do SQLite e `init_db_sync` para garantir que o banco inicie 100% vazio (zero quadras, zero participantes).
- Garantia de que ao detectar uma nova versão no `app_meta`, o banco anterior é descartado e nasce estéril sem re-popular nenhuma quadra pré-existente.
- Blindagem no roteador de SPA em `app/main.py` para nunca responder com o fallback de HTML (200 OK) para rotas de API inexistentes com prefixo `/api/*`, retornando corretamente `HTTP 404 Not Found`.
- Adição da suíte de testes `tests/test_banco_limpo_versao.py` validando os cenários de banco limpo e rejeição de rotas legadas.
- Pagamento integral do débito técnico `debt-arenas-legadas`.
- Bump de versão para `0.4.2`.

## Why it matters

Ao atualizar para uma versão nova, o Navigator observava que 12 quadras prévias reapareciam como ativas. Isso ocorria porque a rotina de inicialização lia `defaultArenas.json` e repovoava o banco a cada boot. Com esta faxina, mais de 1.600 linhas de código legado foram expurgadas, e ao subir uma versão nova, o sistema passa a iniciar genuinamente limpo.

## Verification

- Executados 90 testes automatizados cobrindo todo o ciclo de vida do sistema com 100% de aprovação.
- Verificação estática via Ruff e Svelte Check concluídas sem erros.
- Build de frontend para produção validado via Vite.
