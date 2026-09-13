---
code: CV1.DS1.US2
level: User Story
status: Planned
status_reason:
updated: 2026-09-13
related:
  - 2026-09-13T1425Z-stack-do-frontend
---

# CV1.DS1.US2 — Marcar ponto e ver o placar sincronizado

## Intent

Marcar ponto com um toque e todos na quadra verem o placar mudar imediatamente.

## Scope

Tela do placar com Time A e Time B, botão de ponto por lado dimensionado para uso com uma mão, gravação do evento `PONTO_MARCADO`, propagação por WebSocket a todos os conectados da quadra e reconexão automática com reconciliação de estado.

## Acceptance / Done Condition

Given dois participantes conectados na mesma quadra
When um deles marca ponto para o Time A
Then o placar do Time A incrementa em ambas as telas em até 2 segundos
And o evento fica gravado no log com autor e timestamp
And o número transiciona visualmente em vez de trocar seco
And se um participante perder a conexão e voltar, sua tela mostra o placar correto sem recarregar manualmente.

## Validation Route

Dois celulares na mesma quadra. Marcar pontos alternados observando as duas telas. Colocar um celular em modo avião por 30 segundos, restaurar e conferir a reconciliação.

## Out of Scope

Restrição de quem pode pontuar (entra em DS2), desfazer, linha do tempo.

## Notes

A transição do número do placar (`spring` ou `tween`) faz parte do aceite, não é polimento posterior.
