---
date: 2026-09-13T15:20:00Z
author: Claude (Driver)
kind: milestone
related:
  - CV1.DS1
verification:
  - decisão registrada e propagada para briefing, princípios, development guide e roadmap
---

# Stack do frontend decidida: Svelte 5

## What changed

O Navigator delegou a escolha da stack de frontend ao Driver, acrescentando um requisito que não estava na especificação original: a interface precisa ser bem trabalhada, com animação na interação.

Decisão: **Svelte 5**, com motion nativo (`transition:`, `animate:flip`, `crossfade`, `spring`, `tween`), sem biblioteca de animação adicional, compilado em build multi-estágio no Docker — Node no build, nunca no runtime do Mini PC.

Propagação da decisão:

- Registro de decisão passou de `Open` para `Decided`, com as alternativas avaliadas e o motivo de cada rejeição.
- `briefing.md`: premissa de frontend e de deploy atualizadas; restrição de "sem build step" substituída pelo limite real (Node fora do runtime); premissa de produto sobre a interface acrescentada.
- `principles.md`: novo princípio **O movimento conta o que mudou**, com o limite de legibilidade e `prefers-reduced-motion`.
- `development-guide.md`: comandos do frontend, `svelte-check` na verificação automatizada e nova camada de verificação de interface.
- `CV1.DS1` deixou de ter dependência aberta; `CV1.DS1.US2` saiu de bloqueada e ganhou a transição do placar no aceite; `CV1.DS4.US1` ganhou a transição de entrada na linha do tempo.

## Why it matters

O requisito de animação mudou a natureza da escolha. Sem ele, JS puro seria a resposta certa pela simplicidade de deploy. Com ele, animar entrada, saída e reordenação de listas ao vivo na mão vira exatamente o tipo de código que degrada, e o Svelte resolve isso no núcleo da linguagem.

Mais importante: animação deixou de ser polimento e virou critério de aceite. Story visível não fecha sem a transição correspondente.

## Verification

Nenhum código escrito. A decisão foi propagada por todos os documentos afetados e o roadmap não tem mais bloqueio para iniciar `CV1.DS1`.

## Follow-up

- Confirmar os comandos do frontend ao montar o esqueleto em `CV1.DS1.TS1`.
- Definir o Dockerfile multi-estágio junto com a TS1.
