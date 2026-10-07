---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-07
related:
  - CV8.DS3.US6
---

# CV8.DS3.US6 — encerrar partida e rei da quadra entregues (0.36.0)

- **Entrega:** `POST /api/rodada/encerrar-partida` (lê o placar da quadra vinculada, exige partida terminada e a mesma da chamada, grava placar e vencedor); a fila anda pela derivação da US5 (eliminados, vitórias seguidas, reis, os dois próximos); placar ao vivo e histórico no painel; fim da fila sinalizado; cancelar com partidas pede confirmação reforçada. Rotas da rodada reunidas em `app/rodada_rotas.py`. Quita duas dívidas.
- **Achado de ambiente (de novo):** a instabilidade da CPU do notebook voltou a derrubar o `test_sorteio.py` (o teste que mais usa CPU) de forma intermitente; o teste de composições de gênero foi enxugado (169 → todas até 12 jogadores mais quatro maiores), o que baixou o total do backend para 483. Sem relação com o código da história.
- **Achado de teste:** o cookie do operador é `Secure`, então o Playwright (`page.request`) não o envia por http; os pontos no e2e saem do `fetch` da própria página.
- **Efeito prático:** com número ímpar de jogadores o time incompleto acaba entrando em quadra e bloqueia **Chamar partida** até a US8 (parceiro do incompleto).
- **Evidência:** pytest 483 (15 novos), `npm test` 182, e2e 75 (axe incluído); validada pelo Navigator.
- **Dívidas abertas:** `ponte.py` concentra três responsabilidades, o aviso do placar recalcula o estado completo, o erro de encerrar aparece no bloco da quadra.
