---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-07
related:
  - CV8.DS4.US12
---

# CV8.DS4.US12 — sessão persistida e provada (0.39.0)

- **Entrega:** `synchronous=FULL` nas conexões do gerenciador; `tests/test_persistencia.py` (retomada após cada partida, mata-mata e campeão; registro completo para ranking; partidas preservadas ao cancelar a rodada e encerrar a sessão).
- **Achado:** o gerenciador já era durável; a história virou endurecer e provar o CA1. Sem schema nem rota novos.
- **Ressalva:** o teste do `synchronous` é só trava de regressão (o padrão do SQLite já costuma ser FULL).
- **Evidência:** pytest 521; validada pelo Navigator com reinício do contêiner.
- **Fecha a DS4** (US11 e US12 validadas). Dívidas carregadas: mata-mata sem como desfazer; concentração em `rodada.py` e `Sessao.svelte`.
