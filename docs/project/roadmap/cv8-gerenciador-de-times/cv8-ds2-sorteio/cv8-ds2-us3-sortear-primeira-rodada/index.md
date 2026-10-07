---
code: CV8.DS2.US3
level: User Story
status: Validated
status_reason: validada pelo Navigator em 2026-10-07 (0.34.0); aguarda merge
updated: 2026-10-07
related:
  - ../../../../decisions/records/2026-10-08T0000Z-sorteio-da-primeira-rodada.md
---

# Sortear a primeira rodada

## Intent

**Como** operador, **quero** sortear as duplas aleatoriamente, **para** iniciar a rodada.

## Acceptance / Done Condition

- **CA1:** Bloqueado com menos de 4 presentes.
- **CA2:** Operador define alvo (10/12) antes do sorteio.
- **CA3:** Duplas equilibradas pela nota, sem aleatoriedade, respeitando RN-01 (RN-14).
- **CA4:** Ímpar → time incompleto no fim da fila (RN-05).
- **CA5:** Ordem da fila pela ordem de chegada (RN-13): quem chegou em 1º e em 2º jogam a primeira partida. O resultado aparece como **proposta** para **confirmar, resortear (outra combinação igualmente equilibrada) ou descartar** antes de iniciar.

Regras: RN-01, RN-05, RN-09, RN-11, RN-13, RN-14 (ver [regras-de-negocio.md](../../regras-de-negocio.md)).

## Entregue

Sorteio determinístico (gênero, nota, ímpar, fila pela chegada), proposta com resortear/descartar/confirmar, rodada em andamento com presença travada e cancelar. Plano: [plan.md](plan.md). Validação: [test-guide.md](test-guide.md).

## Validation Route

A definir no plano (Passo 2).

## Out of Scope

Formato trio e histórico entre sessões (fase 2).
