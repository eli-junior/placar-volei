---
date: 2026-10-02T22:00:00Z
author: Claude Code (Driver)
kind: milestone
related:
  - CV7.TS3
verification:
  - cd web && npm test && npm run check && npm run test:e2e
  - uv run pytest
  - ./wear/gradlew -p wear testDebugUnitTest lintDebug assembleDebug
  - adb: DebugCelular no Galaxy Watch SM-L330 contra a quadra local do Galaxy Z Fold
---

# Ponte Data Layer entre o celular e o relógio

## What changed

O relógio envia lances à quadra local do celular pelo Bluetooth e recebe o recibo e o estado, com o mesmo contrato do servidor. O celular aplica uma vez só (recibos gravados com o log), publica o estado como DataItem e atende com o plugin `PlacarRelogio`. O `applicationId` do relógio passou a `br.com.placarvolei`.

## Why it matters

É o canal que permite ao relógio marcar a quadra local sem internet (CV7.US2). O spike mostrou que o JS do WebView para depois de ~2 min com a tela apagada; o plano B mantém a tela acesa e a fila do relógio segura o resto.

## Verification

161 testes do web, 225 do backend, 59 do relógio e lint limpo. No aparelho (Z Fold + Galaxy Watch SM-L330, builds debug com a mesma assinatura): ponto A, A, B e desfazer aplicados, e com o celular fora da sala o lance ficou na fila e entrou uma vez só ao reabrir. A validação achou um bug que os testes não pegam: devolver o proxy do plugin de uma função `async` faz o Capacitor responder "`.then()` is not implemented".

## Follow-up

Próxima: CV7.US2 (a tela do relógio para a quadra local e a escolha do modo). Dívida: tela acesa (plano C se necessário), caminhos nativos sem teste automático, release assinado com a mesma keystore.
