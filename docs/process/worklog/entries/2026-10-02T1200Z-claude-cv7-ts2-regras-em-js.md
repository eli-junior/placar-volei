---
date: 2026-10-02T12:00:00Z
author: Claude Code (Driver)
kind: milestone
related:
  - CV7.TS2
verification:
  - cd web && npm test && npm run check
  - uv run pytest
---

# Regras e projeção da partida em JS

## What changed

`web/src/lib/partida.js` reproduz em JS a projeção do estado e da linha do tempo e os comandos de ponto, desfazer, configurar e reiniciar. Fixtures geradas pelo backend real (`tests/paridade_fixtures.py`) alimentam um teste do JS; um teste do pytest falha se as fixtures ficarem para trás da regra em Python.

## Why it matters

É a base da quadra local do APK (CV7.US1): jogar sem servidor sem que a regra possa divergir da do backend sem aviso.

## Verification

129 testes do web (29 de paridade), 225 do backend e `svelte-check` limpo. O Navigator validou quebrando a regra nos dois lados: a paridade falhou como esperado.

## Follow-up

Próxima: CV7.US1, quadra local no celular. Se a TS3 mostrar que o WebView pausa com a tela apagada, o plano C é portar as regras também para Kotlin, estendendo as fixtures.
