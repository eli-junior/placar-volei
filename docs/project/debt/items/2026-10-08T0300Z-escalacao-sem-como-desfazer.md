---
id: debt-escalacao-sem-como-desfazer
status: Carried
kind: product
severity: low
source: CV8.DS3.US8
revisit_trigger: O operador escolher o parceiro errado na prática
closure_condition: Permitir desfazer a escolha enquanto a partida não foi chamada (ou cobrir na US7)
---

# Escalação sem Como Desfazer

## Description

Escolhido o parceiro do time incompleto, não há como corrigir sem cancelar a rodada. A US7 desfaz a última partida encerrada, não a escolha.

## Carrying Reason

Raro e antes de chamar a partida; custo de implementar agora superou o ganho.

## Notes

Decisão: `docs/project/decisions/records/2026-10-08T0300Z-escalacao-do-parceiro-do-incompleto.md`.
