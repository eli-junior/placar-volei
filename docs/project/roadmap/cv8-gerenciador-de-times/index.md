---
code: CV8
level: Value
status: Active
status_reason: DS1 a DS5 entregues até a 0.44.0 (validação em lote pendente); DS6 (trio) na 0.45.0; DS7 (auditoria do QA) entregue até a 0.48.0 (US21 adiada); validação em lote pendente
updated: 2026-10-09
related:
  - regras-de-negocio.md
---

# CV8 — Gerenciador de times (vôlei de areia)

## Intent

Conduzir o dia de jogo: cadastrar jogadores, abrir a sessão, sortear duplas equilibradas e tocar a rodada no formato rei da quadra até o campeão, com a fila e os reis visíveis a todos e os nomes das duplas no relógio.

## Escopo do MVP

Web + exibição dos nomes das duplas no relógio. Somente formato **dupla**. Regras de negócio e glossário: [regras-de-negocio.md](regras-de-negocio.md).

## Delivery Stories

- [CV8.DS1 — Cadastro e presença](cv8-ds1-cadastro-e-presenca/index.md): Base de jogadores e sessão do dia com presença marcada.
- [CV8.DS2 — Sorteio](cv8-ds2-sorteio/index.md): Sorteio das duplas da primeira rodada e das seguintes, com reequilíbrio.
- [CV8.DS3 — Condução da rodada](cv8-ds3-conducao-da-rodada/index.md): Fila, partidas, rei da quadra, desfazer, time incompleto, atrasados e substituição.
- [CV8.DS4 — Fechamento](cv8-ds4-fechamento/index.md): Mata-mata, campeão e persistência da sessão.
- [CV8.DS5 — Exibição](cv8-ds5-exibicao/index.md): Fila e reis para o espectador e nomes das duplas no relógio.
- [CV8.DS6 — Formato trio](cv8-ds6-formato-trio/index.md): Rodada inteira em trios (RN-16).
- [CV8.DS7 — Joguinho sem becos sem saída](cv8-ds7-joguinho-sem-becos/index.md): Correções da auditoria do QA de 2026-10-08 (anular partida, quadra que some, segredo, rotas, retirar jogador).

- [CV8.DS8 — Formatos de rodada](cv8-ds8-formatos-de-rodada/index.md): Formatos que fogem do rei da quadra; US22, rodada triangular de 3 times (RN-18).

- [CV8.TS1 — Backup do `gerenciador.db`](cv8-ts1-backup-do-gerenciador/index.md): resiliência da base durável (Technical Story).

## Acceptance / Done Condition

Com 4 ou mais presentes, o operador sorteia, conduz as partidas até o mata-mata e fecha a rodada com um campeão; sorteia a rodada seguinte reequilibrada pelo saldo; tudo sobrevive a reinício do servidor; espectadores e relógio veem fila, reis e nomes.

## Fora do escopo (fase 2)

- Tela de histórico / ranking geral entre sessões.
- Edição de partidas antigas (além de desfazer a última).

## Notes

Fonte: especificação "Gerenciador de Times" e decisões de refinamento de 2026-10-07. Estado inicial: `Planned`. Sequência e dependências a definir no plano ao puxar a primeira história.

## Estado em 0.44.0

Todas as Delivery Stories (DS1 a DS5) e a CV8.TS1 estão entregues e na `master`; falta a validação do Navigator em lote (guias em cada `test-guide.md`). O que ficou fora, por decisão da especificação: formato trio, histórico/ranking entre sessões e edição de partidas antigas (fase 2); nenhuma dessas tem regra de negócio fechada ainda.

## Estado em 0.45.0

O formato trio (CV8.DS6.US15) está entregue: rodada inteira em trios, mistos, com a sobra escolhendo parceiros (RN-16). Continuam fora: histórico/ranking entre sessões e edição de partidas antigas.

## Estado em 0.46.2

A auditoria do QA em produção (2026-10-08, `docs/qa/`) virou a CV8.DS7. A US16 (anular partida chamada) está entregue; TS2, US17 a US20 estão planejadas e a US21 adiada.

## Estado em 0.48.0

A DS7 está fechada: anular partida chamada, quadra que não some no meio da rodada, segredo do dono preservado, rota `/joguinho`, joguinho de outro dia e retirar jogador no meio da rodada. Fica adiada só a US21 (placar manual ou W.O.). Continuam pendentes a validação do Navigator em lote das DS1 a DS6 e o teste dos nomes das duplas no relógio físico; histórico/ranking entre sessões e edição de partidas antigas seguem fora (fase 2).

## Estado em 0.49.0

A DS8 (formatos de rodada) abriu com a US22: com exatamente 3 times completos a rodada é triangular (RN-18) e só é rei quem vence os outros dois; qualquer outro desfecho encerra sem campeão. O gerenciador passou ao schema 12.
