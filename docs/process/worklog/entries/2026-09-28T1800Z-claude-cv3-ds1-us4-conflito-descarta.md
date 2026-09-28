---
related:
  - CV3.DS1.US4
  - 2026-09-28T1800Z-conflito-do-relogio-descarta-com-aviso
---

# CV3.DS1.US4 — conflito da fila do relógio descarta com aviso (0.24.0)

O plano original levava a revisão do conflito para o telefone (API de pendência, painel, reaplicar ou descartar). No Checkpoint 1 o Navigator observou que perder o controle não é conflito: quem assumiu já marca o placar real. Escolheu a opção simples: a fila é descartada, com aviso de 3 s, e o relógio converge para o servidor. A US encolheu para uma mudança só no relógio; a tela de lances retidos saiu. Com ela fecham a CV3.DS1 e a CV3. Evidência: 56 testes do relógio, lint sem avisos novos, validação física do Navigator.
