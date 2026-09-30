---
date: 2026-09-30T12:00:00Z
author: Claude Code (Driver)
kind: milestone
related:
  - CV6.DS1.US9
verification:
  - cd web && npm test && npm run check && npm run test:e2e
  - uv run pytest
---

# Destaque do último ponto e sequência de pontos na web

## What changed

O placar web destaca a equipe do último ponto (número maior e aceso, pulso por ponto) e mostra, sob o placar, uma faixa de bolinhas com a sequência da partida atual. Vale para operador e espectador.

## Why it matters

Na quadra, quem olha de longe não precisa comparar números nem abrir a linha do tempo para saber quem pontuou e como a partida andou.

## Verification

97 testes unitários, 36 e2e (incluindo o novo com dois clientes) e 224 do backend passaram; Navigator validou no celular.

## Follow-up

No espectador, a faixa ganhou uma linha própria no grid para o placar não se mover ao revelar controles. Tocar numa bolinha para abrir o lance ficou fora do escopo.
