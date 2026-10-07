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

## Notes

Decisão: `docs/project/decisions/records/2026-10-08T0000Z-sorteio-da-primeira-rodada.md`.
