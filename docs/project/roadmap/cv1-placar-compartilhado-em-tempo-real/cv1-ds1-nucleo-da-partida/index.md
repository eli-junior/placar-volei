---
code: CV1.DS1
level: Delivery Story
status: Active
status_reason: primeiro arco de entrega; nada mais funciona sem o núcleo
updated: 2026-09-13
related:
  - 2026-09-13T1400Z-log-de-eventos-como-fonte-da-verdade
  - 2026-09-13T1420Z-sqlite-como-persistencia
  - 2026-09-13T1425Z-stack-do-frontend
---

# CV1.DS1 — Núcleo da partida em tempo real

## Intent

Duas pessoas em celulares diferentes conseguem abrir a mesma quadra, marcar pontos, corrigir erros e ver o placar idêntico nos dois aparelhos, com o estado sobrevivendo a um restart do servidor.

## Scope

Fundação do backend e do event store, criação e listagem de quadras, registro por apelido, marcação de ponto com propagação por WebSocket, desfazer ponto a ponto, encerramento com reinício automático e empacotamento para deploy no Mini PC.

## Acceptance / Done Condition

A capacidade emergente é **uma partida completa jogável por dois dispositivos**: do 0x0 ao encerramento, com correção de erro no meio e sem perda de estado após reiniciar o processo do servidor.

## Validation Route

Dois navegadores distintos na mesma quadra; sequência de pontos com um erro deliberado corrigido; `docker restart` no meio da partida; conferência de que o placar volta idêntico.

## Out of Scope

Permissões (todos que entram podem pontuar nesta DS), configuração de regras pela UI (valores padrão no código), linha do tempo visível, owner takeover.

## Notes

Stack do frontend decidida: Svelte 5. O contrato de eventos WebSocket segue sendo o limite entre backend e frontend.

Ordem sugerida: TS1 → US1 → US2 → US3 → US4, com TS2 puxada antes da primeira validação em quadra real (validar de celular exige a aplicação fora do localhost).

`TS1` tem plano aprovado e guia de teste registrados; entra direto em implementação quando puxada.
