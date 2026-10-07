---
code: CV8.DS3.US8
level: User Story
status: Active
status_reason: puxada em 2026-10-07; Passo 2 (plano)
updated: 2026-10-07
---

# Escalar parceiro do time incompleto

## Intent

**Como** jogador ímpar ou atrasado, **quero** escolher meu parceiro quando for minha vez, **para** completar minha dupla.

## Acceptance / Done Condition

- **CA1:** Ao chegar a vez de um time incompleto, a partida só pode ser chamada após escolha do parceiro.
- **CA2:** Ímpar: lista "ainda não jogaram"; se vazia, lista de escalação.
- **CA3:** Atrasado: sempre lista de escalação.
- **CA4:** Lista calculada no momento, com exclusões e ordenação de RN-07.
- **CA5:** Escalado tem as duas participações contabilizadas no saldo.

Regras: RN-05, RN-06, RN-07 (ver [regras-de-negocio.md](../../regras-de-negocio.md)).

## Validation Route

A definir no plano (Passo 2).

## Out of Scope

Formato trio e histórico entre sessões (fase 2).
