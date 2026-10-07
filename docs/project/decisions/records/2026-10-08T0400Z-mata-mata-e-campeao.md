---
id: mata-mata-e-campeao
status: Decided
raised: 2026-10-07
decided: 2026-10-07
deciders:
  - Eli (Navigator)
  - Claude Sonnet 5.5 (Driver)
related:
  - CV8.DS4.US11
  - escalacao-do-parceiro-do-incompleto
---

# Mata-mata e Campeão da Rodada

## Question

Como o mata-mata começa, quem joga contra quem e quando a rodada termina, inclusive quando a quadra esvazia no fim da fila (era o "em aberto" da RN-12)?

## Decision

- **Início manual:** no `fim_da_fila` o operador toca em **Iniciar mata-mata** (`POST /api/rodada/iniciar-mata-mata`); só então ninguém mais entra. Sem rivais o botão é **Coroar campeão**.
- **Desafiante:** o time que ficou sozinho na quadra; se a quadra esvaziou porque o último vencedor virou rei, é esse rei, que não entra na lista de rivais. Rivais = demais reis na ordem de coroação.
- **Partida única, ganhou ficou:** o vencedor segue contra o próximo rei; sem 2 vitórias virando rei. O último vencedor é o campeão.
- **Fluxo reaproveitado:** chamar/encerrar partida iguais às da fila; `partidas_rodada.fase` distingue as fases. Ao encerrar a última, a rodada vira `encerrada` com `campeao_time_id`, liberando o sorteio (o índice de rodada ativa só cobre proposta e em andamento).
- **Schema 7** (aditivo): `rodadas.mata_mata_em`, `rodadas.campeao_time_id`, `partidas_rodada.fase`. A derivação continua pura em `app/conducao.py`.

## Rationale

- O botão manual dá ao operador o controle do bloqueio de entradas (RN-04) e evita coroar sozinho por engano.
- Tratar o rei da quadra vazia como desafiante é a leitura direta de "vencedor da última partida" e não o faz jogar sem ter vencido por último.

## Consequences

Não há como desfazer partida do mata-mata nem a coroação até a US7. O painel mostra só o último campeão; histórico entre sessões é fase 2.

## Review Trigger

Quando a US7 (desfazer) ou a US12 (persistir sessão) tocarem no encerramento da rodada.
