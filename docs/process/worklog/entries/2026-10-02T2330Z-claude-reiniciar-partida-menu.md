---
date: 2026-10-02T23:30:00Z
author: Claude Code (Driver)
kind: milestone
related:
  - feature/reiniciar-partida-menu
verification:
  - cd web && npm test && npm run check && npm run test:e2e
  - uv run pytest
  - Navigator: validado na web e no APK
---

# Reiniciar partida pelo menu ⋯

## What changed

Botão "Reiniciar partida" no menu ⋯ (web e quadra local do APK), com confirmação. Zera pontos e linha do tempo no meio da partida e mantém regras, nomes e tema.

## Why it matters

Antes só era possível recomeçar depois da partida encerrada. Corrigir um jogo iniciado errado exigia terminá-lo.

## Verification

pytest 226, npm test 164, e2e 51; Navigator validou web e APK.

## Follow-up

Relógio não tem o comando de zerar; sem e2e do clique no botão.
