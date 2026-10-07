---
id: debt-rotas-da-rodada-na-sessao-py
status: Carried
kind: architecture
severity: low
source: CV8.DS2.US3
revisit_trigger: A DS3 adicionar partidas e placar, ou `app/sessao.py` passar de ~450 linhas
closure_condition: Rotas da rodada em módulo próprio, sem import circular com a sessão
---

# Rotas da Rodada Moram na sessao.py

## Description

As rotas `/api/rodada/*` estão em `app/sessao.py` para evitar import circular (a rodada sai junto do estado da sessão); o arquivo já tem ~335 linhas.

## Carrying Reason

Mover agora seria antecipar a forma da DS3.

## Notes

Decisão: `docs/project/decisions/records/2026-10-08T0000Z-sorteio-da-primeira-rodada.md`.
