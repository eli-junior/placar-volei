---
code: CV8.DS2.US24
level: User Story
status: Validated
status_reason: validada pelo Navigator em 2026-10-15 (0.54.0)
updated: 2026-10-15
related:
  - ../../regras-de-negocio.md
  - ../../../../decisions/records/2026-10-15T1200Z-fila-por-tempo-sem-jogar.md
---

# Ímpar não fica sempre por último

## Intent

**Como** jogador, **quero** que o ímpar não seja sempre a mesma pessoa, **para** ninguém esperar mais em toda rodada. Antes o último a chegar ficava de ímpar, e no fim da fila, em todas as rodadas (RN-05).

## Acceptance / Done Condition

- **Dado** que a rodada 1 foi encerrada com número ímpar de presentes,
- **Quando** o operador sortear a rodada 2,
- **Então** o ímpar é quem jogou por último, entre os que não aumentam o número de duplas H+H (no empate, o último a chegar),
- **E** as duplas saem equilibradas com os demais (RN-01, RN-10, RN-14),
- **E** o time incompleto fica no fim da fila.
- Na 1ª rodada o ímpar é o último a chegar que não cria H+H evitável. No trio, a sobra de 1 ou 2 segue o mesmo critério, sem aumentar os trios de um sexo só (RN-16).

## Decisões (Navigator, 2026-10-15)

Quem jogou por último fica de ímpar; vale para o trio; o incompleto sempre no fim da fila; o gênero prevalece em todas as rodadas.

## Validation Route

[test-guide.md](test-guide.md).
