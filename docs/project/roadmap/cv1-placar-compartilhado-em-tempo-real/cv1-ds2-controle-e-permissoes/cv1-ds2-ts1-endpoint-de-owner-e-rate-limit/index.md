---
code: CV1.DS2.TS1
level: Technical Story
status: Planned
status_reason:
updated: 2026-09-13
related:
  - 2026-09-13T1415Z-owner-takeover-por-codigo-mestre
---

# CV1.DS2.TS1 — Endpoint de owner e proteção contra força bruta

## Intent

Existir um canal de operador, isolado da aplicação, capaz de revelar os códigos mestres, e um limitador que torne 4 dígitos defensáveis.

## Scope

Geração do código de 4 dígitos por quadra com fonte criptograficamente segura, segredo de owner no `.env`, endpoint `/owner/quadras` autenticado por esse segredo, e rate limit por sessão/IP com bloqueio progressivo após 5 tentativas falhas.

## Acceptance / Done Condition

Given o endpoint de owner publicado
When uma requisição chega sem o segredo correto
Then a resposta não revela nenhum código nem a existência do endpoint na UI
And após 5 tentativas falhas de código mestre a partir da mesma sessão/IP, novas tentativas são bloqueadas por janela crescente
And o segredo de owner não aparece em nenhuma resposta de API pública nem em log de aplicação.

## Validation Route

Script de 20 tentativas sequenciais de código incorreto, verificando o bloqueio. `grep` no log da aplicação procurando o segredo. Requisição ao endpoint com e sem o segredo.

## Out of Scope

A ação de takeover em si (US3).

## Notes

Definir no plano o comportamento do contador de tentativas após restart do processo.
