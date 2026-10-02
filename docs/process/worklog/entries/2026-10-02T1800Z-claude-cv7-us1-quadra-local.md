---
date: 2026-10-02T18:00:00Z
author: Claude Code (Driver)
kind: milestone
related:
  - CV7.US1
verification:
  - cd web && npm test && npm run check && npm run test:e2e
  - uv run pytest
---

# Quadra local no celular

## What changed

O APK passa a ter uma quadra local, guardada no aparelho, para quando não há comunicação com o servidor. A tela inicial testa o `/health` pela rede nativa e decide: servidor no ar, só a online; sem ele, só a local. Uma quadra por APK; partida em andamento continua acessível se a conexão voltar.

## Why it matters

A pelada não depende do Mini PC nem da internet da quadra para marcar o placar. Na validação o servidor estava fora do ar (túnel no ar, backend fora: Cloudflare 530), exatamente o caso que o teste antigo daria como disponível.

## Verification

143 testes unitários, 51 e2e (11 da quadra local), `svelte-check` limpo e 225 do backend. O Navigator validou no Galaxy Z Fold. Na revisão apareceu e foi corrigido um bug que só ocorria sem recarregar o app (o resumo da tela inicial não via a partida terminar), e a folha do menu ⋯ cortada pela barra de navegação do Android.

## Follow-up

Não foi observado se a tela apaga sozinha com a sala aberta; decide o plano B da TS3. Próxima: CV7.TS3 (ponte Data Layer) e CV7.US2 (relógio na quadra local).
