---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-07
related:
  - CV8.DS2.US4
---

# CV8.DS2.US4 — rodadas seguintes reequilibradas (0.40.0)

- **Entrega:** `app/reequilibrio.py` (nota efetiva, saldos, duplas anteriores), `sortear(..., anteriores=)`, tela da proposta com o ajuste; `tests/test_reequilibrio.py`.
- **Decisões do Navigator:** ordem de chegada em todas as rodadas; ímpar = último a chegar; cancelada fora do saldo.
- **Evidência:** pytest 533, e2e 77; validada pelo Navigator. Fecha a DS2.
