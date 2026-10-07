---
id: debt-antes-da-restauracao-se-acumulam
status: Carried
kind: operations
severity: low
source: CV8.TS1
revisit_trigger: Restaurar mais de algumas vezes, ou o volume ficar apertado
closure_condition: Comando para listar e limpar os `.antes-*` antigos, ou retenção automática
---

# Arquivos .antes da Restauração se Acumulam

## Description

Cada restauração deixa o banco substituído como `gerenciador.db.antes-<data>` (e `-wal`/`-shm`) no volume, e nada os apaga.

## Carrying Reason

Restaurar é raro e guardar o banco anterior é a proteção desejada; o acúmulo é pequeno.

## Notes

Decisão: `docs/project/decisions/records/2026-10-07T2000Z-sqlite-duravel-com-backup-postgres-adiado.md`.
