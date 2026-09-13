---
status: Decided
raised: 2026-09-13
decided: 2026-09-13
deciders:
  - Navigator
supersedes:
related:
  - CV1.DS1
---

# SQLite como persistência única

## Question

Onde o estado das quadras e o log de eventos são gravados?

## Decision

SQLite, arquivo local no volume do contêiner no Mini PC. Sem servidor de banco, sem cache externo, sem fila.

O estado da partida é reconstruído do log de eventos na inicialização do processo.

## Rationale

A escala é de dezenas de pessoas e dezenas de eventos por partida. Um arquivo SQLite atende com folga e reduz a superfície de operação de uma máquina doméstica ligada 24/7 — princípio "simplicidade de operação vale mais que completude".

Gravação em disco é o que satisfaz o requisito de sobreviver a restart do Mini PC no meio do jogo.

## Options Considered

- **Estado apenas em memória** — rejeitado pelo Navigator: queda do processo zeraria a partida em andamento.
- **PostgreSQL** — rejeitado: custo operacional desproporcional à escala.

## Consequences

- Escrita concorrente exige atenção ao modo WAL e à serialização dos appends no log.
- Backup é cópia de arquivo; precisa entrar nas notas de operação.
- Migração de schema precisa de estratégia mínima antes da primeira partida real gravada.

## Review Trigger

Se o sistema passar a servir múltiplos grupos simultâneos com escrita concorrente relevante, reavaliar.
