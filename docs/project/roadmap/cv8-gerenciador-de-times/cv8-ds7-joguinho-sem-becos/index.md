---
code: CV8.DS7
level: Delivery Story
status: Done
status_reason: US16, TS2, US17, US18, US20, TS3 e US19 validadas pelo Navigator (0.46.2 a 0.48.0); US21 adiada por decisão A; cenários de regressão conferidos em 2026-10-09
updated: 2026-10-09
related:
  - ../../../../qa/2026-10-08-auditoria-producao.md
  - ../../../../qa/2026-10-08-furos-de-logica-joguinho.md
---

# CV8.DS7 — Joguinho sem becos sem saída

## Intent

A auditoria do QA em produção (2026-10-08) achou estados do Joguinho dos quais nenhuma ação da tela leva a um estado válido: partida chamada numa quadra que sumiu, jogador que não pode sair, segredo perdido por engano. Princípio: **quem opera sempre consegue sair de qualquer estado**, sem precisar cancelar a rodada inteira.

## Histórias

| Código | História | Origem (QA) | Status |
|---|---|---|---|
| [US16](cv8-ds7-us16-anular-partida-chamada/index.md) | Anular partida chamada | P1, P6, F1, F4 | Done (0.46.2) |
| [TS2](cv8-ds7-ts2-quadra-do-joguinho-nao-some/index.md) | Quadra do joguinho não some no meio da rodada | P2, F3 | Done (0.46.3) |
| [US17](cv8-ds7-us17-segredo-nao-some-por-engano/index.md) | Segredo do dono não some por engano | P5, F5.2 | Done (0.46.4) |
| [US18](cv8-ds7-us18-rota-joguinho-e-pagina-nao-encontrada/index.md) | Rota `/joguinho` e página não encontrada | P3, P4 | Done (0.46.5) |
| [TS3](cv8-ds7-ts3-ajustes-da-fila/index.md) | Ajustes da fila: remover e pular time na derivação | base da F2 | Done (0.48.0) |
| [US19](cv8-ds7-us19-retirar-jogador-no-meio-da-rodada/index.md) | Retirar jogador no meio da rodada | F2 | Done (0.48.0) |
| [US20](cv8-ds7-us20-joguinho-velho-e-mensagens-de-saida/index.md) | Joguinho de ontem e mensagens que ensinam a saída | F1.5, F4, F5.1, F5.3 | Done (0.47.0) |
| [US21](cv8-ds7-us21-resultado-de-partida-abandonada/index.md) | Resultado de partida abandonada (placar manual ou W.O.) | F1.2, F1.3 | Deferred (decisão A) |

Ordem sugerida: US16 → TS2 → US17 → US18 → US20 → US19 → US21.

## Decisões de produto

- **A — Partida abandonada (2026-10-08, Navigator):** por ora só **anular** (US16). Placar manual ou W.O. ficam na US21, adiada.
- **B — Banco das quadras (2026-10-08, Navigator):** opção (a). O banco das quadras continua efêmero (a decisão de 2026-09-27 fica de pé); o joguinho se reconcilia com as quadras que existem e a quadra vinculada a uma rodada em andamento não expira por TTL (TS2).
- **C — Retirar jogador (2026-10-08, Navigator):** quem sai deixa a **vaga vazia** enquanto o time está na fila; o substituto só é **obrigatório na hora de entrar em quadra**. Time sem nenhum jogador **deixa de existir** (sai da fila). Em jogo não sai; rei segue a mesma regra; sem elegível, o time é pulado. Resolvido no plano da US19: *Retirar* e *Substituir* (US10) convivem; "pular" manda o time para o fim da fila. Detalhes na US19.

## Done Condition

Os cenários de regressão do relatório de furos (seção "Cenários de regressão sugeridos") passam, e nenhuma tela do Joguinho mostra uma instrução que a própria tela impede de cumprir.

## Fechamento (2026-10-09)

Conferência dos cenários de regressão do relatório de furos, por onde cada um é coberto:

| # | Cenário | Coberto por |
|---|---|---|
| 1 | Chamar partida, reiniciar, anular ou recriar a quadra sem cancelar a rodada | US16: `test_quadra_sumiu_anular_trocar_de_quadra_e_chamar_de_novo` e e2e "quadra some com partida chamada" |
| 2 | Partida com placar no meio: "encerrar sem placar" | US16 (decisão A): **anular** (`test_anular_jogo_parado_no_meio_nao_conta_e_nao_mexe_no_placar`). Placar manual ou W.O. ficam na US21 |
| 3 | Retirar jogador sem substituto, sem partida chamada | US19: `test_retirar_da_fila_deixa_a_vaga_e_o_jogador_ausente` e e2e "retirar da rodada: vaga aberta…" |
| 4 | Retirar jogador com partida chamada | US19 (decisão C): quem está em jogo não sai e a tela mostra o motivo (e2e "quem está em jogo não sai") |
| 5 | Cancelar rodada com partida chamada e vincular outra quadra | US16: `test_cancelar_com_partida_chamada_libera_o_vinculo` e `test_chamada_orfa_de_rodada_cancelada_nao_trava_o_vinculo` |
| 6 | Sessão do dia anterior: aviso e escolha | US20: e2e "joguinho de outro dia: aviso com continuar ou encerrar" |
| 7 | Quadra expirada por TTL no meio da rodada | TS2: a quadra vinculada a rodada em andamento é renovada pelo servidor |

Os cenários 2 (parcial) e 4 (em jogo) saem por decisão de produto, não por falta de teste. A DS7 fecha sem a US21; ela volta ao roadmap se o grupo precisar registrar placar de partida abandonada.
