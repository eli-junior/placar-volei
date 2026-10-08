---
id:
status: Carried
kind: architecture
severity: low
source: CV8.DS6.US15
revisit_trigger: novo tamanho de time ou mudança de regra que mexa no sorteio de duplas e de trios
closure_condition: um algoritmo único para qualquer tamanho, coberto pelos testes de duplas e trios
---

# Dois algoritmos de sorteio (dupla e trio)

## Description

`app/sorteio.py` tem o caminho das duplas (`_inicial`, `_descer`, `_candidatas`) e o dos trios (`*_n`), paralelos.

## Carrying Reason

As duplas têm regra própria de H+H e estão validadas; unificar arriscava regressão na US15.

## Impact

Mudança de regra de equilíbrio precisa ser feita nos dois.

## Notes

Ver worklog 2026-10-08T1100Z.
