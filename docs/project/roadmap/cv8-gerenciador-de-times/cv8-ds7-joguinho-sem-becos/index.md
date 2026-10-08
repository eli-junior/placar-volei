---
code: CV8.DS7
level: Delivery Story
status: Active
status_reason: US16 (0.46.2), TS2 (0.46.3) e US17 (0.46.4) validadas; próxima US18
updated: 2026-10-08
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
| [US18](cv8-ds7-us18-rota-joguinho-e-pagina-nao-encontrada/index.md) | Rota `/joguinho` e página não encontrada | P3, P4 | Planned |
| [US19](cv8-ds7-us19-retirar-jogador-no-meio-da-rodada/index.md) | Retirar jogador no meio da rodada | F2 | Planned |
| [US20](cv8-ds7-us20-joguinho-velho-e-mensagens-de-saida/index.md) | Joguinho de ontem e mensagens que ensinam a saída | F1.5, F4, F5.1, F5.3 | Planned |
| [US21](cv8-ds7-us21-resultado-de-partida-abandonada/index.md) | Resultado de partida abandonada (placar manual ou W.O.) | F1.2, F1.3 | Deferred (decisão A) |

Ordem sugerida: US16 → TS2 → US17 → US18 → US20 → US19 → US21.

## Decisões de produto

- **A — Partida abandonada (2026-10-08, Navigator):** por ora só **anular** (US16). Placar manual ou W.O. ficam na US21, adiada.
- **B — Banco das quadras (2026-10-08, Navigator):** opção (a). O banco das quadras continua efêmero (a decisão de 2026-09-27 fica de pé); o joguinho se reconcilia com as quadras que existem e a quadra vinculada a uma rodada em andamento não expira por TTL (TS2).
- **C — Retirar jogador (2026-10-08, Navigator):** quem sai deixa a **vaga vazia** enquanto o time está na fila; o substituto só é **obrigatório na hora de entrar em quadra**. Time sem nenhum jogador **deixa de existir** (sai da fila). Em jogo não sai; rei segue a mesma regra; sem elegível, o time é pulado. Em aberto: relação com a US10 (substituir). Detalhes na US19.

## Done Condition

Os cenários de regressão do relatório de furos (seção "Cenários de regressão sugeridos") passam, e nenhuma tela do Joguinho mostra uma instrução que a própria tela impede de cumprir.
