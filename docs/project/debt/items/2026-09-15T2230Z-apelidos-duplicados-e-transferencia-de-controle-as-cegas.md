---
id: debt-apelidos-e-transferencia-de-controle
status: Paying
kind: correctness
severity: medium
source: CV1.DS2.US1
revisit_trigger: Relato de controle perdido para participante ausente, ou confusão de identidade na sala
closure_condition: Apelidos únicos por quadra e transferência de controle bloqueada para participantes offline, com auto-retorno ao admin
---

# Apelidos Duplicados e Transferência de Controle para Participantes Offline

## Description

Dois vazamentos de integridade no modelo de identidade e permissão da sala:

1. **Apelidos duplicados (A5):** nada impede que dois participantes da mesma quadra usem o mesmo apelido. Como a linha do tempo e a lista de presentes identificam pessoas por apelido, isso permite personificação e torna a auditoria da partida ambígua.
2. **Transferência às cegas (A4):** promover um controlador não distingue conceder permissão de transferir o controle ativo, e nada impede repassar o comando para alguém desconectado. A partida fica sem operador até que o admin perceba e retome manualmente.

## Carrying Reason

A `CV1.DS2` entregou o modelo de papéis (admin, controlador, participante) e a sucessão automática do admin. A granularidade entre permissão e posse do controle ativo ficou deliberadamente fora do escopo daquela story.

## Revisit Trigger

Qualquer mudança no modelo de papéis, presença ou sucessão.

## Closure Condition

Rejeição de apelido já em uso na quadra com mensagem clara, bloqueio de repasse de controle para participante offline e auto-retorno do controle ao admin após 15s de ausência do controlador, tudo com teste automatizado.

## Notes

Pago por `CV2.DS2` (US5 e US6).
