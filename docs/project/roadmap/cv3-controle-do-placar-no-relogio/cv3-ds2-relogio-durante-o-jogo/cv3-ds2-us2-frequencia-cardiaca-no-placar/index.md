---
code: CV3.DS2.US2
level: User Story
status: Done
status_reason: Entregue na 0.11.0; teste físico no Galaxy Watch 8 com treino do Samsung Health aprovado em 2026-09-26
updated: 2026-09-26
related:
  - CV3.DS2.US1
---

# CV3.DS2.US2 — Frequência cardíaca no placar

## Intent
Como Eli, quero ver meu batimento no placar do relógio enquanto o Samsung Health grava o treino, sem sair do placar e sem interromper a gravação.

## Scope
- Frequência cardíaca ao vivo no topo do placar, lida do sensor pelo `MeasureClient` do Health Services, só com o placar visível.
- A frequência cardíaca não sai do relógio (nem servidor, nem espectadores).

## Acceptance / Done Condition
- Dado um treino de Vôlei ativo no Samsung Health e o placar aberto, então a frequência aparece no placar e o Samsung Health continua gravando.
- Sem permissão de sensor, nada aparece e o placar funciona igual; sem leitura, "♥ --".

## Out of Scope
Duração, calorias e zonas do Samsung Health (não legíveis por outros apps); cronômetro da partida (retirado pelo Navigator); dados do treino no site; envio em segundo plano (CV3.DS1.US4).

## Notes
- [Plano](plan.md).
- Risco conhecido: só `BODY_SENSORS` é pedido em tempo de execução (`READ_HEART_RATE` está só no manifest). Funciona no Wear OS 6 pela compatibilidade; se uma atualização quebrar, o rótulo fica em "♥ --".
- Bateria com tela acesa (US1) + sensor ligado ainda não medida.
