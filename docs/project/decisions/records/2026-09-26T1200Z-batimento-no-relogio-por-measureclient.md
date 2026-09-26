---
id: batimento-no-relogio-por-measureclient
status: Decided
raised: 2026-09-26
decided: 2026-09-26
deciders:
  - Eli (Navigator)
  - Claude Opus 5.5 (Driver)
related:
  - CV3.DS2.US2
---

# Batimento no Placar do Relógio pelo MeasureClient

## Question

Como mostrar a frequência cardíaca no placar sem interromper o treino que o Samsung Health está gravando?

## Decision

- Ler `HEART_RATE_BPM` pelo `MeasureClient` do Health Services, só enquanto o placar está visível.
- Permissão pedida uma vez; negada, o placar fica como era.
- O valor fica só no relógio: não vai ao servidor nem aos espectadores.

## Rationale

- O `ExerciseClient` permite um só exercício ativo no aparelho: iniciar um encerraria o treino do Samsung Health.
- O `MeasureClient` roda em paralelo; o teste físico no Galaxy Watch 8 confirmou.

## Options Considered

- `ExerciseClient`: encerra o treino do Samsung Health.
- Samsung Health Sensor SDK: exige aprovação de parceiro.
- Ler a notificação do treino: frágil e pede acesso a notificações.
- Duração, calorias e zonas do Samsung Health: não legíveis por outros apps.

## Consequences

- Sensor ligado com o placar aberto: gasto de bateria somado à tela acesa, ainda não medido.
- Só `BODY_SENSORS` é pedido em tempo de execução; `READ_HEART_RATE` fica declarado no manifest.

## Review Trigger

Se o Wear OS deixar de aceitar `BODY_SENSORS`, ou se dados do treino passarem a ir ao site.
