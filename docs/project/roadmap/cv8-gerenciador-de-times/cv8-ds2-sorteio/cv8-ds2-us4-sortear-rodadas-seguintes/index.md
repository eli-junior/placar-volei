---
code: CV8.DS2.US4
level: User Story
status: Validated
status_reason: puxada em 2026-10-07; validada pelo Navigator (0.40.0)
updated: 2026-10-07
---

# Sortear rodadas seguintes com reequilíbrio

## Intent

**Como** operador, **quero** que as próximas rodadas sejam balanceadas pelo saldo, **para** jogos mais equilibrados.

## Acceptance / Done Condition

- **CA1:** Disponível só após a rodada anterior ter campeão.
- **CA2:** Aplica RN-10 sobre os presentes atuais.
- **CA3:** Jogador novo (sem saldo) entra com saldo 0. A ordem de chegada **não** vale da segunda rodada em diante (RN-13). O saldo da sessão ajusta a nota (RN-14); a fórmula e os limites estão na RN-14 (ajuste de até ±15 por saldo médio por partida, só na sessão; a nota cadastrada não muda).
- **CA4:** Exibe resultado para confirmar ou resortear.

Regras: RN-01, RN-05, RN-10 (ver [regras-de-negocio.md](../../regras-de-negocio.md)).

## Validation Route

A definir no plano (Passo 2).

## Out of Scope

Formato trio e histórico entre sessões (fase 2).
