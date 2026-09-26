---
date: 2026-09-27T01:00:00Z
author: Claude Code (Opus 5.5)
kind: milestone
related:
  - CV4.DS3.TS1
  - CV4
verification:
  - npm run test:e2e (24 passed, três execuções locais)
  - GitHub Actions CI run #3 verde (a9b2354)
  - uv run pytest (191 passed); npm test (66 passed); svelte-check limpo
  - Navigator aprovou a matriz física V6 em 2026-09-26
---

# Regressão consolidada e fechamento do CV4

## What changed

Os cenários de navegador verificados à mão nas últimas histórias viraram 24 testes Playwright versionados, com axe nos dois temas, rodando localmente e num CI novo no GitHub Actions. O teste de requisições externas encontrou o Google Fonts ainda carregado pelo `index.html`; saiu.

## Why it matters

Fecha o CV4 (painel esportivo): Home, placar do espectador, temas, tela cheia, operação, superfícies auxiliares e regressão. A partir daqui, uma quebra de layout, foco, permissão ou contraste falha no CI antes de chegar ao Mini PC.

## Follow-up

Parte do relógio da dívida de testes de ponta a ponta na `CV3.DS1.TS1`; testes estáticos independentes do build; atualizar as actions quando houver versões para Node 24.
