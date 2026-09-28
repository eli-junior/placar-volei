---
code: CV3.DS1.US4
level: User Story
status: Done
status_reason: validada fisicamente pelo Navigator em 2026-09-28; fechada na 0.24.0
updated: 2026-09-28
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
- ~~Regra aprovada: conflito pausa sincronização e permite revisão pelo telefone.~~ Substituída em 2026-09-28: conflito descarta a fila com aviso de 3 s ([decisão](../../../../decisions/records/2026-09-28T1800Z-conflito-do-relogio-descarta-com-aviso.md)).
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

## Entrega (0.24.0)

- Opção simples do Navigator (2026-09-28): controle com outra pessoa, partida nova, placar mudado por fora ou vínculo encerrado descartam a fila inteira. O relógio mostra por 3 s "N lances não enviados · motivo" e volta ao placar do servidor. Sem revisão pelo telefone e sem mudança no servidor.
- A tela de lances retidos com **Descartar** saiu; filas pausadas por versões anteriores são descartadas ao abrir.
- Testes: 56 no relógio (6 novos de descarte). Validação física aprovada pelo Navigator. Ver [plano](plan.md).
- Nota: o relógio distingue "nova partida" de "placar mudou" pelo texto da recusa; revisar se o servidor passar a mandar código de motivo.
