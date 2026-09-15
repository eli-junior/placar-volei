---
code: CV1.DS2
level: Delivery Story
status: Validated
status_reason: histórias ativas concluídas e validadas (US1, US2, TS1); US3 adiada
updated: 2026-09-15
related:
  - 2026-09-13T1410Z-sucessao-automatica-de-admin
  - 2026-09-13T1415Z-owner-takeover-por-codigo-mestre
---

# CV1.DS2 — Controle e permissões da quadra

## Intent

A quadra tem dono claro e continua administrável mesmo quando o admin some, com uma saída de emergência para o operador da instância.

## Scope

Papéis (admin, controlador, espectador), promoção e revogação de controladores, restrição de pontuar a quem tem permissão, presença por WebSocket, sucessão automática após 2 minutos de admin offline, endpoint de owner protegido, rate limit e owner takeover por código mestre.

## Acceptance / Done Condition

A capacidade emergente é **autoridade resiliente**: nenhuma configuração de papéis deixa a quadra travada, e o operador sempre consegue recuperar o controle de forma auditável.

## Validation Route

Cenário completo em três dispositivos: admin promove controlador, espectador tenta pontuar e é impedido, admin cai e a sucessão ocorre, operador assume por takeover.

## Out of Scope

Contas persistentes entre partidas, papéis adicionais, banimento de participante.

## Notes

Histórico de entregas do arco:

- `US1` (Admin promove e revoga controladores): Concluída e validada em 2026-09-14 (v0.3.1).
- `US2` (Sucessão automática de admin após ausência): Concluída e validada em 2026-09-15 (v0.3.3).
- `TS1` (Endpoint de owner e rate limit contra força bruta): Concluída e validada em 2026-09-15 (v0.4.1).
- `US3` (Owner takeover por código mestre): Adiada (Deferred) por decisão do Navigator em 2026-09-15 (salas conflitantes podem ser simplesmente recriadas).
