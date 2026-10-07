---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-07
related:
  - CV8.DS1.US1
---

# CV8.DS1.US1 — cadastro de jogadores entregue (0.31.0)

- **Registro:** as 14 histórias do gerenciador de times entraram no roadmap como CV8 (5 DS, 14 US, regras em `regras-de-negocio.md`).
- **Entrega:** base de jogadores (nome, gênero; criar, editar, inativar/reativar) em `gerenciador.db`, volume `gerenciador-dados`, protegida pelo `OWNER_SECRET`; tela `/jogadores` oculta no APK.
- **Achado:** o banco efêmero e a ausência de volume impediam o CA3; resolvido com arquivo e volume próprios (decisão `base-de-jogadores-duravel-e-protegida`).
- **Evidência:** pytest 274, `npm test` 169, e2e 56 (axe incluído); validada pelo Navigator pela rota do `test-guide.md`.
- **Dívidas abertas:** segredo no `localStorage`, sem backup do volume, listagem sem paginação.
