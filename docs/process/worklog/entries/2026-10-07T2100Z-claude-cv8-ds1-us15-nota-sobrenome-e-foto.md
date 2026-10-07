---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-07
related:
  - CV8.DS1.US15
---

# CV8.DS1.US15 — nota, nome completo e foto entregues (0.32.0)

- **Entrega:** nota 1–100 (padrão 60), nome com ao menos 2 palavras e foto opcional tirada na hora, em BLOB no `gerenciador.db`; migração 1→2 preserva a base da 0.31.0 com nota 60.
- **Antes:** o pedido do Navigator virou RN-13 (ordem de chegada na 1ª rodada), RN-14 (nota e saldo, fórmula ±15) e RN-15 (fila de chegada editável); a TS1 de backup e a decisão "SQLite com Postgres adiado" foram registradas.
- **Achado:** `<input type=number>` vazio chega como `null` no Svelte; o formulário usa `novalidate` para mostrar as mensagens do servidor.
- **Evidência:** pytest 290, `npm test` 172, e2e 58 (axe incluído); validada pelo Navigator.
- **Dívidas abertas:** corpo da foto sem teto na leitura, fotos sem exclusão em massa, lista baixa fotos uma a uma.
