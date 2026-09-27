---
code: CV5.DS1.TS1
level: Technical Story
status: Done
status_reason: aceito pelo Navigator em 2026-09-27 (teste conjunto da integracao/cv5)
human_validation: accepted
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

## Plano

[plan.md](plan.md) — branch `feature/cv5-ds1-ts1-sigilo-do-pin`.

## Revisão (Passo 5)

- **Refatoração feita:** `extrair_chave_rate_limit` substituída por `app/rede.py`, usada por owner, pareamento, aprovação e entrada.
- **Considerado e não feito:** limite persistido entre reinícios (continua em memória).
- **Débito pago em parte:** `debt-limite-de-vinculo-do-relogio-por-ip-e-em-memoria` (o IP agora é o real; a persistência continua pendente).
- **Débito novo:** nenhum.
- **Docs:** decisão `2026-09-27T1500Z-lobby-publico-e-pin-como-identificador`; `.env.example`.
- **Validação humana pendente:** roteiro do Checkpoint 2 (curl com `X-Forwarded-For` trocado, 21 códigos errados, uso normal com relógio).
