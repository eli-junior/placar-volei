---
id: debt-rotas-da-rodada-na-sessao-py
status: Closed
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

## Updates

- 2026-10-08 (CV8.DS3.US5, 0.35.0): agravada — as rotas da rodada agora estão em dois arquivos (`sessao.py`, 359 linhas, e `ponte.py` com `/api/rodada/chamar-partida`). A próxima história da DS3 deve reunir tudo num módulo de rodada.

## Updates

- 2026-10-08 (CV8.DS3.US6, 0.36.0): **quitada** — as rotas e operações da rodada foram reunidas em `app/rodada_rotas.py`; `sessao.py` voltou a cuidar só de sessão e presença.

## Notes

Decisão: `docs/project/decisions/records/2026-10-08T0000Z-sorteio-da-primeira-rodada.md`.
