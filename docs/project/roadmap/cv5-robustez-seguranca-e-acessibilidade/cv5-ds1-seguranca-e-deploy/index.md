---
code: CV5.DS1
level: Delivery Story
status: Planned
updated: 2026-09-27
---

# CV5.DS1 — Segurança e deploy

## Intent
O PIN volta a ser o que separa uma sala dos curiosos, e atualizar o Mini PC não apaga nada.

## Histórias (em ordem)
1. [TS1 — Sigilo do PIN e limite por cliente real](cv5-ds1-ts1-sigilo-do-pin/index.md)
2. [TS2 — Deploy seguro](cv5-ds1-ts2-deploy-seguro/index.md)
3. [TS3 — Higiene do SQLite e da memória](cv5-ds1-ts3-higiene-do-sqlite/index.md)

## Acceptance / Done Condition
Listagem pública não expõe PIN (ou a decisão de expor fica registrada), tentativas de PIN são limitadas pelo IP real, e `docker compose up -d --build` preserva salas e vínculos.
