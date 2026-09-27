---
code: CV5.DS2.TS2
level: Technical Story
status: Planned
updated: 2026-09-27
---

# CV5.DS2.TS2 — Envio sem travar

## Scope
- 408, 425 e 429 tratados como falta de rede, com backoff; só recusas definitivas viram `held` (`ScoreSync.kt:107`).
- Gravação com `fsync` num dispatcher de IO serial, vibração depois de gravar (`CommandQueue.kt:69`, `WatchModel.kt:94`).
- Toque ignorado enquanto a gravação anterior não termina (`ScoreScreen.kt:149`).

## Acceptance
Um 429 do servidor não trava a fila; toques rápidos não travam a tela.
