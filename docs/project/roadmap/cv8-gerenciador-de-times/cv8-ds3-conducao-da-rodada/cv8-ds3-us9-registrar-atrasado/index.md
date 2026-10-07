---
code: CV8.DS3.US9
level: User Story
status: Validated
status_reason: implementada em 0.41.0; aguarda validação do Navigator em lote
updated: 2026-10-07
---

# Registrar atrasado

## Intent

**Como** operador, **quero** incluir um atrasado na rodada em andamento, **para** ele jogar sem esperar.

## Acceptance / Done Condition

- **CA1:** Cada atrasado vira time incompleto no fim da fila, individualmente.
- **CA2:** Nunca pareia dois atrasados entre si.
- **CA3:** Bloqueado após início do mata-mata; o jogador fica presente para a próxima rodada.

Regras: RN-04, RN-06 (ver [regras-de-negocio.md](../../regras-de-negocio.md)).

## Validation Route

A definir no plano (Passo 2).

## Out of Scope

Formato trio e histórico entre sessões (fase 2).
