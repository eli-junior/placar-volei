---
code: CV8.DS3.US5
level: User Story
status: Validated
status_reason: validada pelo Navigator em 2026-10-07 (0.35.0); aguarda merge
updated: 2026-10-07
related:
  - ../../../../decisions/records/2026-10-08T0100Z-ponte-com-o-placar-e-sincronia.md
---

# Visualizar e conduzir a fila

## Intent

**Como** operador, **quero** ver quem está em quadra, a fila, os reis e os eliminados, **para** conduzir a rodada.

## Acceptance / Done Condition

- **CA1:** Painel com: partida atual, fila ordenada, reis (com ordem), eliminados.
- **CA2:** Botão "Chamar partida" carrega as duplas (e o alvo da rodada) no placar da quadra vinculada, zerado (RN-09); recusado se a quadra tem partida em andamento com pontos.
- **CA3:** Estado sincronizado em todos os aparelhos abertos na tela da sessão, sem atualizar.

Regras: RN-02, RN-12 (ver [regras-de-negocio.md](../../regras-de-negocio.md)).

## Entregue

Vínculo da sessão com a quadra do placar, Chamar partida (admin da quadra, recusa com pontos, nomes curtos), painel da condução (quadra, partida, fila, reis, eliminados) e sincronia por WebSocket. Reis e eliminados só enchem com os resultados da US6. Plano: [plan.md](plan.md). Validação: [test-guide.md](test-guide.md).

## Validation Route

A definir no plano (Passo 2).

## Out of Scope

Formato trio e histórico entre sessões (fase 2).
