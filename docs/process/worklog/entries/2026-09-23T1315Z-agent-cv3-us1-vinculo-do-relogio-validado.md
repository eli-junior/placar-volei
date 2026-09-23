---
date: 2026-09-23T13:15:00Z
author: Claude Opus 5.5 (Driver)
kind: milestone
related:
  - CV3.DS1.US1
  - apelido-senha-habilita-relogio
  - debt-limite-de-vinculo-do-relogio-por-ip-e-em-memoria
  - debt-banco-de-producao-sem-volume-persistente
verification:
  - .venv/bin/pytest -q (133 passed)
  - .venv/bin/ruff check . e ruff format --check . (passaram)
  - web: npm test (22 passed), npm run check (0 erros, 0 avisos), npm run build
  - Validação física no Galaxy Watch em produção aprovada pelo Navigator
---

# Vínculo do Relógio Validado em Produção

## What changed

- Retomada da US1 depois do handoff do Codex. A API do relógio tinha chegado à master e à produção por `feature/cv3-ds1-us1-api-relogio`; as duas branches foram unificadas.
- O primeiro teste físico achou o campo do código recusando todo código: em template Svelte, `pattern="[0-9]{8}"` saía como `[0-9]8`. Corrigido, com teste que compila o componente.
- O Navigator aprovou os cenários 1–4 do test-guide em produção.
- No Checkpoint 3, a habilitação passou a ser pelo apelido-senha `eli.relogio`, exibido como `eli`. Aprovação e modal usam o apelido real em vez de `eli` fixo.

## Why

Habilitar pelo terminal em cada sala pesava no uso real, e habilitar pelo apelido público deixava o acesso ser copiado. O apelido-senha resolve os dois.

## Follow-up

- US2: ver e marcar pontos no relógio.
- Dívidas registradas: limite de vínculo por IP/em memória, e banco sem volume.
- Remover a branch `fix/codigo-relogio-pattern`, criada por engano.
