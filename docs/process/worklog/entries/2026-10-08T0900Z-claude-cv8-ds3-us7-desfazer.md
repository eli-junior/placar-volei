---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-07
related:
  - CV8.DS3.US7
---

# CV8.DS3.US7 — desfazer a última partida (0.43.0)

- **Entrega:** `app/desfazer.py`, `POST /api/rodada/desfazer-partida`, `rodadas.desfeito` (schema 8), botão com confirmação no painel e no cartão do campeão; `tests/test_desfazer_partida.py`.
- **Decisão do Driver:** como o estado é derivado das partidas, desfazer = apagar a última encerrada (e a chamada pendente); o placar é rechamado depois. Um nível via `desfeito`, zerado ao encerrar a próxima partida. Reabre a rodada se a última deu o campeão.
- **Incidente evitado:** o primeiro arquivo de testes foi gravado sobre o `tests/test_desfazer.py` existente (desfazer de pontos); restaurado do git antes de qualquer commit e movido para `test_desfazer_partida.py`.
- **Fecha a DS3** (US5 a US10 todas implementadas; validação do Navigator em lote).
