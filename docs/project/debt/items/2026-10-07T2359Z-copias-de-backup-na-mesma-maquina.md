---
id: debt-copias-de-backup-na-mesma-maquina
status: Carried
kind: operations
severity: medium
source: CV8.TS1
revisit_trigger: Dado do gerenciador (fotos, sessões, histórico) passar a ser difícil de refazer, ou troca/queda do Mini PC
closure_condition: Cópia periódica da pasta `backups/` para fora da máquina (nuvem ou outro disco), com restauração testada a partir dela
---

# Cópias de Backup na Mesma Máquina

## Description

A pasta `./backups` protege contra apagar ou corromper o volume `gerenciador-dados`, mas fica no mesmo disco do Mini PC: perder o disco ou a máquina perde banco e cópias.

## Carrying Reason

Primeira camada de resiliência entregue; o envio para fora foi deixado fora do escopo da TS1 (a pasta do host facilita um `rsync`/`rclone`).

## Notes

Decisão: `docs/project/decisions/records/2026-10-07T2000Z-sqlite-duravel-com-backup-postgres-adiado.md`.
