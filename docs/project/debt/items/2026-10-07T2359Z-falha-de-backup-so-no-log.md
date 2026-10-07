---
id: debt-falha-de-backup-so-no-log
status: Carried
kind: operations
severity: medium
source: CV8.TS1
revisit_trigger: O primeiro backup falhar em produção sem ninguém perceber, ou pedido de ver o estado dos backups
closure_condition: Mostrar a data do último backup bom (no `/health` ou numa tela) e sinalizar quando passar de ~2 intervalos
---

# Falha de Backup Só no Log

## Description

Se a pasta perder a permissão ou o disco encher, o app registra `Falha no backup do gerenciador` e segue; ninguém é avisado e a tela não mostra a idade da última cópia.

## Carrying Reason

O requisito era que a falha não derrubasse o app; visibilidade ficou para depois.

## Notes

Decisão: `docs/project/decisions/records/2026-10-07T2000Z-sqlite-duravel-com-backup-postgres-adiado.md`.
