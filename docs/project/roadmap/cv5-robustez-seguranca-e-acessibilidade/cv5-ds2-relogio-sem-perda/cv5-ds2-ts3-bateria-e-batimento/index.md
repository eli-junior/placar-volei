---
code: CV5.DS2.TS3
level: Technical Story
status: Active
status_reason: Checkpoint 1 (plano) aguardando o Navigator
updated: 2026-09-27
---

# CV5.DS2.TS3 — Bateria e sensor de batimento

## Scope
- Sensor de batimento ligado só com a Activity em STARTED (`HeartRate.kt:52`, `ScoreScreen.kt:67`).
- Sem polling de `/session` e `/state` com o WebSocket aberto; reconectar em falha com backoff (`WatchModel.kt:491`).
- Permissão por versão: `READ_HEART_RATE` no Wear OS 6, `BODY_SENSORS` antes (`HeartRate.kt:36`).
- **Decisão do Navigator:** tela sempre acesa, modo ambient ou tempo limite sem toque (`ScoreScreen.kt:63`).

## Acceptance
Com a tela apagada o sensor para; uma partida de 1 h gasta menos bateria que hoje (medir antes e depois).

## Plano

[plan.md](plan.md) — branch `feature/cv5-ds2-ts3-bateria-e-batimento`.
