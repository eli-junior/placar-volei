---
id: debt-ponte-py-concentra-vinculo-chamada-e-encerramento
status: Carried
kind: architecture
severity: low
source: CV8.DS3.US6
revisit_trigger: `app/ponte.py` passar de ~450 linhas, ou a US7/US8 mexerem nela
closure_condition: Dividir em vínculo, chamada/encerramento e leitura do placar
---

# ponte.py Concentra Vínculo, Chamada e Encerramento

## Description

`app/ponte.py` (381 linhas) reúne o vínculo com a quadra, a chamada da partida, o encerramento e a leitura do placar.

## Carrying Reason

Ainda legível; a divisão depende do que a US7 e a US8 pedirem.

## Notes

Decisão: `docs/project/decisions/records/2026-10-08T0200Z-encerramento-lendo-o-placar.md`.
