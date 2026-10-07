---
id: debt-rodada-trava-sem-ninguem-elegivel
status: Carried
kind: product
severity: low
source: CV8.DS3.US8
revisit_trigger: Rodada parada no time incompleto por falta de elegíveis
closure_condition: Saída para a rodada sem elegíveis (escolher entre os que aguardam ou encerrar sem o incompleto)
---

# Rodada Trava sem Ninguém Elegível

## Description

Se não houver jogador eliminado elegível para o time incompleto, a rodada fica parada e só cancelar resolve. Não deve ocorrer: o incompleto só entra depois de uma partida e o perdedor dela é elegível.

## Carrying Reason

Caso teórico; o painel já avisa "ninguém elegível".

## Notes

Decisão: `docs/project/decisions/records/2026-10-08T0300Z-escalacao-do-parceiro-do-incompleto.md`.
