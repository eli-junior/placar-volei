---
id: debt-relogio-local-sem-servico-em-primeiro-plano
status: Carried
kind: operation
severity: low
source: CV7.US2
revisit_trigger: Lances do relógio na quadra local ficarem presos com a tela do relógio apagada por mais que alguns minutos, ou o app do relógio ser encerrado pelo sistema no meio de uma partida local
closure_condition: A `CelularSessao` rodar sob o mesmo serviço em primeiro plano (`WatchSessionService`) do modo servidor, mantendo o envio da fila e a notificação de partida em andamento
---

# Relógio na Quadra Local sem Serviço em Primeiro Plano

## Description

O modo servidor mantém o app vivo com o `WatchSessionService` (Ongoing Activity). O modo da quadra local (CV7.US2) não: a `CelularSessao` roda no processo do app. Os lances ficam na fila durável do relógio e são enviados quando a atividade volta, mas se o sistema encerrar o app com a tela apagada o envio espera a próxima abertura.

## Carrying Reason

O relógio só gera lance por toque, com a tela acesa, e o envio sai logo depois. O serviço traria uma notificação fixa e o custo de bateria do modo servidor, sem necessidade comprovada na quadra.

## Notes

Os recibos por id do celular tornam o reenvio seguro depois de qualquer interrupção.
