---
code: CV8.DS3.US7
level: User Story
status: Validated
status_reason: implementada em 0.43.0; aguarda validação do Navigator em lote
updated: 2026-10-07
---

# Desfazer última partida

## Intent

**Como** operador, **quero** desfazer a última partida encerrada, **para** corrigir erro de registro.

## Acceptance / Done Condition

- **CA1:** Restaura estado anterior completo (fila, reis, eliminados, vitórias, placar no painel).
- **CA2:** Apenas 1 nível de desfazer.

Regras: RN-09 (ver [regras-de-negocio.md](../../regras-de-negocio.md)).

## Validation Route

A definir no plano (Passo 2).

## Out of Scope

Formato trio e histórico entre sessões (fase 2).
