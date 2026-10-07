---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-07
related:
  - CV8.DS2.US3
---

# CV8.DS2.US3 — sorteio da primeira rodada entregue (0.34.0)

- **Entrega:** sorteio determinístico (`app/sorteio.py`: gênero por invariante, equilíbrio por trocas, ímpar = último a chegar, fila pela chegada), rodada com proposta/confirmar/resortear/descartar/cancelar (`app/rodada.py`, schema 4), presença travada durante a rodada e painel em `/sessao`. Inclui a extração do módulo comum (`app/gerenciador_db.py`), que quitou a dívida da US2.
- **Achado de ambiente:** o notebook do Navigator (i9-14900HX) corrompe o Python de forma intermitente em laços longos; custou cerca de 1 h de investigação até provar que não era o código (um script sem relação falhou igual). Regra prática: reexecutar 3–5 vezes antes de depurar um erro de interpretador.
- **Achado de teste:** com cada homem obrigado a formar dupla com uma mulher, o melhor equilíbrio do exemplo do guia é 100/125/130/140, não 120/125/125/125 da serpentina livre; o teste confere contra força bruta.
- **Evidência:** pytest 519 (203 novos), `npm test` 179, e2e 68 (axe incluído); validada pelo Navigator.
- **Dívidas abertas:** rotas da rodada na `sessao.py`, `Sessao.svelte` grande, sorteio heurístico sem prova de ótimo, cancelar rodada sem checar partidas.
