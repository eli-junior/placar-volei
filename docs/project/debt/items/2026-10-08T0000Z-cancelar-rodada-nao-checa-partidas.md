---
id: debt-cancelar-rodada-nao-checa-partidas
status: Carried
kind: product
severity: low
source: CV8.DS2.US3
revisit_trigger: A DS3 criar partidas
closure_condition: Cancelar só enquanto não houver partida jogada; depois, só pelo fluxo de encerramento
---

# Cancelar Rodada Não Checa Partidas

## Description

Hoje a rodada em andamento só tem a fila, então cancelar é sempre seguro. Quando a DS3 criar partidas, cancelar uma rodada com partidas jogadas apagaria histórico.

## Carrying Reason

A regra depende de a partida existir; é fechamento obrigatório da DS3.

## Notes

Decisão: `docs/project/decisions/records/2026-10-08T0000Z-sorteio-da-primeira-rodada.md`.
