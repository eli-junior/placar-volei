---
code: CV6.DS1.US9
level: User Story
status: Done
status_reason: validado no celular pelo Navigator em 2026-09-30; entregue na 0.26.0, destaque permanente e faixa maior na 0.26.1
updated: 2026-10-01
---

# CV6.DS1.US9 — Destaque do último ponto e sequência de pontos

## Intent

Quem olha o placar na web sabe na hora quem fez o último ponto e vê o histórico da partida sem abrir a linha do tempo — o relógio já mostrava isso com uma bolinha.

## Scope

- O número da equipe do último ponto ativo cresce (~9%) e acende na cor dela; o outro fica apagado. Um pulso de 0,6 s a cada ponto marcado; nenhum no desfazer; sem animação com movimento reduzido. Temas esportivo e clássico.
- Faixa de bolinhas sob o placar (`SequenciaPontos.svelte`), uma por ponto ativo da partida atual, nas cores das equipes (A ciano, B laranja), a mais recente à direita com anel.
- Operador e espectador. Deriva da linha do tempo já projetada (`sequenciaDePontos` em `lib/controle.js`); sem mudança de backend ou protocolo.

## Acceptance / Done Condition

Given uma partida em andamento com operador e espectador conectados
When A marca um ponto e B marca dois
Then as duas telas mostram ciano, laranja, laranja na faixa
And o número de B aparece maior e aceso, pulsando a cada ponto
And ao desfazer, a última bolinha some e o destaque volta a quem fez o ponto anterior

## Validation Route

`web/tests/controle.test.js` (sequência), `web/e2e/sequencia.spec.js` (dois clientes, desfazer); Navigator validou no celular.

## Out of Scope

Relógio (Wear); estatísticas de sequência; tocar numa bolinha para abrir o lance.
