---
date: 2026-09-26T12:00:00Z
author: Claude Opus 5.5 (Driver)
kind: milestone
related:
  - CV3.DS2.US2
  - batimento-no-relogio-por-measureclient
verification:
  - Android: testes unitários (HeartRateTest), assembleDebug
  - Teste físico no Galaxy Watch 8 com treino do Samsung Health aprovado pelo Navigator
---

# Batimento no Placar do Relógio

## What changed

- `HeartRate.kt`: `MeasureClient` lê o batimento enquanto o placar está visível; `♥ bpm` ao lado da bolinha de conexão.
- Permissões `BODY_SENSORS` e `READ_HEART_RATE` no manifest; pedido único em tempo de execução.
- CV3.DS2 fecha com a US1 e a US2.

## Why

O Navigator grava o treino no Samsung Health e queria ver o batimento sem sair do placar. O `ExerciseClient` encerraria esse treino.

## Follow-up

- Medir a bateria numa partida de 1 h com tela acesa e sensor ligado.
- Próximo: `CV3.DS1.US4`.
