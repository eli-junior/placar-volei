---
code: CV1.DS4
level: Delivery Story
status: Planned
status_reason: depende do event store entregue em DS1.TS1
updated: 2026-09-13
related:
  - 2026-09-13T1400Z-log-de-eventos-como-fonte-da-verdade
---

# CV1.DS4 — Auditoria visível da partida

## Intent

A discussão sobre "quem fez esse ponto" acaba com uma consulta na tela, não com a memória de quem fala mais alto.

## Scope

Botão de linha do tempo na tela do placar e visualização cronológica dos eventos da partida corrente.

## Acceptance / Done Condition

A capacidade emergente é **transparência do placar**: qualquer participante reconstitui como o placar chegou ao número atual, incluindo correções e mudanças de regra.

## Validation Route

Partida com pontos, desfazimentos e mudança de regra; conferir se a linha do tempo conta a história completa e correta.

## Out of Scope

Consulta a partidas arquivadas, exportação, filtros e busca.
