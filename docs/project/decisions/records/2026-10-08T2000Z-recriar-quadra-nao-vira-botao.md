---
id: recriar-quadra-nao-vira-botao
status: Decided
raised: 2026-10-08
decided: 2026-10-08
deciders:
  - Eli (Navigator)
  - Claude Sonnet 5.5 (Driver)
related:
  - CV8.DS7.US20
  - quadra-da-rodada-renovada-pelo-servidor
  - docs/qa/2026-10-08-furos-de-logica-joguinho.md
---

# Recriar a quadra com as mesmas duplas não vira botão

## Question

O QA (F3) esperava que, ao detectar a quadra indisponível, o Joguinho oferecesse **recriar a quadra com as mesmas duplas** ou anular a chamada. Vale construir a recriação?

## Decision

Não, por ora. A saída é **Anular partida** (US16): os dois times voltam a ser a próxima partida e, com **Criar quadra e vincular** seguido de **Chamar partida**, a quadra nasce de novo com as mesmas duplas. São dois toques, sem tela nova, e já funcionam com o que existe.

## Rationale

A decisão B (2026-10-08) escolheu reconciliar e anular, mantendo o banco das quadras efêmero. Um botão "Anular e criar nova quadra" seria só atalho sobre essa sequência. Se o operador reclamar dos dois toques, o atalho vira uma história própria, sem rever nada do que foi decidido.

## Consequences

- O placar da quadra perdida não volta: a partida chamada é anulada e o placar novo começa zerado.
- Revisitar se o uso real mostrar que reiniciar o contêiner no meio da rodada é frequente.
