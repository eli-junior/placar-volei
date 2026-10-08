---
id:
status: Carried
kind: design
severity: low
source: CV8 (ajustes do joguinho, 0.46.0)
revisit_trigger: próxima limpeza da API ou uma tela que precise cadastrar e marcar presente de uma vez
closure_condition: endpoint e testes removidos, ou reaproveitado por uma tela
---

# Endpoint `/presencas/rapido` sem uso na tela

## Description

A tela não chama mais o cadastro rápido; o endpoint e seus testes continuam.

## Carrying Reason

Remover API sai do escopo pedido pelo Navigator.

## Impact

Código e testes sem uso para manter.
