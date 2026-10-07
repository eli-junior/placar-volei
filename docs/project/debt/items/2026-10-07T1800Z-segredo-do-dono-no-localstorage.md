---
id: debt-segredo-do-dono-no-localstorage
status: Carried
kind: security
severity: low
source: CV8.DS1.US1
revisit_trigger: Entrar conteúdo de terceiros na página, ou o cadastro passar a guardar dado sensível
closure_condition: Trocar o segredo guardado por sessão com expiração (cookie HttpOnly) ou pedir o segredo a cada uso
---

# Segredo do Dono Guardado no localStorage

## Description

A tela de jogadores guarda o `OWNER_SECRET` no `localStorage` do navegador. Um XSS o exporia e daria acesso a toda a base.

## Carrying Reason

Não há conteúdo de terceiros na página e é uma pelada; guardar evita digitar a cada visita. Decisão do Navigator (2026-10-07).

## Notes

Decisão: `docs/project/decisions/records/2026-10-07T1800Z-base-de-jogadores-duravel-e-protegida.md`.
