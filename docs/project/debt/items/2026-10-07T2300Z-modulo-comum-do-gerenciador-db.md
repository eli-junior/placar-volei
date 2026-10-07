---
id: debt-modulo-comum-do-gerenciador-db
status: Carried
kind: architecture
severity: low
source: CV8.DS1.US2
revisit_trigger: A DS2 criar um terceiro módulo sobre o `gerenciador.db`, ou o `app/jogadores.py` passar de ~500 linhas
closure_condition: Mover `_conectar`, `_erro`, `_obter`, `_linha` e `_agora` para um módulo comum, com nomes públicos
---

# Módulo Comum de Acesso ao gerenciador.db

## Description

`app/sessao.py` importa auxiliares privados (com sublinhado) de `app/jogadores.py`, que já tem ~430 linhas e mistura base de jogadores, fotos e o esquema do banco.

## Carrying Reason

Dois módulos ainda são fáceis de ler; extrair agora seria antecipar a forma da DS2.

## Notes

Decisão: `docs/project/decisions/records/2026-10-07T2300Z-sessao-unica-presenca-e-ordem-de-chegada.md`.
