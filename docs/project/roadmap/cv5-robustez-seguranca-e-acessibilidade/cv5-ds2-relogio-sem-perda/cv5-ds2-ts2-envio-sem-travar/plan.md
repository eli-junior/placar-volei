# Plano — CV5.DS2.TS2 Envio sem travar

- **Nível:** Technical Story · **Branch:** `feature/cv5-ds2-ts2-envio-sem-travar` · **Versão:** patch (APK)

## Scope
1. `ScoreSync.sendNext` (`ScoreSync.kt:107`): 408, 425 e 429 viram `SEM_REDE` (o lance fica na fila); `Retry-After` do 429 é respeitado pelo `sendLoop`. Só 4xx definitivos (400, 403, 404, 409, 410, 422) sem recibo viram `held`.
2. Backoff exponencial com jitter no `sendLoop` (1 s → 30 s) em `SEM_REDE`, zerado ao primeiro sucesso.
3. Persistência fora da thread principal: `ScoreSync.tap/undo/applySnapshot` passam a `suspend` e gravam em `Dispatchers.IO.limitedParallelism(1)`. O invariante "grava antes do retorno visual" continua: a vibração e o `rev++` só acontecem depois do `fsync`.
4. Toque ignorado enquanto a gravação anterior não termina (flag `writing` no `WatchModel`; `ScoreScreen.kt:149`).

## Acceptance
- Dado o servidor devolvendo 429, quando marco um ponto, então o lance fica pendente e sai quando o servidor volta, sem descarte manual.
- Dado um 422 sem recibo, então o lance fica retido como hoje.
- Quando toco rápido várias vezes, então cada toque registrado vibra e a tela não trava.

## Design
Rejeitado: `runBlocking` ou gravar sem `fsync` (perde a durabilidade que a TS1 da CV3 garantiu). O dispatcher serial preserva a ordem dos lances.

## Out of Scope
Envio em segundo plano (WorkManager, US4).

## Risks
`tap` suspenso muda a assinatura usada nos testes da `ScoreSync` (44 testes): atualizar com `runTest`.

## Validation
Testes JVM com servidor falso devolvendo 429/408/422; no relógio, 10 toques rápidos e contagem conferida no telefone.
