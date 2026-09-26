---
code: CV3.DS2.US2
level: User Story
status: Planned
status_reason: Navigator pediu frequência cardíaca e a duração do exercício do Samsung Health; a duração depende de viabilidade técnica
updated: 2026-09-26
related:
  - CV3.DS2.US1
---

# CV3.DS2.US2 — Dados do treino no placar

## Intent
Como Eli, quero ver no placar do relógio os dados do treino que o Samsung Health está gravando, sem sair do placar e sem interromper a gravação.

## Scope (proposto)
- Frequência cardíaca ao vivo no topo do placar, lida do sensor pelo `MeasureClient` do Health Services, só com o placar visível.
- Duração do exercício do Samsung Health: pedido do Navigator em 2026-09-26. O Samsung Health não expõe o treino em andamento a outros apps; alternativas em avaliação no Checkpoint 1 desta HU.
- A frequência cardíaca não sai do relógio (nem servidor, nem espectadores).

## Acceptance / Done Condition (proposta)
- Dado um treino de Vôlei ativo no Samsung Health e o placar aberto, então a frequência aparece no placar e o Samsung Health continua gravando.
- Sem permissão de sensor, nada aparece e o placar funciona igual; sem leitura, "♥ --".

## Risks
- Paralelismo do `MeasureClient` com o treino do Samsung Health: previsto pela documentação, não provado no Watch 8. Primeira tarefa: APK mínimo de prova no aparelho.
- `ExerciseClient` (o placar gravar o próprio treino) encerraria o treino do Samsung Health: rejeitado.
- Samsung Health Sensor SDK exige aprovação de parceiro da Samsung: rejeitado.

## Out of Scope
Calorias e zonas do Samsung Health, dados do treino no site, envio em segundo plano (CV3.DS1.US4).
