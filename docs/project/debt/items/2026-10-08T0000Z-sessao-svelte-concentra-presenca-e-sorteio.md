---
id: debt-sessao-svelte-concentra-presenca-e-sorteio
status: Carried
kind: maintainability
severity: low
source: CV8.DS2.US3
revisit_trigger: A DS3 mexer na mesma tela, ou `Sessao.svelte` passar de ~350 linhas
closure_condition: Dividir em componentes de presença, sorteio e encerramento
---

# Sessao.svelte Concentra Presença e Sorteio

## Description

O componente tem ~270 linhas e junta presença, cadastro rápido, sorteio e encerramento.

## Carrying Reason

Ainda legível; a divisão certa depende do que a DS3 pedir da tela.

## Updates

- 2026-10-08 (CV8.DS3.US5, 0.35.0): o componente subiu para 346 linhas (sincronia por WebSocket, vínculo e chamada). Os painéis já saíram (`PainelRodada`, `PainelConducao`); falta dividir presença, sorteio e a camada de conexão. Dividir antes de passar de ~350.

- 2026-10-08 (CV8.DS3.US6, 0.36.0): 347 linhas, praticamente no gatilho de ~350; dividir na próxima história que mexer na tela.

- 2026-10-08 (CV8.DS3.US8, 0.37.0): 362 linhas — passou do gatilho de ~350; dividir antes da próxima história que mexa na tela (US7/US9).

## Notes

Decisão: `docs/project/decisions/records/2026-10-08T0000Z-sorteio-da-primeira-rodada.md`.
