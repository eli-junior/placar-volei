---
code: CV8.DS6.US15
level: User Story
status: Validated
status_reason: implementada (0.45.0); aguarda validação do Navigator
updated: 2026-10-08
related:
  - ../../regras-de-negocio.md
---

# CV8.DS6.US15 — Rodada em trios

## Intent

O operador escolhe, ao sortear, entre **duplas** e **trios**. No trio a rodada inteira tem times de 3, mistos, e o resto do fluxo (fila, rei da quadra, mata-mata, desfazer, substituição, atrasado) funciona igual.

## Acceptance / Done Condition

Given 9 presentes (5 H e 4 M)
When o operador sorteia em trios
Then saem 3 trios equilibrados pela nota, cada um com ao menos 1 H e 1 M
And o placar, o relógio e o espectador mostram os 3 nomes.

Given 7 (ou 8) presentes
When sorteia em trios
Then o último a chegar (ou os 2 últimos) forma um time incompleto, por último na fila
And, na sua vez, escolhe os 2 (ou 1) parceiros pela lista de escalação, sem fechar trio de um sexo havendo alternativa.

Given menos de 6 presentes
When tenta sortear em trios
Then o sistema recusa, pedindo o mínimo de 6.

## Decisões (Navigator, 2026-10-08)

Rodada inteira em trios; trio misto salvo grupo de um sexo só; sobra é time incompleto que escolhe parceiros; placar igual (set único, alvo e vantagem iguais). Sem mulher/homem suficiente: minimiza trios de um sexo (como a RN-01). Sobra de 2 forma time de 2 que escolhe 1.

## Out of Scope

Formato misto na mesma rodada; alvo próprio para trio; histórico entre sessões.
