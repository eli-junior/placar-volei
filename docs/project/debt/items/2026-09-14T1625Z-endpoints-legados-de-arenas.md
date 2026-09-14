---
id: debt-arenas-legadas
status: Carried
kind: architecture
severity: low
source: CV1.DS1.US1
revisit_trigger: Decisão de descontinuação formal e remoção do suporte a arenas no backend
closure_condition: Exclusão da tabela arenas e rotas /api/arenas/* após refatoração dos testes legados
---

# Endpoints e Tabelas Legadas de Arenas Mantidos por Retrocompatibilidade

## Description

Com a transição para o modelo direto de salas por PIN de 5 dígitos, a hierarquia de arenas foi removida do fluxo do usuário e do frontend. No entanto, a tabela `arenas` no SQLite, funções auxiliares em `app/quadras.py` e rotas `/api/arenas/*` em `app/api.py` continuam existindo no código para preservar compatibilidade com testes anteriores e fixtures.

## Carrying Reason

A remoção imediata exigiria reescrever ou eliminar testes existentes de fixtures e endpoints que ainda validam o comportamento da API legada. Manter o código isolado não prejudica o novo fluxo de salas por código.

## Impact

Baixo. Há pequenas linhas de código morto do ponto de vista do frontend, sem impacto perceptível de performance ou segurança.

## Revisit Trigger

Quando o Navigator aprovar um ciclo de faxina técnica ou consolidação do roadmap que elimine expressamente o conceito de arenas do repositório.

## Closure Condition

Remoção da tabela `arenas` em `SCHEMA_SQL`, limpeza das rotas legadas em `app/api.py` e atualização dos testes em `test_fixtures.py` e `test_quadras_e_participantes.py`.
