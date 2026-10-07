---
id: debt-difusao-do-estado-completo
status: Carried
kind: performance
severity: low
source: CV8.DS3.US5
revisit_trigger: Passar de algumas centenas de jogadores, ou lentidão na difusão
closure_condition: Enviar só a diferença (ou só a parte que mudou) pelo WebSocket
---

# Difusão do Estado Completo

## Description

Cada mudança publica o estado completo da sessão (presentes, ausentes, rodada, condução) a todos os aparelhos.

## Carrying Reason

Dezenas de jogadores e poucos aparelhos; mesmo gatilho da paginação já registrada.

## Notes

Decisão: `docs/project/decisions/records/2026-10-08T0100Z-ponte-com-o-placar-e-sincronia.md`.
