---
id: debt-contraste-do-contador-de-quadras-na-home
status: Carried
kind: accessibility
severity: low
source: CV8.DS1.US2
revisit_trigger: Qualquer ajuste visual na Home, ou nova rodada de acessibilidade
closure_condition: `.contagem` com contraste mínimo de 4,5:1 e o axe da Home rodando com quadras ao vivo
---

# Contraste do Contador de Quadras na Home

## Description

O `.contagem` da lista de quadras ao vivo na Home tem texto `#94a3b8` sobre `#334155` (4,03:1, abaixo de 4,5:1). O axe só o acusa quando já existe quadra ao vivo; o teste de acessibilidade da Home roda antes de haver quadras e por isso passa.

## Carrying Reason

Defeito anterior à CV8, achado durante a US2; o ajuste é uma cor de texto.

## Notes

Decisão: `docs/project/decisions/records/2026-10-07T2300Z-sessao-unica-presenca-e-ordem-de-chegada.md`.
