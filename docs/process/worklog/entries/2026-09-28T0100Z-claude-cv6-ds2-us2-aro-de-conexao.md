---
date: 2026-09-28T01:00:00Z
author: Claude Code (Driver)
kind: milestone
related:
  - CV6.DS2.US2
verification:
  - 53 testes JVM do relógio
  - build debug/release e lint Android
  - validação manual do Navigator no Galaxy Watch real
---

# CV6.DS2.US2 — aro de conexão no relógio

## What changed

A bolinha de conexão do cabeçalho virou um aro fino na borda da tela: verde conectado, amarelo reconectando ou enviando, vermelho sem conexão. Os batimentos ficam sozinhos no centro; pendentes aparecem como `↑N` só quando existem.

## Why it matters

O centro da tela fica livre para a leitura no pulso, e o estado da conexão continua visível à distância sem disputar com os números. A cor usa o mesmo sinal de antes, então não há estado paralelo que possa mentir.

## Verification

Testes JVM, builds e lint passaram. O Navigator validou no relógio a queda, a fila e a reconexão. Testes de tela do relógio seguem no débito existente.

## Follow-up

CV6.DS2.US3 (perceber pontos registrados) e US4 (apagar a tela e retomar).
