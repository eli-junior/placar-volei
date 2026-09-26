---
code: CV3.DS2.US3
level: User Story
status: Done
status_reason: Entregue na 0.12.0; teste físico no Galaxy Watch 8 aprovado em 2026-09-26
updated: 2026-09-26
related:
  - CV3.DS1.US3
  - nova-partida-pelo-relogio-de-admin
---

# CV3.DS2.US3 — Nova partida rápida pelo relógio

## Intent
Como Eli, ao fim da partida, quero começar a próxima pelo relógio com um toque, com os mesmos times e as mesmas regras, sem pegar o telefone.

## Scope
- Com a partida encerrada, a faixa inferior do placar se divide em **↶ Desfazer** e **▶ Nova**.
- Um toque em **▶ Nova** começa uma partida nova em 0 × 0, com os mesmos times, jogadores, alvo, vantagem e teto.

## Acceptance / Done Condition
Ver [plano](plan.md).

## Out of Scope
Mudar times ou regras pelo relógio; nova partida com a partida em andamento.

## Notes
- [Plano](plan.md).
- Risco conhecido: recusa da nova partida não mostra aviso no relógio; o placar só fica na partida encerrada.
- `pode_nova_partida` é lido ao entrar na quadra; se o papel do dono mudar, o servidor recusa e o botão não tem efeito.
