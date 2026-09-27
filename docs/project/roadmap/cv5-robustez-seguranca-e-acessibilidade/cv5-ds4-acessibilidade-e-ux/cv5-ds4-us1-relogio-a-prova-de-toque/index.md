---
code: CV5.DS4.US1
level: User Story
status: Validated
status_reason: automode aprovado pelo Navigator em 2026-09-27; testes automatizados verdes
human_validation: pending
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

## Revisão (Passo 5)

- **Feito:** "Nova" em dois toques (`NEW_MATCH_CONFIRM_MS` = 3 s, vibração `CLOCK_TICK` ao armar); `undoLabel` e `undoDescription` puros, com teste; `ScoreSync.undoTeam`; textos de 13 sp; bolinha de 22 dp com 11 sp; "(enviando)" no número previsto; margem do motivo por `isScreenRound`.
- **Considerado e não feito:** toque longo (pouco descobrível e parecido com gestos do sistema).
- **Testes:** testes JVM (1 novo), build e lint verdes.
- **Débito novo:** nenhum.
- **Validação humana pendente:** no fim da partida, um toque em "Nova" não reinicia e dois toques reiniciam; o desfazer mostra "+1 {equipe}"; os textos cabem no relógio de 40 mm; com TalkBack, o desfazer lê o nome da equipe.
