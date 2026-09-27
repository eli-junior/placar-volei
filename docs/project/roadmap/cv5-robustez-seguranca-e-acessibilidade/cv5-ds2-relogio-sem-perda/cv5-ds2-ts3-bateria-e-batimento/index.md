---
code: CV5.DS2.TS3
level: Technical Story
status: Done
status_reason: aceito pelo Navigator em 2026-09-27 (teste conjunto da integracao/cv5)
human_validation: accepted
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

## Revisão (Passo 5)

- **Feito:** `LifecycleStartEffect` no batimento; sem `refresh()` com socket aberto, `poke` ao fechar/falhar e backoff de reconexão 2→30 s; tela liberada após 10 min sem atividade (decisão do Navigator: timeout, não ambient).
- **Movido:** permissão granular `READ_HEART_RATE` para a `CV5.DS2.TS4` (só vale com targetSdk 36).
- **Débito novo (pequeno):** `pode_nova_partida` (admin do dono) só é relido em `refresh()`; se o dono virar admin com o socket aberto, o "▶ Nova" aparece só após reconectar. Revisitar se aparecer no uso.
- **Não medido:** bateria antes/depois (exige o relógio; fica no roteiro).
- **Testes:** 44 testes JVM, build e lint (12 avisos, iguais à `master`).
- **Validação humana pendente:** sair do app pelo botão e ver o batimento sumir do Samsung Health? (não deve afetar o treino); 5 min com socket aberto sem `/api/watch/session` no log do servidor; tela apaga após 10 min parado; partida de 30 min comparando bateria.
