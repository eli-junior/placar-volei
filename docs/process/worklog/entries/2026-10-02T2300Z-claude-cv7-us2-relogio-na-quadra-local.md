---
date: 2026-10-02T23:00:00Z
author: Claude Code (Driver)
kind: milestone
related:
  - CV7.US2
verification:
  - cd web && npm test && npm run check && npm run test:e2e
  - uv run pytest
  - ./wear/gradlew -p wear testDebugUnitTest lintDebug assembleDebug
  - adb: Galaxy Watch SM-L330 contra a quadra local do Galaxy Z Fold
---

# Relógio na quadra local do celular

## What changed

O app do relógio mostra e opera a quadra local do celular, sem internet. O celular decide o modo: com a sala local aberta ele publica `sala_aberta` e um sinal de vida a cada 20 s, e o relógio (`CelularSessao`) entra na quadra local sozinho, com a tag **LOCAL**, a mesma fila durável e o mesmo desfazer, em fila própria. A tela do placar passou a depender de `PlacarFonte`.

## Why it matters

Fecha a CV7: o placar roda no celular sem servidor e o relógio marca nele pelo Bluetooth, com o mesmo contrato do servidor.

## Verification

163 testes do web, 51 e2e, 225 do backend e 81 do relógio. No aparelho: relógio entra sozinho, toques nos dois sentidos, desfazer, saída e volta da sala, e a queda do app do celular devolve o relógio ao servidor. Na revisão apareceu uma falha de desenho (com a tela do celular apagada o sinal para e o relógio largaria a partida com lances na fila), corrigida.

## Follow-up

Dívida: tela acesa (plano C se necessário), serviço em primeiro plano no modo local do relógio, caminhos nativos sem teste automático e release assinado com a mesma keystore. Para usar no relógio de produção é preciso um Wear 0.27.0 de release e revincular as quadras do servidor.
