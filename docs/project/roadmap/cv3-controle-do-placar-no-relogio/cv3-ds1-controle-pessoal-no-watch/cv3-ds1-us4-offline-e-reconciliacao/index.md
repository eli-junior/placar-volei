---
code: CV3.DS1.US4
level: User Story
status: Planned
status_reason: Descoberta registrada; aguardando aceite do Checkpoint 1
updated: 2026-09-22
---

# CV3.DS1.US4 — Registrar offline e sincronizar com segurança

## Intent
Como Eli, quero continuar marcando sem conexão e sincronizar depois para não perder a contagem durante a partida.

## Scope
Fila persistente no relógio com ID único por comando, sala, partida, ordem, versão/base de estado e alvo de correção. Confirmações duráveis no servidor e reenvio idempotente. Placar local previsto e quantidade pendente distinguem-se do estado confirmado.

## Acceptance / Done Condition
- Dada uma sala vinculada com snapshot local, quando perder conexão e marcar A, B, A e desfazer, então a projeção local soma 1 para A e 1 para B e a fila sobrevive ao reinício do app.
- Quando reconectar sem conflito, então os comandos são reconciliados na ordem original e cada intenção produz no máximo um efeito.
- Se a resposta sumir após a gravação no servidor, o reenvio recupera o resultado sem duplicar o evento.
- Com mudança de partida, sala expirada, revogação, alteração de regras ou disputa de controle, não aplicar cegamente nem descartar silenciosamente a fila.
- Proposta pendente de aceite: conflito pausa sincronização, preserva lances e permite revisão explícita pelo telefone antes de reaplicar ou descartar. Confirmação de descarte deve deixar claro quais lances serão abandonados.
- Devolução automática de controle sem alteração da partida deve ter tratamento explícito: recuperar autorização válida antes de retomar; nunca ignorar revogação.
- Sem snapshot inicial não é possível começar uma partida offline; nenhuma fila antiga é aplicada a uma partida nova.

## Validation Route
Watch e dois clientes web: modo avião por 30 s, sequência acima, reiniciar app e reconectar; conferir estado e histórico. Repetir com outro operador pontuando, troca de partida e revogação. Reiniciar backend após confirmação e verificar idempotência de reenvio.
