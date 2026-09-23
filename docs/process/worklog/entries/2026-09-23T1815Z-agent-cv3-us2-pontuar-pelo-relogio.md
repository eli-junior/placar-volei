---
date: 2026-09-23T18:15:00Z
author: Claude Opus 5.5 (Driver)
kind: milestone
related:
  - CV3.DS1.US2
  - relogio-como-participante-com-controle-delegado
  - debt-fluxos-da-interface-sem-teste-de-ponta-a-ponta
  - debt-regra-de-vitoria-duplicada-no-relogio
verification:
  - uv run pytest (151 passed)
  - uv run ruff check . e ruff format --check . (passaram)
  - web: npm test (27 passed), npm run check (0 erros, 0 avisos), npm run build
  - Android: 18 testes, assembleDebug, lintDebug (0 erros)
  - Validação física no Galaxy Watch 8 (44 mm) em produção: vínculo, Eli (Relógio) e pontuação com controle delegado
---

# Pontuar pelo Relógio com Controle Delegado

## What changed

- O relógio marca pontos: placar Nós/Eles (ou iniciais), fila gravada no aparelho antes do retorno visual, envio em ordem, recibo durável e idempotente no servidor, descarte confirmado quando um lance é recusado.
- O plano mudou duas vezes. A revisão 2 (chave "Controlar pelo Relógio") foi implementada e, no teste físico, o Navigator redirecionou para a revisão 3: `eli` em qualquer caixa habilita, e o relógio vira o participante "Eli (Relógio)", com controle delegado.
- O teste físico revelou dois defeitos antigos de interface: a engrenagem sem ícone e a ausência do botão Passar controle. Ambos corrigidos.

## Why

A delegação reaproveita o modelo de controle que o site já tinha, e o participante próprio torna visível para a sala quem está pontuando.

## Follow-up

- US3: desfazer pelo relógio.
- US4: envio em segundo plano e reconciliação.
- Puxar `debt-banco-de-producao-sem-volume-persistente`: cada deploy de teste apagou as salas.
