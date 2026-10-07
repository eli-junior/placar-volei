---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-07
related:
  - CV8.DS3.US9
---

# CV8.DS3.US9 — atrasado no meio da rodada (0.41.0)

- **Entrega:** `app/atrasados.py` + `POST /api/rodada/atrasado`; botão "Chegou atrasado" nos ausentes com a rodada em andamento; `tests/test_atrasado.py`.
- **Achado:** a escalação por `origem = 'atrasado'` e a exclusão de times ativos já existiam (US8), então "dois atrasados nunca se pareiam" saiu de graça e ficou coberto por teste.
- **Delegação:** o Navigator autorizou fazer as histórias de jogadores em sequência, com merge na `master` e validação em lote depois; sem perguntas intermediárias.
- **Evidência:** pytest 537, e2e 77 (um teste de mata-mata oscilou uma vez e passou isolado e na reexecução).
