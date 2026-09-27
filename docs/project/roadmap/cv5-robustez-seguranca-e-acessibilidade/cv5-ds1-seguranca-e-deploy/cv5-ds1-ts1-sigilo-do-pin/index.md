---
code: CV5.DS1.TS1
level: Technical Story
status: Planned
updated: 2026-09-27
related:
  - docs/project/debt/items/2026-09-23T1305Z-limite-de-vinculo-do-relogio-por-ip-e-em-memoria.md
---

# CV5.DS1.TS1 — Sigilo do PIN e limite por cliente real

## Scope
- `GET /api/quadras` (`app/api.py:228`, `app/quadras.py:336`) deixa de devolver o `id`/PIN, ou fica só para o owner. **Decisão do Navigator:** o lobby público é requisito?
- Limite de tentativas por IP em `POST /entrar` para respostas 404.
- IP real via `CF-Connecting-IP` (ou `--proxy-headers --forwarded-allow-ips`) em vez do primeiro valor de `X-Forwarded-For` (`app/api.py:631`).
- Limite de aprovação do relógio também por IP e por quadra, não só por participante (`app/watch.py:399`).
- PIN gerado com `secrets` (`app/quadras.py:87`); `x-session-id` aceito só como UUID (`app/api.py:215`).

## Acceptance
- Dado um visitante sem PIN, quando consulta a listagem, então nenhum PIN aparece.
- Quando alguém erra PINs em sequência trocando `X-Forwarded-For`, então o bloqueio vale do mesmo jeito.

## Notes
Paga `debt-limite-de-vinculo-do-relogio-por-ip-e-em-memoria` (parte do IP real).
