---
code: CV4
level: Value
status: Active
status_reason: CV4.DS1 concluída e aprovada; CV4.DS2 é a próxima frente planejada
updated: 2026-09-26
---

# CV4 — Painel esportivo e leitura em qualquer tela

## Intent

Dar prioridade à leitura do placar e à operação na quadra, com uma identidade esportiva consistente do início ao acompanhamento. Atender telefone na mão, Fold aberto/fechado e tablet apoiado, nos temas claro e escuro.

## Leitura para começar ou retomar

1. [Plano detalhado e esforço por tarefa](plan.md).
2. [Handoff e estado de autorização](handoff.md).
3. [Rota de validação](test-guide.md).
4. [Decisão visual aprovada](../../decisions/records/2026-09-26T1238Z-painel-esportivo-e-numeros-prioritarios.md).
5. [Referências visuais e limites dos protótipos](references/README.md).

## Delivery Stories

- [CV4.DS1 — Início e entrada na quadra](cv4-ds1-inicio/index.md).
- [CV4.DS2 — Acompanhamento e imersão](cv4-ds2-acompanhamento/index.md).
- [CV4.DS3 — Operação e consistência](cv4-ds3-operacao/index.md).

Os estados de execução pertencem aos arquivos de cada história. As dependências e estimativas estão no plano; este índice não mantém outra tabela de andamento.

## Acceptance / Done Condition

- Home utilizável no Fold fechado e aberto, com entrada por código e criação de quadra preservadas.
- Pontos são a informação dominante; identificação da sala e regras permanecem secundárias.
- Abrir, fechar ou girar o Fold preserva sala, sessão, tema, lado local e placar.
- Imersão oculta controles sem deslocar os números. Tela cheia real é solicitada por toque e falhas têm alternativa utilizável.
- Admin/controlador marcam e desfazem com um toque; espectador não recebe comandos de pontuação.
- Temas, teclado, movimento reduzido, zoom e leitura em aparelhos reais validados.
- Cada história aceita individualmente pelo Navigator, com documentação, revisão de dívida e histórico remoto.

## Out of Scope

Novas regras esportivas, novas permissões, alterações do protocolo de eventos, evolução do app Wear OS, analytics, autenticação, um terceiro tema e uma reformulação de infraestrutura.
