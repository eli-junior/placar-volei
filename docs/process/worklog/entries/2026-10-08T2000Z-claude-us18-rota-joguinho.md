---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-08
related:
  - CV8.DS7.US18
  - docs/qa/2026-10-08-auditoria-producao.md
---

# US18: a tela do Joguinho é `/joguinho` e endereço errado diz que não existe (0.46.5)

- **Problema:** o botão empurrava `/sessao` e qualquer caminho desconhecido (inclusive `/joguinho`) caía na home sem aviso, o que escondeu o erro de digitação no QA (P3/P4).
- **Entrega:** tabela de rotas pura (`web/src/lib/rotas.js`), página "Página não encontrada", `/sessao` redirecionando por `replaceState` (com `?query` e `#hash`) e APK sem `/joguinho`. O servidor continua devolvendo o SPA.
- **Detalhe da revisão:** a checagem de "ainda na sala" passou a usar a mesma tabela, para `/quadra/<id>/` com barra final abrir a sala.
- **Validação:** feita pelo Navigator em 2026-10-08.
