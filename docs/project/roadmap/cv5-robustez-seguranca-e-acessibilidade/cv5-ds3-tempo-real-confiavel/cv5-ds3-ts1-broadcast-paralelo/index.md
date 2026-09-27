---
code: CV5.DS3.TS1
level: Technical Story
status: Done
status_reason: aceito pelo Navigator em 2026-09-27 (teste conjunto da integracao/cv5)
human_validation: accepted
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

## Revisão (Passo 5)

- **Feito:** `broadcast_many` com `asyncio.gather` e `asyncio.timeout(2 s)` por socket; o socket lento é desconectado e fechado com 1011; `device_active` saiu do envio; `publicar_snapshot` numa rodada só.
- **Considerado e não feito:** expiração avisada pelo hub (o SELECT do laço de 5 s continua).
- **Testes:** 200 passaram (2 novos, com socket falso lento).
- **Débito novo:** nenhum.
- **Validação humana pendente:** 3 celulares numa sala, um deles com "Slow 3G" no DevTools. Os outros continuam recebendo os pontos na hora, e o lento reconecta sozinho.
