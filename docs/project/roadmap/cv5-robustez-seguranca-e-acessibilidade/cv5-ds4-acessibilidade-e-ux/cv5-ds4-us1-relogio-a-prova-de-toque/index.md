---
code: CV5.DS4.US1
level: User Story
status: Active
status_reason: Checkpoint 1 (plano) aguardando o Navigator
updated: 2026-09-27
---

# CV5.DS4.US1 — Relógio à prova de toque acidental

## Scope
- "▶ Nova" pede confirmação (segundo toque ou toque longo, vibração distinta) (`ScoreScreen.kt` ~236).
- Desfazer mostra a equipe do último ponto (`ScoreScreen.kt` ~228).
- Textos de 10–11sp sobem para 13–14sp; número previsto com traço e "(enviando)" no `contentDescription`.
- Espaçamentos ajustados para tela redonda de 40 mm.

## Acceptance
- Dado o fim da partida, quando toco "Nova" uma vez, então nada reinicia sem a confirmação.
- Então o Desfazer diz qual equipe perde o ponto.

## Plano

[plan.md](plan.md) — branch `feature/cv5-ds4-us1-relogio-a-prova-de-toque`.
