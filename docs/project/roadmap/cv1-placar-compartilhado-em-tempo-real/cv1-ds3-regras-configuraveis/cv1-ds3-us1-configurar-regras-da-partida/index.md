---
code: CV1.DS3.US1
level: User Story
status: Active
status_reason: puxada para desenvolvimento
updated: 2026-09-15
related:
  - CV1.DS1.US4
---

# CV1.DS3.US1 — Configurar pontuação-alvo, vantagem e teto

## Intent

Ajustar a regra da pelada em segundos, na hora em que o grupo combina.

## Scope

Painel de configuração da quadra com pontuação-alvo (padrão 12), interruptor de vantagem mínima de 2 pontos e teto opcional da vantagem, com validação de valores e evento `REGRA_ALTERADA`.

## Acceptance / Done Condition

Given uma quadra com partida em andamento em 11x11 e alvo 12 com vantagem ligada
When o admin desliga a exigência de vantagem
Then o próximo ponto de qualquer lado encerra a partida
And a alteração fica registrada como evento com autor e horário
And com o posto de admin vago, um controlador consegue fazer a mesma alteração
And um espectador não consegue, mesmo forjando a chamada fora da UI
And um teto menor que a pontuação-alvo é rejeitado com mensagem clara.

## Validation Route

Partida em 11x11 em duas telas. Desligar a vantagem e marcar ponto. Repetir religando a vantagem e definindo teto 15, chegando a 15x14. Tentar salvar teto 10 com alvo 12 e conferir a rejeição.

## Out of Scope

Alterar regra de partidas já arquivadas.

## Notes

Alteração com partida em andamento é permitida por decisão de produto — a quadra manda. O que não pode é a alteração passar despercebida.
