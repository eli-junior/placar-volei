---
code: CV8.DS1.US1
level: User Story
status: Validated
status_reason: validada pelo Navigator em 2026-10-07 (0.31.0); aguarda merge
updated: 2026-10-07
related:
  - ../../../../decisions/records/2026-10-07T1800Z-base-de-jogadores-duravel-e-protegida.md
---

# Cadastrar jogadores

## Intent

**Como** operador, **quero** manter uma base persistente de jogadores (nome, gênero), **para** não redigitar a cada sessão.

## Acceptance / Done Condition

- **CA1:** Criar, editar e inativar jogador (nome obrigatório, gênero H/M obrigatório).
- **CA2:** Nome único na base ativa.
- **CA3:** Dados persistem entre reinícios do servidor.

## Validation Route

A definir no plano (Passo 2).

## Entregue

Base em arquivo próprio e durável (volume `gerenciador-dados`), protegida pelo `OWNER_SECRET`, tela `/jogadores` oculta no APK. Plano: [plan.md](plan.md). Validação: [test-guide.md](test-guide.md).

## Out of Scope

Formato trio e histórico entre sessões (fase 2).
