---
code: CV1.DS3
level: Delivery Story
status: Active
status_reason: US2 (jogadores e inversão) entregue na v0.3.2; US1 (regras configuráveis) em planejamento
updated: 2026-09-14
related:
  - CV1.DS1.US4
---

# CV1.DS3 — Regras da partida configuráveis pela quadra

## Intent

Cada grupo joga com a regra que combinou, sem depender de alteração de código.

## Scope

Pontuação-alvo, exigência de vantagem de 2 pontos (liga/desliga), teto opcional da vantagem, edição pelo admin — ou por qualquer controlador quando o posto estiver vago — e registro da alteração como evento.

## Acceptance / Done Condition

A capacidade emergente é **regra do jogo sob controle da quadra**: alterar a configuração muda o comportamento do encerramento na partida em andamento e fica registrado na linha do tempo.

## Validation Route

Alterar cada parâmetro com partida em andamento e confirmar o efeito na condição de vitória.

## Out of Scope

Sets múltiplos, tie-break, nomes personalizados de times, presets de modalidade.
