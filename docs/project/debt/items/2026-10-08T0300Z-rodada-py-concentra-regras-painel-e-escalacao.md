---
id: debt-rodada-py-concentra-regras-painel-e-escalacao
status: Carried
kind: architecture
severity: low
source: CV8.DS3.US8
revisit_trigger: `app/rodada.py` passar de ~500 linhas, ou a US9/US10 mexerem nele
closure_condition: Mover a montagem do painel da condução para um módulo próprio
---

# rodada.py Concentra Regras, Painel e Escalação

## Description

`app/rodada.py` (452 linhas) reúne o ciclo da rodada, a montagem do painel da condução e a escalação do parceiro.

## Carrying Reason

Ainda legível; a divisão certa depende do que a US9 e a US10 pedirem.

## Notes

Decisão: `docs/project/decisions/records/2026-10-08T0300Z-escalacao-do-parceiro-do-incompleto.md`.
