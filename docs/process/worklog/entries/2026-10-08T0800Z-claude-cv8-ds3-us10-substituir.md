---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-07
related:
  - CV8.DS3.US10
---

# CV8.DS3.US10 — substituir jogador que saiu (0.42.0)

- **Entrega:** `app/substituicao.py` + `POST /api/rodada/substituir`; formulário no painel da condução; `tests/test_substituicao.py`. Extraída `elegiveis()` de `_escalacao` para ser reaproveitada.
- **Decisões do Driver (Navigator pediu para não perguntar):** substituição bloqueada com partida chamada; quem sai some da presença (reversível); o substituto vindo dos eliminados entra como "escalado".
- **Dívida:** saldo do substituto herda as partidas anteriores do time (ver item de dívida).
- **Evidência:** pytest 541; E2E 77 (o teste axe da sessão oscila de forma intermitente e passa isolado). Achado no caminho: chave duplicada no `{#each}` da lista "quem saiu" no mata-mata (o desafiante está em quadra e entre os reis); corrigido e coberto por teste.
