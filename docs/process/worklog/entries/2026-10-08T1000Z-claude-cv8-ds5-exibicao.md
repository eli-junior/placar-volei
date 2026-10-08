---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-07
related:
  - CV8.DS5.US13
  - CV8.DS5.US14
---

# CV8.DS5 — exibição (0.44.0)

- **US13:** `app/exibicao.py` projeta o estado da sessão na parte pública; `sincronia.publicar` envia `EXIBICAO_ATUALIZADA` à sala da quadra vinculada e o `ESTADO_INICIAL` leva `exibicao`. Web: `FilaEReis.svelte` (faixa no modo imersivo, cartão fora dele). Testes: `tests/test_exibicao.py` e um E2E com espectador.
- **US14:** já estava entregue (chamada de partida grava `equipe_a`/`jogadores_a`; o Wear já os exibe). Fechada só com documentação e rota de validação no relógio físico.
- **Decisão do Driver:** a faixa compacta no modo imersivo (a tela é de altura fixa), em vez de rolagem.
- **Dívida:** desvincular a quadra não limpa a exibição da sala antiga.
- **Armadilha:** `npx playwright test` direto usa o build antigo; só `npm run test:e2e` (ou `npm run build`) o atualiza.
- **Fecha a DS5 e a CV8** (validação do Navigator em lote).
