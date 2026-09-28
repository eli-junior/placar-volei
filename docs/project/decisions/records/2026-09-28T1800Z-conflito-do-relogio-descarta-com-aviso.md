---
status: Decided
raised: 2026-09-28
decided: 2026-09-28
deciders:
  - Eli (Navigator)
  - Claude Code (Driver)
related:
  - CV3.DS1.US4
  - 2026-09-27T0200Z-fila-offline-aceita-devolucao-de-controle
---

# Conflito da fila do relógio descarta com aviso, sem revisão no telefone

## Decision

Quando a fila offline do relógio entra em conflito (controle com outra pessoa, partida nova, placar mudado por fora ou vínculo encerrado), o relógio descarta a fila inteira, mostra por 3 s "N lances não enviados · motivo" e volta ao placar do servidor. Não há revisão pelo telefone.

Substitui a regra aprovada em 2026-09-22: "conflito pausa a sincronização, preserva lances e permite revisão explícita pelo telefone".

## Rationale

Se o controle saiu do relógio, quem assumiu já está marcando o placar real: não há conflito a arbitrar. Uma tela de revisão seria rara, cara (API, painel no telefone, relógio obedecendo) e deixaria o relógio travado até alguém decidir.

## Options Considered

- Revisão pelo telefone (reaplicar ou descartar, listando os lances): plano original, rejeitado.
- Descartar só na perda de controle e revisar os demais casos: rejeitado pela mesma razão.
- Descartar sem aviso: rejeitado; o aviso diz que os toques do pulso não entraram.

## Consequences

O relógio sempre converge para o servidor. A devolução de controle sem lances de outros no meio continua aceitando a fila (decisão de 2026-09-27). Recusas passageiras (408/425/429) continuam segurando o lance.

## Review Trigger

Se, em jogo, o Navigator perder pontos legítimos com frequência por esse descarte.
