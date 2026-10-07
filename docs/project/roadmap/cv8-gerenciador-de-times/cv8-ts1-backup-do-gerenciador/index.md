---
code: CV8.TS1
level: Technical Story
status: Active
status_reason: puxada em 2026-10-07; Passo 2 (plano)
updated: 2026-10-07
related:
  - ../../../decisions/records/2026-10-07T2000Z-sqlite-duravel-com-backup-postgres-adiado.md
  - ../../../debt/items/2026-10-07T1800Z-sem-backup-do-volume-de-jogadores.md
---

# Backup do `gerenciador.db`

## Intent

Dar resiliência à base durável do gerenciador (jogadores, notas, fotos e, depois, sessões e histórico): uma cópia consistente, fora do volume `gerenciador-dados`, que permita restaurar depois de perder o volume. Quita a dívida `sem-backup-do-volume-de-jogadores`.

## Scope

- Rotina de backup que usa a API de backup do SQLite (`sqlite3 .backup` / `Connection.backup`), consistente com o app rodando e com o WAL ativo.
- Destino **fora do volume** do banco (pasta no host do Mini PC, montada no compose), com retenção das últimas N cópias (padrão a definir no plano; ex.: diárias por 14 dias).
- Disparo: ao subir o contêiner, a cada intervalo configurável e sob demanda. O mecanismo (tarefa interna do app, serviço no compose ou `cron` do host) é escolhido no plano.
- Verificação de integridade da cópia (`PRAGMA integrity_check`) logo após gravá-la.
- Procedimento de **restauração** documentado e testado (parar o app, trocar o arquivo, subir).
- Variáveis de configuração no `.env.example`.

## Acceptance / Done Condition

Given um `gerenciador.db` com jogadores, notas e fotos
When a rotina de backup roda com o app em uso
Then surge uma cópia íntegra no destino, fora do volume, e as mais antigas além da retenção são removidas
And restaurar essa cópia num volume novo devolve todos os jogadores, notas e fotos
And uma cópia que falha na verificação é sinalizada no log e não substitui a última boa.

## Validation Route

A definir no plano: rodar o backup, abrir a cópia com `sqlite3` e conferir a contagem de jogadores; apagar o volume de propósito (`docker volume rm`, com autorização do Navigator, em ambiente de teste) e restaurar.

## Out of Scope

Migração para Postgres (adiada; ver a decisão); backup do banco efêmero das quadras; envio da cópia para a nuvem (pode virar história própria).
