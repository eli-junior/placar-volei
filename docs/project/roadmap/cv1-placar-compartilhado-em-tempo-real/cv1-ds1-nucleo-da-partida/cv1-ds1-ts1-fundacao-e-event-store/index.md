---
code: CV1.DS1.TS1
level: Technical Story
status: Done
status_reason: implementado e validado com 14 testes automatizados e script de integridade de banco
updated: 2026-09-13
related:
  - 2026-09-13T1400Z-log-de-eventos-como-fonte-da-verdade
  - 2026-09-13T1420Z-sqlite-como-persistencia
---

# CV1.DS1.TS1 — Fundação do backend e event store

## Intent

Existir uma base FastAPI + SQLite onde eventos são gravados de forma append-only e o estado da partida é uma projeção determinística desse log.

## Scope

Projeto FastAPI, schema SQLite (quadras, participantes, partidas, eventos), tipos de evento do MVP, função de append, função de projeção, reconstrução de estado na inicialização, hub de conexões WebSocket por quadra e configuração por `.env`.

## Acceptance / Done Condition

Given uma sequência de eventos gravada no log
When a projeção é executada sobre essa sequência
Then o estado resultante é idêntico ao esperado
And executar a projeção de novo sobre o mesmo log produz exatamente o mesmo estado.

## Validation Route

Suíte de testes da projeção, incluindo sequência com pontos e desfazimentos intercalados. Inspeção do arquivo SQLite mostrando eventos em ordem e nenhuma linha de evento alterada ou removida.

## Out of Scope

Qualquer interface de usuário. Snapshot ou compactação do log.

## Notes

Plano aprovado e registrado em `plan.md`. Guia de teste em `test-guide.md`. A story está pronta para implementação: o próximo ciclo entra direto na fase de implementação, sem repetir o Checkpoint 1.

A serialização dos appends por quadra precisa ser explícita — dois controladores marcando ponto no mesmo instante não podem produzir sequência ambígua.
