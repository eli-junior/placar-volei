---
id: debt-mata-mata-sem-como-desfazer
status: Carried
kind: product
severity: medium
source: CV8.DS4.US11
revisit_trigger: A US7 (desfazer) ou um erro de encerramento no mata-mata
closure_condition: Desfazer a última partida do mata-mata e reabrir a rodada encerrada com campeão
---

# Mata-mata e Campeão sem Como Desfazer

## Description

Uma partida encerrada errada no mata-mata, ou a coroação do campeão, não pode ser revertida: a rodada fica `encerrada`. A US7 está prevista para desfazer a última partida e precisa cobrir também a rodada já encerrada.

## Carrying Reason

O desfazer é escopo da US7; abrir a rodada de volta exige decidir como tratar o sorteio seguinte já feito.

## Notes

Decisão: `docs/project/decisions/records/2026-10-08T0400Z-mata-mata-e-campeao.md`. Agravada: `rodada.py` (529 linhas) e `Sessao.svelte` (369), ver as dívidas de concentração.
