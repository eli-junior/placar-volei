---
id: debt-sorteio-heuristico-sem-prova-de-otimo
status: Carried
kind: algorithm
severity: low
source: CV8.DS2.US3
revisit_trigger: Reclamação de duplas desequilibradas com 12 ou mais jogadores
closure_condition: Comparar com busca exata (programação dinâmica) para 12–20 jogadores e ajustar a heurística
---

# Sorteio Heurístico sem Prova de Ótimo

## Description

O equilíbrio é achado por trocas e reinícios determinísticos. Foi conferido contra força bruta até 10 jogadores; com 12 ou mais não há prova de que seja o ótimo.

## Carrying Reason

Para o tamanho de uma pelada o resultado é bom e instantâneo (19 ms com 24 jogadores).

## Notes

Decisão: `docs/project/decisions/records/2026-10-08T0000Z-sorteio-da-primeira-rodada.md`.
