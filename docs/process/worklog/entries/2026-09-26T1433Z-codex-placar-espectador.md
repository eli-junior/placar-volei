---
date: 2026-09-26T14:33:30Z
author: Codex
kind: milestone
related:
  - CV4.DS2.US1
verification:
  - uv run pytest (185 passed)
  - npm test (39 passed)
  - npm run check (0 errors, 0 warnings)
  - npm run build
  - uv run ruff check app tests; uv run ruff format --check app tests
  - Navigator approval in browser on 2026-09-26
---

# Placar esportivo do espectador aprovado

## What changed

O placar retrô do espectador foi substituído por um painel esportivo que reserva a maior área para os pontos. A escala usa a largura e a altura disponíveis, trata três dígitos separadamente e mantém identificação e regras em uma faixa compacta. A inversão continua local e as atualizações recebem feedback curto com alternativa para movimento reduzido.

## Why it matters

Quem acompanha na mão, na mesa ou à distância identifica o resultado antes dos detalhes da sala. A representação visual também deixou de conhecer transporte, permissões e comandos, reduzindo o custo das próximas adaptações de tela.

## Verification

O backend passou em 185 testes. O frontend passou em 39 testes, na verificação Svelte sem advertências e no build de produção. Ruff foi aprovado. Uma sala real isolada foi inspecionada nos temas claro e escuro em 658 × 781 e 1066 × 600 CSS px, incluindo modo imersivo e inversão local. O Navigator pediu números maiores e aprovou a escala final.

## Follow-up

`CV4.DS2.US2` implementará fullscreen real e estabilidade da imersão. A matriz física completa de Fold, tablet, zoom e acessibilidade permanece em `CV4.DS3.TS1`. O nome interno `PlacarManual.svelte` pode ser atualizado quando as demais superfícies de placar forem migradas.
