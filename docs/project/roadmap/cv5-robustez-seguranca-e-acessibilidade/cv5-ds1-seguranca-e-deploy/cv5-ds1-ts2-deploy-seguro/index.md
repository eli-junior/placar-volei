---
code: CV5.DS1.TS2
level: Technical Story
status: Active
status_reason: Checkpoint 1 (plano) aguardando o Navigator
updated: 2026-09-27
related:
  - docs/project/debt/items/2026-09-23T1310Z-banco-de-producao-sem-volume-persistente.md
---

# CV5.DS1.TS2 — Deploy seguro

## Scope
- Montar `./data:/data` no `docker-compose.yml` e documentar a atualização.
- `OWNER_SECRET` obrigatório (`${OWNER_SECRET:?}`); o app recusa subir com o valor padrão (`app/config.py:12`).
- `/health` sem o caminho do banco (`app/main.py:131`); cookie de sessão com `secure=True` (`app/api.py:327`).

## Acceptance
- Dado um deploy com `--build`, então salas e vínculos do relógio continuam.
- Sem `OWNER_SECRET`, o container não sobe e diz por quê.

## Notes
Paga `debt-banco-de-producao-sem-volume-persistente`.

## Plano

[plan.md](plan.md) — branch `feature/cv5-ds1-ts2-deploy-seguro`.
