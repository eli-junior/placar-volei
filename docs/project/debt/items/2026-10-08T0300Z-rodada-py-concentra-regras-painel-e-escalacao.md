---
id: debt-rodada-py-concentra-regras-painel-e-escalacao
status: Carried
kind: architecture
severity: low
source: CV8.DS3.US8
revisit_trigger: `app/rodada.py` passou de ~500 linhas (já aconteceu); revisitar na próxima história que mexa na montagem do painel
closure_condition: Mover a montagem do painel da condução para um módulo próprio
---

# rodada.py Concentra Regras, Painel e Escalação

## Description

`app/rodada.py` (713 linhas na 0.49.0; eram 452 quando o item foi aberto) reúne o ciclo da rodada, a montagem do painel da condução e a escalação do parceiro.

## Carrying Reason

Ainda legível, mas o gatilho de tamanho já foi cruzado (US19 e US22 acrescentaram o painel de retirada e o do triângulo). A divisão natural é tirar `montar_conducao` e a escalação para um módulo próprio.

## Notes

Decisão: `docs/project/decisions/records/2026-10-08T0300Z-escalacao-do-parceiro-do-incompleto.md`.
