---
code: CV6.DS1.US6
level: User Story
status: Done
status_reason: validado e aceito pelo Navigator em 2026-09-27; entregue na 0.22.0
updated: 2026-09-27
---

# CV6.DS1.US6 — Atalhos de ajuste no placar

## Intent

Quem controla a partida ajusta regras e jogadores tocando direto no que quer mudar, sem passar pelo modal completo do ⚙.

## Scope

- Resumo de regras do topo ("12 pontos · Vantagem") abre um modal só com Pontuação e Vantagem.
- Nome da equipe no placar (esportivo e clássico) abre um modal só com os dois jogadores daquela equipe.
- Tocar fora, Esc, X ou Cancelar fecha sem salvar.
- Mesma permissão do ⚙ (admin e controladores); espectador não tem atalho.

## Acceptance / Done Condition

Given sou admin numa sala
When toco em "12 pontos · Vantagem", escolho 15 e salvo
Then o topo mostra "15 pontos" em todos os clientes
When toco em "EQUIPE A" e salvo Ana / Bia
Then o placar mostra os nomes, e Equipe B e regras não mudam
And tocar fora do modal fecha sem salvar; o espectador não abre nada ao tocar no nome

## Design

`ModalConfigurarPartida` ganha a prop `secao` (`tudo`, `regras`, `equipe-a`, `equipe-b`). A seção curta só mostra uma parte, mas envia todos os campos atuais, então nada oculto é alterado. No esportivo o nome editável fica à frente do número, que o cobria.

## Validation Route

`web/e2e/atalhos.spec.js` (esportivo e clássico, dois clientes). Navigator validou em aparelho.

## Out of Scope

Nome de equipe independente dos jogadores; atalhos no modal de próxima partida.
