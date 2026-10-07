---
code: CV8.DS3.US8
level: User Story
status: Validated
status_reason: validada pelo Navigator em 2026-10-07 (0.37.0); aguarda merge
updated: 2026-10-07
related:
  - ../../../../decisions/records/2026-10-08T0300Z-escalacao-do-parceiro-do-incompleto.md
---

# Escalar parceiro do time incompleto

## Intent

**Como** jogador ímpar ou atrasado, **quero** escolher meu parceiro quando for minha vez, **para** completar minha dupla.

## Acceptance / Done Condition

- **CA1:** Ao chegar a vez de um time incompleto, a partida só pode ser chamada após escolha do parceiro.
- **CA2:** Ímpar: lista "ainda não jogaram"; se vazia, lista de escalação (na prática sempre a de escalação).
- **CA3:** Atrasado: sempre lista de escalação.
- **CA4:** Lista calculada no momento, com exclusões e ordenação de RN-07.
- **CA5:** Escalado tem as duas participações contabilizadas no saldo; o painel mostra o "Saldo da rodada".

Regras: RN-05, RN-06, RN-07 (ver [regras-de-negocio.md](../../regras-de-negocio.md)).

## Entregue

Lista de escalação calculada no servidor (eliminados fora de time ativo, gênero, ordem de chegada), escolha validada na transação, escalado em dois times, saldo da rodada e `times.origem` pronta para a US9. Plano: [plan.md](plan.md). Validação: [test-guide.md](test-guide.md).

## Validation Route

A definir no plano (Passo 2).

## Out of Scope

Formato trio e histórico entre sessões (fase 2).
