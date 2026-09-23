---
date: 2026-09-23T23:35:00Z
author: Claude Opus 5.5 (Driver)
kind: milestone
related:
  - CV3.DS1.US5
  - CV3.DS1.US4
  - um-vinculo-por-vez-troca-na-aprovacao
  - debt-fluxos-da-interface-sem-teste-de-ponta-a-ponta
verification:
  - uv run pytest (178 passed)
  - uv run ruff check . e ruff format --check . (passaram)
  - web: npm test (27 passed), npm run check (0 erros, 0 avisos), npm run build
  - Android: 33 testes, assembleDebug, lintDebug (0 erros)
  - Dois testes físicos no Galaxy Watch 8 em produção, na branch da HU, aprovados pelo Navigator
---

# Um Vínculo por Vez no Relógio

## What changed

- O relógio fica em uma quadra por vez. Ao reabrir o app, ele oferece **Retornar** (com o nome da quadra) ou **Parear outra quadra**. O código novo informa o vínculo que substitui, e o antigo só cai na aprovação: o relógio sai da quadra anterior e o controle volta ao dono.
- Desistir cancela o código no servidor. Lances pendentes da quadra antiga são avisados antes e só descartados na aprovação.
- Os dois testes físicos redesenharam as telas de vínculo no padrão do placar: conteúdo no centro, ação na faixa inferior, bola quicando no lugar das mensagens, e nada de botão piscando enquanto o relógio consulta o servidor.

## Why

A quadra travada ou o vínculo ruim precisavam de saída pelo próprio relógio, sem o telefone revogar antes. E um código aprovado em outra quadra deixava o relógio em duas quadras ao mesmo tempo.

## Observação

No primeiro teste, o "Passar controle" não apareceu na primeira quadra (o relógio foi promovido, revogado e promovido de novo, sem transferência). O site não mudou nesta HU, o servidor entrega o estado certo e o defeito não se repetiu no segundo teste. Fica registrado sem causa.

## Follow-up

- US4: envio em segundo plano e reconciliação. Começar separando o `WatchModel` e criando o `conftest` comum dos testes do relógio.
