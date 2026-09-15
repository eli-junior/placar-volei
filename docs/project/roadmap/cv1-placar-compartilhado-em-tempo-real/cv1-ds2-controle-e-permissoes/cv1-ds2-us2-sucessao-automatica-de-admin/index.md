---
code: CV1.DS2.US2
level: User Story
status: Active
status_reason: puxada para desenvolvimento
updated: 2026-09-15
related:
  - 2026-09-13T1410Z-sucessao-automatica-de-admin
---

# CV1.DS2.US2 — Sucessão automática do admin

## Intent

A partida não trava porque o admin ficou sem bateria.

## Scope

Rastreio de presença por WebSocket, ordem de chegada dos controladores, temporizador de 2 minutos de admin offline, promoção automática do controlador online há mais tempo, evento `ADMIN_SUCEDIDO` e retorno do admin original como controlador.

## Acceptance / Done Condition

Given uma quadra com admin e dois controladores
When o admin fica offline por mais de 2 minutos
Then o controlador que entrou primeiro é promovido a admin
And o evento aparece para todos na quadra
And quando o admin original reconecta, ele volta como controlador
And se não houver controlador online, a quadra segue sem admin e os controladores existentes continuam pontuando.

## Validation Route

Três navegadores. Fechar o do admin e cronometrar. Conferir a promoção e reabrir o navegador original para verificar o papel de retorno. Repetir o cenário sem controlador online.

## Out of Scope

Devolução automática do posto ao admin original.

## Notes

Enquanto o posto de admin estiver vago, qualquer controlador pode alterar a configuração da quadra.
