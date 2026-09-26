---
code: CV3.DS1.US4
level: User Story
status: Active
status_reason: CV3.DS1.TS1 entregue na 0.19.0; falta a revisão de conflito pelo telefone
updated: 2026-09-26
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
- Regra aprovada: conflito pausa sincronização, preserva lances e permite revisão explícita pelo telefone antes de reaplicar ou descartar. Confirmação de descarte deve deixar claro quais lances serão abandonados.
- Devolução automática de controle sem alteração da partida deve ter tratamento explícito: recuperar autorização válida antes de retomar; nunca ignorar revogação.
- Sem snapshot inicial não é possível começar uma partida offline; nenhuma fila antiga é aplicada a uma partida nova.

## Validation Route
Watch e dois clientes web: modo avião por 30 s, sequência acima, reiniciar app e reconectar; conferir estado e histórico. Repetir com outro operador pontuando, troca de partida e revogação. Reiniciar backend após confirmação e verificar idempotência de reenvio.

## Estado para retomada

- Branch de implementação: `feature/cv3-ds1-us4-offline-reconciliacao`, criada de `master` `446282c`.
- Checkpoint 1 aprovado em 2026-09-26 (divisão em TS1 + US4).
- Base técnica entregue pela [CV3.DS1.TS1](../cv3-ds1-ts1-fila-offline-e-reenvio/index.md) na 0.19.0: placar persistido, `base_seq` e `ScoreSync`. Lances recusados continuam retidos no relógio (`held`) com descarte explícito; é daí que parte a revisão pelo telefone.
- Próximo passo: planejar a detecção de conflito e a revisão explícita pelo telefone. Fora de escopo até aqui: envio com o app em segundo plano.

## Decisões do Navigator (2026-09-26)

- **Divisão aprovada.** A fila persistente no relógio, o reenvio idempotente e o placar previsto vão para a [CV3.DS1.TS1](../cv3-ds1-ts1-fila-offline-e-reenvio/index.md). Esta US fica com a detecção de conflito, a pausa da sincronização e a revisão explícita pelo telefone (reaplicar ou descartar, listando os lances).
- **Devolução automática de controle ao relógio:** basta um token de vínculo válido; não exige nova autorização explícita. Revogação continua nunca ignorada: token revogado ou expirado pausa a fila e cai na revisão.
