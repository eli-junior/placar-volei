---
date: 2026-09-26T13:00:00Z
author: Claude Opus 5.5 (Driver)
kind: milestone
related:
  - CV3.DS2.US3
  - nova-partida-pelo-relogio-de-admin
  - debt-erro-de-entrada-pela-home-fora-da-vista
verification:
  - uv run pytest (185), ruff check, ruff format --check
  - Android: 36 testes, assembleDebug, lintDebug (JDK 21)
  - Teste físico no Galaxy Watch 8 aprovado pelo Navigator
---

# Nova Partida Rápida pelo Relógio

## What changed

- `nova_partida` em `/api/watch/comandos`, reusando o `reiniciar` do site; `pode_nova_partida` na sessão do relógio.
- Placar do relógio: com a partida encerrada, a faixa inferior vira **↶ Desfazer | ▶ Nova**.
- CV3.DS2 fecha com US1, US2 e US3.

## Why

O Navigator quer emendar partidas pelo pulso, sem pegar o telefone.

## Observação

Antes da US3, o Navigator relatou que **Entrar** na Home "não funcionava": o apelido salvo já estava em uso na quadra e o erro 409 aparecia fora da vista. Anotado como `debt-erro-de-entrada-pela-home-fora-da-vista`; a branch `fix/entrar-na-quadra-pela-home` ficou no remoto só com o registro.

## Follow-up

- Corrigir a entrada pela Home.
- Próximo no roadmap: `CV3.DS1.US4`.
