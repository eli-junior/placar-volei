---
code: CV1.DS1.US3
level: User Story
status: Done
status_reason: implementado, verificado com 34 testes e validado pelo Navigator
updated: 2026-09-13
related:
  - 2026-09-13T1400Z-log-de-eventos-como-fonte-da-verdade
---

# CV1.DS1.US3 — Desfazer ponto a ponto até zerar

## Intent

Corrigir erro de marcação sem sair da tela do placar e sem limite de quantos pontos voltar.

## Scope

Botão de desfazer na tela do placar, gravação do evento `PONTO_DESFEITO` referenciando o ponto anulado, recálculo da projeção e propagação a todos os conectados.

## Acceptance / Done Condition

Given um placar em 5x3
When o controlador aciona desfazer três vezes seguidas
Then o placar mostra 3x2 em todas as telas conectadas
And o log contém os três eventos `PONTO_DESFEITO`, nenhum evento original apagado
And desfazer permanece disponível até o placar chegar a 0x0
And com o placar em 0x0 o botão de desfazer fica inativo.

## Validation Route

Marcar dez pontos alternados, desfazer todos até 0x0 conferindo cada passo em duas telas, e inspecionar a tabela de eventos confirmando que nenhuma linha foi removida.

## Out of Scope

Desfazer eventos que não sejam ponto (mudança de regra, troca de papel). Refazer.

## Notes

Desfazer também precisa reverter um encerramento de partida quando o último ponto foi o ponto da vitória — ver US4.
