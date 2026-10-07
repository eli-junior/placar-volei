---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-07
related:
  - CV8.DS4.US11
---

# CV8.DS4.US11 — mata-mata e campeão entregues (0.38.0)

- **Entrega:** fases `mata_mata` e `campeao` derivadas em `app/conducao.py`; `POST /api/rodada/iniciar-mata-mata`; encerrar a última partida fecha a rodada com o campeão e libera o sorteio; painel com desafiante, rivais, histórico por fase e cartão do campeão.
- **Decisões do Navigator:** início manual; partida única (ganhou ficou); rei da quadra vazia é o desafiante. Ver a decisão `mata-mata-e-campeao`.
- **Achados:** "mata-matacontra" (espaço perdido no Svelte) pego no e2e; dois e2e antigos esperavam **Chamar partida** no fim da fila.
- **Evidência:** pytest 517, `npm test`, `npm run check`, e2e 77 (axe incluído); validada pelo Navigator.
- **Dívida nova:** mata-mata/campeão sem como desfazer; agravadas `rodada.py` e `Sessao.svelte`.
