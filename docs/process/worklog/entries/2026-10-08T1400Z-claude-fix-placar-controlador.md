---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-08
related:
  - CV8.DS5.US13
  - CV4.DS3.US1
---

# Fix: +1 cobrindo o placar do controlador (0.46.1)

- **Sintoma (Navigator, celular):** os botões +1 por cima do número do time de baixo, com o cartão "Rodada 1" abaixo.
- **Causa:** `.sala-container.operador` tem `height: 100dvh` e `overflow: hidden` (operar sem rolagem, CV4.DS3.US1). O cartão completo do `FilaEReis` (US13) entrou nessa moldura e o palco, com `min-height: 0`, encolheu.
- **Correção:** `compacto={modoImersivo || podeControlar}` em `SalaQuadra.svelte`: o controlador vê só a faixa.
- **Lição:** conteúdo novo na sala do controlador precisa caber na moldura fixa; o e2e da US13 só cobria o espectador e não pegou isso. Agora há um teste de geometria em 360×700.
