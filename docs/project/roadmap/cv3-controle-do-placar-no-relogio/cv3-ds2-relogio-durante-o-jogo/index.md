---
code: CV3.DS2
level: Delivery Story
status: Active
status_reason: US1 (0.10.1) e US2 (0.11.0) entregues; US3 (nova partida rápida) em planejamento
updated: 2026-09-26
related:
  - CV3.DS1
  - tela-acesa-no-placar-do-relogio
  - batimento-no-relogio-por-measureclient
---

# CV3.DS2 — Relógio durante o jogo e o treino

## Intent
O placar do relógio tem de conviver com a partida real: ficar pronto para o toque sem acordar a tela, e rodar junto com o treino que o Eli grava no Samsung Health.

## Scope
- US1: tela sempre acesa enquanto o placar está visível.
- US2: frequência cardíaca no placar enquanto o Samsung Health grava o treino.
- US3: nova partida rápida pelo relógio, nos mesmos moldes, com um toque.

## Acceptance / Done Condition
Uma partida inteira no Galaxy Watch 8, com treino de Vôlei ativo no Samsung Health, sem a tela apagar no placar e sem interromper a gravação do treino.

## Out of Scope
Envio em segundo plano (CV3.DS1.US4), modo ambiente, dados do treino no site ou no servidor.

## Notes
- [US1 — Tela acesa no placar](cv3-ds2-us1-tela-acesa-no-placar/index.md).
- [US2 — Frequência cardíaca no placar](cv3-ds2-us2-frequencia-cardiaca-no-placar/index.md).
- [US3 — Nova partida rápida pelo relógio](cv3-ds2-us3-nova-partida-rapida-no-relogio/index.md).
- Pedido do Navigator em 2026-09-26. As duas HUs passam na frente da CV3.DS1.US4, que continua planejada.
