---
date: 2026-09-27T02:00:00Z
author: Claude Code (Opus 5.5)
kind: milestone
related:
  - CV3.DS1.TS1
  - CV3.DS1.US4
  - fila-offline-aceita-devolucao-de-controle
verification:
  - pytest (198 passed); ruff limpo
  - gradlew testDebugUnitTest assembleDebug lintDebug (44 testes)
  - Navigator validou os cinco cenários físicos em 2026-09-26
---

# Fila offline do relógio sobrevive ao reinício

## What changed

O relógio grava o último placar confirmado com a fila: reaberto sem rede, mostra o placar e segue marcando. Os lances levam `base_seq`, e o servidor aceita a fila quando o controle volta ao relógio sem mudança na partida. Fila, placar e envio saíram do `WatchModel` para a `ScoreSync`, testada com servidor falso.

## Why it matters

É a base da US4: a partida continua no pulso sem conexão, e cada toque produz no máximo um efeito. A maior parte (fila, recibos idempotentes) já vinha da US2/US3; a TS1 fechou o reinício offline e a devolução de controle.

## Follow-up

CV3.DS1.US4 (revisão de conflito pelo telefone); envio com o app em segundo plano; testes da abertura e troca de quadra no `WatchModel`. A versão exibida estava parada em 0.10.1 (backend) e 0.12.0 (APK) e foi alinhada em 0.19.0.
