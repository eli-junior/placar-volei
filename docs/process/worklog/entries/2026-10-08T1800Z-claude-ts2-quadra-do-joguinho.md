---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-08
related:
  - CV8.DS7.TS2
  - quadra-da-rodada-renovada-pelo-servidor
---

# TS2: a quadra do joguinho não some no meio da rodada (0.46.3)

- **Problema:** o TTL de 1 h e o reinício apagavam a quadra de um joguinho em andamento, e o vínculo durável ficava apontando para o nada (QA P2/F3).
- **Entrega:** batimento que renova a quadra de rodada em andamento e reconciliação do vínculo em todo estado devolvido. Sem partida chamada o vínculo morto some; com ela, a saída é anular (US16).
- **Achado na revisão:** a reconciliação só no GET deixava a resposta de "anular" com a quadra morta; foi para dentro de `_estado`.
- **Ambiente:** `tests/test_sorteio.py` oscila nesta máquina (também no `master`) e um run derrubou o interpretador; fora ele, 485 passam, e 586 numa rodada completa.
- **Validação:** feita pelo Navigator em 2026-10-08.
