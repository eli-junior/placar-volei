---
id: debt-aviso-do-placar-recalcula-o-estado-completo
status: Carried
kind: performance
severity: low
source: CV8.DS3.US6
revisit_trigger: Vários placares ou muitos aparelhos conectados ao mesmo tempo
closure_condition: Publicar só o pedaço do placar, ou limitar a frequência do aviso
---

# Aviso do Placar Recalcula o Estado Completo

## Description

Cada evento da quadra vinculada recalcula e publica o estado completo da sessão quando há aparelho no gerenciador.

## Carrying Reason

Um placar e poucos aparelhos: custo irrelevante.

## Notes

Decisão: `docs/project/decisions/records/2026-10-08T0200Z-encerramento-lendo-o-placar.md`.
