---
id: debt-ws-nao-fecha-ao-trocar-o-segredo
status: Carried
kind: security
severity: low
source: CV8.DS3.US5
revisit_trigger: Vazamento do `OWNER_SECRET` seguido de troca
closure_condition: Fechar os WebSockets do gerenciador quando o segredo mudar (ou revalidar periodicamente)
---

# WebSocket Não Fecha ao Trocar o Segredo

## Description

Quem já está conectado em `/ws/gerenciador` continua recebendo o estado depois de o `OWNER_SECRET` ser trocado, até reconectar.

## Carrying Reason

A troca exige reiniciar o app, o que já derruba as conexões; o risco restante é mínimo.

## Notes

Decisão: `docs/project/decisions/records/2026-10-08T0100Z-ponte-com-o-placar-e-sincronia.md`.
