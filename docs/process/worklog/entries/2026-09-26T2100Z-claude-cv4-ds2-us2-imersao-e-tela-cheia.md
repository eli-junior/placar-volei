---
date: 2026-09-26T21:00:00Z
author: Claude Code (Opus 5.5)
kind: milestone
related:
  - CV4.DS2.US2
verification:
  - uv run pytest (191 passed)
  - npm test (54 passed)
  - npm run check (0 errors, 0 warnings)
  - npm run build
  - Playwright headless em 360×640, 390×780 e 1066×600 (scripts temporários)
  - Navigator validou no Fold em 2026-09-26
---

# Imersão estável e tela cheia real

## What changed

O espectador ganhou o botão **Tela cheia**, que pede fullscreen no próprio toque e só mostra "Sair" quando o navegador confirma. Recusa ou falta de suporte vira aviso, e o placar continua na aba. Os controles passaram a sobrepor o palco: revelar ou esconder não move os pontos, e o toque que revela não aciona o botão que surge sob o dedo.

## Why it matters

Fecha a CV4.DS2: o placar pode ser deixado no cavalete, legível e sem barras do navegador quando o aparelho permite, sem estados mentirosos.

## Follow-up

Tablet na matriz física da CV4.DS3.TS1; cenários de navegador no runner da TS1; sobreposição em telas estreitas revisitada na CV4.DS3.US2. As branches das próximas histórias já estão abertas com Checkpoint 1 apresentado.
