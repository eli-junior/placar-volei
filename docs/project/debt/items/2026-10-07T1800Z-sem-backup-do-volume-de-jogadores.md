---
id: debt-sem-backup-do-volume-de-jogadores
status: Carried
kind: operations
severity: medium
source: CV8.DS1.US1
revisit_trigger: Sessões e histórico (CV8.DS2+) passarem a depender do mesmo arquivo, ou perda do volume
closure_condition: CV8.TS1 entregue — rotina de backup/exportação do `gerenciador.db` testada com restauração
---

# Sem Backup do Volume de Jogadores

## Description

O volume `gerenciador-dados` é o primeiro dado durável do projeto e não tem cópia. Perder o volume perde o cadastro.

## Carrying Reason

Hoje o cadastro é pequeno e refazível; o valor cresce com sessões e histórico.

## Updates

- 2026-10-07: tratada pela Technical Story `CV8.TS1` (backup do `gerenciador.db`); Postgres foi considerado e adiado.

## Notes

Decisão: `docs/project/decisions/records/2026-10-07T1800Z-base-de-jogadores-duravel-e-protegida.md`.
