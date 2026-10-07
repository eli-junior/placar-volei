---
code: CV8.DS3.US6
level: User Story
status: Validated
status_reason: validada pelo Navigator em 2026-10-07 (0.36.0); aguarda merge
updated: 2026-10-07
related:
  - ../../../../decisions/records/2026-10-08T0200Z-encerramento-lendo-o-placar.md
---

# Encerrar partida e aplicar rei da quadra

## Intent

**Como** operador, **quero** confirmar o fim da partida, **para** o sistema registrar o placar e definir o próximo confronto.

## Acceptance / Done Condition

- **CA1:** Encerramento manual (só de partida que terminou no placar); lê e registra o placar final e o vencedor.
- **CA2:** Perdedor → eliminados.
- **CA3:** Vencedor com 2 vitórias seguidas → rei; próximos 2 da fila entram.
- **CA4:** Vencedor com 1 vitória → enfrenta o próximo da fila.
- **CA5:** Fila vazia → fim da fase de fila: o painel avisa a transição para o mata-mata (RN-03) e bloqueia novas chamadas; jogar o mata-mata é a US11.

Regras: RN-02, RN-03, RN-09 (ver [regras-de-negocio.md](../../regras-de-negocio.md)).

## Entregue

`POST /api/rodada/encerrar-partida` lê o placar da quadra vinculada e grava o resultado; a fila anda (eliminados, vitórias seguidas, reis, entrada dos dois próximos); placar ao vivo e histórico no painel; fim da fila sinalizado. Plano: [plan.md](plan.md). Validação: [test-guide.md](test-guide.md).

## Validation Route

A definir no plano (Passo 2).

## Out of Scope

Formato trio e histórico entre sessões (fase 2).
