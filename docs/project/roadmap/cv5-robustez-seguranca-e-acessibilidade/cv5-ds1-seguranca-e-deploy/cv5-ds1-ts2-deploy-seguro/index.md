---
code: CV5.DS1.TS2
level: Technical Story
status: Validated
status_reason: automode aprovado pelo Navigator em 2026-09-27; testes automatizados verdes
human_validation: pending
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

## Revisão (Passo 5)

- **Feito:** volume nomeado `placar-data`; `OWNER_SECRET` obrigatório no compose e recusado em produção se for o de exemplo; `/health` sem `db`; `COOKIE_SECURE`.
- **Considerado e não feito:** bind `./data` (exigiria `chown 1001` no host).
- **Débito pago:** `debt-banco-de-producao-sem-volume-persistente`.
- **Débito novo:** nenhum.
- **Docs:** `development-guide.md` (atualização, backup, `COOKIE_SECURE`), `.env.example`.
- **Validação humana pendente:** conferir que o `.env` do Mini PC tem `OWNER_SECRET` próprio antes do deploy; criar sala, `docker compose up -d --build`, conferir a sala; `curl -sI` mostrando `Secure` no `Set-Cookie`; primeiro deploy começa com banco vazio (parear o relógio de novo).
