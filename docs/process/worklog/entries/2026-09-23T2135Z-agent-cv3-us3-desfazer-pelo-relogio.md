---
date: 2026-09-23T21:35:00Z
author: Claude Opus 5.5 (Driver)
kind: milestone
related:
  - CV3.DS1.US3
  - CV3.DS1.US5
  - desfazer-do-relogio-com-alvo-explicito-e-registro-antes-do-envio
  - debt-regra-de-vitoria-duplicada-no-relogio
verification:
  - uv run pytest (166 passed)
  - uv run ruff check . e ruff format --check . (passaram)
  - web: npm test (27 passed), npm run check (0 erros, 0 avisos), npm run build
  - Android: 26 testes, assembleDebug, lintDebug (0 erros)
  - Validação física no Galaxy Watch 8 em produção, na branch da HU, incluindo os ajustes de tela
---

# Desfazer pelo Relógio

## What changed

- O relógio desfaz o último ponto que mostra, inclusive com o ponto ainda na fila, sem rede. O servidor só desfaz se o alvo ainda for o último ponto ativo.
- No teste físico, o Navigator redesenhou a tela: faixa inferior inteira para o desfazer (some sem o controle, o que resolveu o aviso escondido atrás dos números) e bolinha colorida de conexão com o número de pendentes.
- A tela de vínculo perdeu o campo de servidor.
- Dois pedidos do Navigator viraram a US5: escolher entre retomar a quadra ou parear outra ao abrir o app, com o relógio vinculado a uma quadra por vez. A US5 entra antes da US4.

## Why

O relógio atrasado não pode corrigir um ponto que não viu. E a quadra travada precisa de saída pelo próprio relógio.

## Follow-up

- US5: retomar ou trocar de quadra.
- US4: envio em segundo plano e reconciliação, respeitando o alvo do desfazer.
- Separar os testes do relógio com um `conftest` comum quando a US4 aumentar o `test_watch_comandos.py`.
