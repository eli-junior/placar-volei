---
id: debt-lista-baixa-fotos-uma-a-uma
status: Carried
kind: performance
severity: low
source: CV8.DS1.US15
revisit_trigger: Passar de algumas centenas de jogadores com foto
closure_condition: Paginação da lista ou miniaturas em um único pedido
---

# Lista Baixa as Fotos Uma a Uma

## Description

A tela faz um `fetch` por jogador com foto a cada carga da página (o `ETag` responde 304 depois).

## Carrying Reason

Dezenas de jogadores e imagens pequenas; mesmo gatilho da paginação já registrada.

## Notes

Decisão: `docs/project/decisions/records/2026-10-07T2100Z-nota-nome-completo-e-foto-do-jogador.md`.
