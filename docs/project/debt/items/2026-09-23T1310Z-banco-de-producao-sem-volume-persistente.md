---
id: debt-banco-de-producao-sem-volume-persistente
status: Carried
kind: operation
severity: medium
source: CV3.DS1.US1
revisit_trigger: Próximo deploy que precise preservar salas, ou reclamação de vínculo perdido após atualização
closure_condition: /data montado em volume nomeado no docker-compose, com o procedimento de atualização documentado
---

# Banco de Produção sem Volume Persistente

## Description

O `docker-compose.yml` grava o SQLite em `/data` dentro do contêiner, sem volume. `docker compose up -d --build` recria o contêiner e apaga salas, participantes, habilitações e vínculos de relógio. `docker compose restart` preserva.

## Carrying Reason

As salas são efêmeras (TTL de uma hora), então a perda era tolerada. Com o relógio, cada deploy também obriga a vincular o relógio de novo.

## Revisit Trigger

Qualquer mudança de deploy, ou quando o custo de revincular aparecer no uso.

## Closure Condition

Volume nomeado para `/data`, com a atualização validada preservando uma sala ativa.
