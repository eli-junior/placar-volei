---
code: CV5.DS3.TS1
level: Technical Story
status: Active
status_reason: Checkpoint 1 (plano) aguardando o Navigator
updated: 2026-09-27
---

# CV5.DS3.TS1 — Broadcast paralelo

## Scope
- `broadcast` com `asyncio.gather` e timeout por socket (`app/hub.py:70`); um broadcast por snapshot (`app/main.py:52`).
- `device_active` em cache ou checado só no loop; expiração avisada pelo hub em vez de SELECT por socket a cada 5 s (`app/main.py:192`).

## Acceptance
Com um cliente que não lê o socket, os demais recebem o ponto em menos de 1 s.

## Plano

[plan.md](plan.md) — branch `feature/cv5-ds3-ts1-broadcast-paralelo`.
