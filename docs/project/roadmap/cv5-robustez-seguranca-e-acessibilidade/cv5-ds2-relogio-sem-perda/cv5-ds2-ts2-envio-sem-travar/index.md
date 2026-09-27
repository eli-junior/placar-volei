---
code: CV5.DS2.TS2
level: Technical Story
status: Done
status_reason: aceito pelo Navigator em 2026-09-27 (teste conjunto da integracao/cv5)
human_validation: accepted
updated: 2026-09-27
---

# CV5.DS2.TS2 — Envio sem travar

## Scope
- 408, 425 e 429 tratados como falta de rede, com backoff; só recusas definitivas viram `held` (`ScoreSync.kt:107`).
- Gravação com `fsync` num dispatcher de IO serial, vibração depois de gravar (`CommandQueue.kt:69`, `WatchModel.kt:94`).
- Toque ignorado enquanto a gravação anterior não termina (`ScoreScreen.kt:149`).

## Acceptance
Um 429 do servidor não trava a fila; toques rápidos não travam a tela.

## Plano

[plan.md](plan.md) — branch `feature/cv5-ds2-ts2-envio-sem-travar`.

## Revisão (Passo 5)

- **Feito:** `SendResult.ADIADO` para 408/425/429 com backoff até 30 s (sem marcar "sem conexão"); todas as mutações da `ScoreSync` no dispatcher `Dispatchers.IO.limitedParallelism(1)`; `state`/`score` `@Volatile`; `tap`/`undo` com callback e trava `writing`.
- **Ajuste ao plano:** `ScoreSync` continuou síncrona (o `WatchModel` decide a thread), então os 44 testes antigos não mudaram; `Retry-After` não é lido (o `/api/watch/comandos` não devolve 429 hoje; o backoff cobre o caso do Cloudflare).
- **Testes:** 46 testes JVM (2 novos), build e lint (12 avisos, iguais à `master`).
- **Risco residual:** interleaving entre envio e toque é o mesmo de antes (o dispatcher serial se comporta como a thread principal); nenhum lock novo.
- **Validação humana pendente:** 10 toques rápidos no relógio e a contagem igual no telefone; vibração em cada toque aceito.
