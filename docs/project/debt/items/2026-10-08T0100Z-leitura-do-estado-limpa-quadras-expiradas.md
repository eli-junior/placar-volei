---
id: debt-leitura-do-estado-limpa-quadras-expiradas
status: Carried
kind: architecture
severity: low
source: CV8.DS3.US5
revisit_trigger: Mais telas lendo o estado da sessão, ou queixa de quadra sumindo
closure_condition: Ler o vínculo sem apagar quadras vencidas (consulta sem efeito colateral)
---

# Ler o Estado Limpa Quadras Expiradas

## Description

`info_quadra` chama `obter_quadra_sync`, que apaga quadras vencidas do placar a cada leitura do estado e a cada difusão.

## Carrying Reason

A limpeza já roda a cada 5 minutos; o efeito extra é inofensivo hoje.

## Notes

Decisão: `docs/project/decisions/records/2026-10-08T0100Z-ponte-com-o-placar-e-sincronia.md`.
