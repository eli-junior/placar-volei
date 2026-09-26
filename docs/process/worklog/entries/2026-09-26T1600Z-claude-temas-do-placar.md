---
date: 2026-09-26T16:00:00Z
author: Claude Code (Opus 5.5)
kind: milestone
related:
  - CV4.DS2.US3
verification:
  - .venv/bin/pytest (191 passed)
  - node --test web/tests (45 passed)
  - svelte-check (0 errors, 0 warnings)
  - vite build
  - ruff check app tests; ruff format --check app tests
  - Navigator approval on 2026-09-26
---

# Temas de placar escolhidos pelo administrador

## What changed

O administrador escolhe **Esportivo** ou **Clássico** nas configurações; a escolha fica na sala e troca na hora a representação de todos os papéis, sem tocar no estado da partida. O indicador **Ao vivo** ganhou a altura dos demais controles do cabeçalho.

## Why it matters

A sala tem uma identidade visual única para quem opera e quem acompanha, sem abrir mão do visual clássico conhecido e sem misturar essa escolha com claro/escuro, que continua do aparelho.

## Handoff

A implementação começou com o Codex (sessão 01a0dd8e) num worktree Windows e foi assumida no Passo 3 sem commits intermediários. O trabalho herdado tinha dois defeitos corrigidos antes do Checkpoint 2: bloco de tema duplicado que encerrava `configurar` antes das regras, e `ReiniciarPartidaBody` sem o campo enviado pelo modal.

## Follow-up

Representação clássica duplicada na operação (item de dívida `2026-09-26T1600Z`). `CV4.DS2.US2` (fullscreen) é a próxima história da DS2.
