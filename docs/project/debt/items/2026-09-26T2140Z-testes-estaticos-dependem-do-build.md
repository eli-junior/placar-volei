---
id: debt-testes-estaticos-dependem-do-build
status: Carried
kind: validation
severity: low
source: CV4.DS3.TS1 (primeira execução do CI)
revisit_trigger: Qualquer falha do pytest ligada a `app/static`, ou reorganização das etapas do CI
closure_condition: Testes de rota estática usam um diretório estático próprio (temporário) e passam sem build do frontend
---

# Testes de Rota Estática Dependem do Build do Frontend

## Description

Cinco casos de `tests/test_review_regressions.py::test_static_nao_escapa_da_raiz` só passam se `app/static` existir, isto é, depois de `npm run build`. Num checkout limpo, `uv run pytest` falha nesses casos sem que nada esteja errado no código.

## Carrying Reason

O CI já gera o build antes do pytest, que é a ordem real de execução do produto. Corrigir o teste é pequeno, mas fora do escopo da história que só consolidava a regressão.

## Proposed Fix

Apontar o diretório estático para um `tmp_path` com um `index.html` mínimo durante esses testes.
