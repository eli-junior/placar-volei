---
code: CV8.DS3.US10
level: User Story
status: Validated
status_reason: implementada em 0.42.0; aguarda validação do Navigator em lote
updated: 2026-10-07
---

# Substituir jogador que saiu

## Intent

**Como** operador, **quero** substituir um jogador que saiu de um time ativo, **para** manter o time sem perder suas vitórias.

## Acceptance / Done Condition

- **CA1:** Opções: jogador ímpar aguardando ou lista de escalação, respeitando RN-01.
- **CA2:** Vitórias e posição do time preservadas.
- **CA3:** Jogador que saiu é marcado ausente para próximas rodadas (reversível).

Regras: RN-07, RN-08 (ver [regras-de-negocio.md](../../regras-de-negocio.md)).

## Validation Route

A definir no plano (Passo 2).

## Out of Scope

Formato trio e histórico entre sessões (fase 2).
