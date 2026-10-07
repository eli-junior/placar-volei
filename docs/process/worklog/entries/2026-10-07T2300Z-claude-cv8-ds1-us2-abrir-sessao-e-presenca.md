---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-07
related:
  - CV8.DS1.US2
---

# CV8.DS1.US2 — sessão do dia, presença e ordem de chegada entregues (0.33.0)

- **Entrega:** sessão única (índice no banco), presença a partir da base, cadastro rápido, ordem de chegada 1..N com ↑/↓, aviso do mínimo de 4, encerrar sessão; tela `/sessao` oculta no APK. Fecha a DS1 (US1, US15, US2).
- **Achado de bug:** a renumeração da ordem por `UPDATE` com subconsulta empatava posições conforme a ordem de varredura do SQLite; trocada por renumeração linha a linha, com teste.
- **Achado de revisão:** reordenar com a tela desatualizada dava 422 sem recarregar a lista; agora recarrega (teste de navegador com dois estados).
- **Achado de acessibilidade:** `.contagem` da Home com contraste 4,03:1 quando há quadra ao vivo (anterior à história); virou dívida.
- **Evidência:** pytest 303, `npm test` 175, e2e 64 (axe incluído); validada pelo Navigator.
- **Dívidas abertas:** módulo comum do `gerenciador.db`, contraste do contador, sessões encerradas sem histórico.
