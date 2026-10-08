---
code: CV8.DS7.US19
level: User Story
status: Planned
status_reason: depende da decisão C (ver DS7)
updated: 2026-10-08
---

# Retirar jogador no meio da rodada

## Intent

**Como** operador, **quero** tirar da rodada um jogador que foi embora, **para** que ele não seja escalado de novo, sem cancelar a rodada (QA F2).

## Hoje

Presença travada com rodada ativa; inativar é recusado; a substituição (US10) exige substituto vindo da fila ou dos eliminados e é recusada com partida chamada. Sem substituto disponível não há saída além de cancelar a rodada.

## Acceptance (rascunho, a fechar com a decisão C)

- **Dado** uma rodada em andamento sem partida chamada **quando** o operador retira um jogador **então** ele vira ausente; se estava num time, o time usa substituto quando houver ou segue incompleto (escolhe parceiro na vez, como a US8).
- **Dado** uma partida chamada com o jogador em quadra **então** o que acontece é decisão de produto (cenário 4 do QA).
- **E** os botões "Desmarcar" travados dizem o motivo ao lado, não só no fim da página.

## Decisão C

Substituto obrigatório, ou o time pode seguir incompleto?
