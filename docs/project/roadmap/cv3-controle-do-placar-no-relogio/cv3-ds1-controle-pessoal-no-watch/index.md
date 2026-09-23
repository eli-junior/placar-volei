---
code: CV3.DS1
level: Delivery Story
status: Active
status_reason: US1 (0.7.0), US2 (0.8.0) e US3 (0.9.0) entregues; próxima: US5 (retomar ou trocar de quadra), depois US4
updated: 2026-09-23
---

# CV3.DS1 — Controle pessoal no Galaxy Watch

## Intent
Preparar a sala no telefone e operar pelo relógio durante o jogo.

## Scope
- US1: vincular e autorizar o relógio na sala.
- US2: acompanhar o placar e marcar para cada equipe.
- US3: desfazer o último ponto visto, inclusive com fila local.
- US4: registrar offline e reconciliar sem duplicação.
- US5: um vínculo por vez — retomar a quadra ou trocar, revogando a anterior. Entra antes da US4.

## Acceptance / Done Condition
As cinco HUs são validadas no Watch e em clientes web simultâneos, incluindo telefone bloqueado, perda de conexão, reinício do app e conflito de controle.

## Validation Route
Ver [plano](plan.md), com sequência de entrega, decisões propostas e roteiro integrado.

## Out of Scope
Loja, outros usuários/relógios, gestos e botões físicos, criação/configuração/reinício de partida no relógio e operação offline do servidor inteiro.
