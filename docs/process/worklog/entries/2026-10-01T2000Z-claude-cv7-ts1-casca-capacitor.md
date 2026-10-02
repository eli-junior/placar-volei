---
date: 2026-10-01T20:00:00Z
author: Claude Code (Driver)
kind: milestone
related:
  - CV7.TS1
verification:
  - cd web && npm test && npm run check && npx vite build --mode e2e && npx playwright test casca
  - uv run pytest
---

# Casca Capacitor do APK Android

## What changed

O APK `br.com.placarvolei` embarca a web e abre a quadra online do servidor fixo do build, depois de testar `/health`. Ícone da bola do `favicon.svg`. `scripts/build-apk.sh` gera o APK de debug.

## Why it matters

Dá ao celular um app instalável sem reescrever a interface e prepara a quadra local e a ponte com o relógio (CV7).

## Verification

100 testes unitários, `svelte-check` limpo, 4 e2e da casca (axe nos dois temas) e 224 do backend passaram. O Navigator validou o APK no Galaxy Z Fold: abre a quadra dentro do app, e o botão online respeita a conexão.

## Follow-up

O `adb install` sem `--user 0` duplicou o app no perfil Dual App da Samsung. O teste de conexão só detecta rede (`debt-apk-teste-de-conexao-so-detecta-rede`). Release sem assinatura (`debt-apk-release-sem-assinatura`). Próxima: CV7.TS2, regras e projeção em JS.
