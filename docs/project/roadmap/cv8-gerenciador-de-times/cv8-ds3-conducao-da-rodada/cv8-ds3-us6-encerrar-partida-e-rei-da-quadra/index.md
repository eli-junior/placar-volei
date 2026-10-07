---
code: CV8.DS3.US6
level: User Story
status: Planned
status_reason: registrada em 2026-10-07, ainda não puxada
updated: 2026-10-07
---

# Encerrar partida e aplicar rei da quadra

## Intent

**Como** operador, **quero** confirmar o fim da partida, **para** o sistema registrar o placar e definir o próximo confronto.

## Acceptance / Done Condition

- **CA1:** Encerramento manual; registra placar final e vencedor.
- **CA2:** Perdedor → eliminados.
- **CA3:** Vencedor com 2 vitórias seguidas → rei; próximos 2 da fila entram.
- **CA4:** Vencedor com 1 vitória → enfrenta o próximo da fila.
- **CA5:** Fila vazia → transição para mata-mata (RN-03).

Regras: RN-02, RN-03, RN-09 (ver [regras-de-negocio.md](../../regras-de-negocio.md)).

## Validation Route

A definir no plano (Passo 2).

## Out of Scope

Formato trio e histórico entre sessões (fase 2).
