---
code: CV5.DS1.TS3
level: Technical Story
status: Active
status_reason: Checkpoint 1 (plano) aguardando o Navigator
updated: 2026-09-27
---

# CV5.DS1.TS3 — Higiene do SQLite e da memória

## Scope
- Validar `^\d{5}$` antes de criar lock de sala e limpar `_quadra_locks` na expiração (`app/eventos.py:41`, `app/main.py:145`).
- Limpeza de salas apaga também `watch_recibos` (`app/quadras.py:115`).
- Listagem sem rodar a limpeza e sem reprojetar o log de cada sala por GET (`app/quadras.py:337`).
- `PRAGMA busy_timeout`, WAL só no init, `synchronous=NORMAL` (`app/db.py:106`).
- **Decisão do Navigator:** migrar o schema em vez de apagar o banco a cada versão (`app/db.py:130`), preservando os recibos de idempotência.

## Acceptance
Conexões em `/ws/<id inválido>` não criam estado; depois da expiração não sobra linha da sala em nenhuma tabela.

## Plano

[plan.md](plan.md) — branch `feature/cv5-ds1-ts3-higiene-do-sqlite`.
