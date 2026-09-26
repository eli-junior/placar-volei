---
date: 2026-09-26T13:41:00Z
author: Codex
kind: milestone
related:
  - CV4.DS1.US1
verification:
  - uv run pytest (185 passed)
  - npm test (31 passed)
  - npm run check (0 errors, 0 warnings)
  - npm run build
  - Navigator approval in browser on 2026-09-26
---

# Home esportiva aprovada

## What changed

A Home passou a iniciar por entrada via código, mantém criação em uma aba e usa o espaço disponível em computador, Fold e larguras estreitas. Partidas ativas usam três colunas: informações pequenas, placar Teko dominante no centro e ação **Abrir** ocupando a coluna final. Os dois temas preservam os tokens locais.

Falhas ao entrar por um card agora permanecem na aba Acompanhar, com o código preenchido, mensagem junto ao formulário e foco no apelido que precisa ser corrigido.

## Why it matters

A pessoa identifica uma partida e seu resultado com menos varredura visual. A correção também fecha o caso em que uma recusa por apelido duplicado parecia um botão sem resposta.

## Verification

O backend passou em 185 testes. O frontend passou em 31 testes, na verificação Svelte sem advertências e no build de produção. A composição foi inspecionada com partida real isolada em 658, 904 e 1440 px. O Navigator refinou proporções, tipografia e card ao vivo no navegador e aprovou a versão final.

## Follow-up

CV4.DS2 continua planejada para placar de acompanhamento, responsividade durante a partida e imersão. Esta entrega não altera permissões, eventos, operação do placar ou Wear OS.
