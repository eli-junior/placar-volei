---
date: 2026-09-27T23:00:00Z
author: Claude Code (Opus 5.5)
kind: milestone
related:
  - CV6.DS1
verification:
  - node --test (92 passed), svelte-check sem avisos, vite build
  - Playwright e2e (27 passed), incluindo axe nos dois temas
  - pytest (221 passed)
  - validação do Navigator em tablet e Fold, história a história, em 2026-09-27
---

# CV6.DS1: placar web mais legível e fácil de operar (0.21.0)

Foram cinco HUs, nascidas do feedback do Navigator depois de usar o placar em quadra. Cada uma teve branch própria, checkpoint de plano e validação manual antes do merge. A ordem foi US1, US2, US5 e US3; a US4 ficou coberta dentro da US1.

Pontos que valem lembrar:

- A validação mudou o desenho duas vezes. O status foi para o canto e passou a pulsar. "Você está no controle" deu lugar às regras da partida, porque para quem opera saber o alvo e a vantagem vale mais que ver a posse. A posse continua anunciada ao leitor de tela.
- No P/M/G, o primeiro desenho tratava o tamanho de antes como M e quase não mudava nada. O Navigator pediu que ele virasse o P. Os limites foram medidos pelos dígitos reais, para o G não cortar com 100 pontos.
- Tela em pé agora empilha as equipes. Lado a lado, os números ficavam presos à meia largura no Fold fechado.
- O axe falhava de forma intermitente também em `master`, porque media o contraste no meio dos fades. O teste agora espera as animações finitas.
- Follow-up: no tablet deitado o glifo fica acima do centro; centralizar liberaria altura para o G.
