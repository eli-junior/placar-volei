---
code: CV6
level: Value
status: Active
status_reason: CV6.DS1 entregue; CV6.DS2.US1–US3 entregues; próxima US4, repouso e retomada
updated: 2026-09-28
---

# CV6 — Ajustes de uso em quadra

## Intent

Consolidar a rodada de feedback de 27/09/2026 em nove HUs para desenvolvimento posterior. Escopo documental; nenhuma implementação autorizada por este registro. Organização em CV/DS proposta para revisão do Navigator.

## Entregas

- [CV6.DS1 — Placar web](cv6-ds1-placar-web/index.md): seis HUs (US6 acrescentada após a 0.21.0).
- [CV6.DS2 — Placar no relógio](cv6-ds2-placar-no-relogio/index.md): quatro HUs.

## Acceptance / Done Condition

Todas as HUs aceitas individualmente pelo Navigator em aparelhos reais. Os estados de execução pertencem a cada história. Versão futura a definir no planejamento; esta consolidação não altera a versão do produto nem a prioridade atual do roadmap.

## Referências e rastreabilidade

Feedbacks e cinco imagens fornecidos pelo Navigator nesta conversa:

- Captura de tela 2026-09-27 134614.png: tablet escuro; DS1.US1–US4.
- Screenshot_20260927_134243_Chrome.jpg: Fold aberto claro; DS1.US1–US4.
- Screenshot_20260927_140703_Chrome.jpg: Fold fechado claro; DS1.US1–US4.
- Screenshot_20260927_134303_Chrome.jpg: ajustes; DS1.US5.
- 20260927_135541.jpg: relógio; DS2.US1–US3.
- Feedback textual posterior: repouso/retomada (DS2.US4), aro (DS2.US2) e batimentos centralizados (DS2.US1).

As imagens permanecem anexadas à conversa original; não dependem de caminhos temporários para definir os critérios escritos. Fonte e retorno de pontuação foram entregues; continuidade em repouso permanece para a US4.

## Validação comum

Web: tablet, Fold aberto e fechado/celular; temas claro/escuro; estilos esportivo/clássico quando pertinentes; retrato/paisagem, zoom, teclado e movimento reduzido. Validar com dois clientes simultâneos; três quando envolver presença/papéis. Relógio: aparelho real e telefone na mesma quadra, incluindo treino ativo quando pertinente. Cada HU traz seu roteiro e condições de aprovação/falha.

## Coerência e limites

- CV4 permanece concluído: esta rodada trata de melhorias posteriores observadas em uso.
- DS2.US4 revisita explicitamente a decisão de manter a tela acesa em CV3.DS2.US1; não modifica retroativamente o aceite anterior.
- README e briefing atualizados no fechamento da US3: Wear 0.24.1, backend/web 0.24.0; foco seguinte na US4.
- O guia menciona restaurar estado após restart, mas também documenta reset intencional do banco em produção. Os testes destas HUs devem distinguir repouso/reconexão do relógio de reinício destrutivo do servidor.
- Não inclui novas regras esportivas, redesenho de permissões ou infraestrutura. Pendências de produto estão nas respectivas HUs.
