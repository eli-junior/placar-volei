---
date: 2026-09-26T03:00:00Z
author: Claude Opus 5.5 (Driver)
kind: milestone
related:
  - CV3.DS2.US1
  - CV3.DS2.US2
  - tela-acesa-no-placar-do-relogio
verification:
  - Android: 33 testes, assembleDebug, lintDebug (0 erros)
  - uv run pytest, ruff check, ruff format --check
  - Teste físico no Galaxy Watch 8 aprovado pelo Navigator
---

# Tela Acesa no Placar do Relógio

## What changed

- Novo Delivery Story `CV3.DS2`, relógio durante o jogo e o treino, pedido pelo Navigator.
- O placar do relógio liga `keepScreenOn` enquanto está visível. Vínculo e escolha seguem o tempo normal.
- `.gitattributes` fixa LF em `gradlew` e `*.sh`: com `core.autocrlf=true`, o checkout do Windows quebrava o wrapper no WSL.

## Why

A tela apagava no meio do jogo e o primeiro toque só acordava o relógio. A decisão do DS1 de não manter a tela acesa foi substituída.

## Observação

Um daemon Gradle antigo, no JDK 25, fez o build falhar com `IllegalArgumentException: 25.0.4.1`. `--stop` e o JDK 21 resolveram.

## Follow-up

- Medir a bateria numa partida de 1 h com o placar aceso (adiado pelo Navigator).
- `CV3.DS2.US2`: frequência cardíaca e duração do exercício do Samsung Health no placar.
