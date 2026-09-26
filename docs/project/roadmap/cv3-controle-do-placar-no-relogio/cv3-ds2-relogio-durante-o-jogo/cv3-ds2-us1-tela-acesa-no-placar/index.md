---
code: CV3.DS2.US1
level: User Story
status: Done
status_reason: Validada no Galaxy Watch 8 pelo Navigator (2026-09-26); entregue na 0.10.1
updated: 2026-09-26
related:
  - tela-acesa-no-placar-do-relogio
---

# CV3.DS2.US1 — Tela acesa no placar do relógio

## Intent
Como Eli, quero que a tela do relógio não apague enquanto uso o placar, para marcar o ponto com um toque sem antes acordar o relógio.

## Scope
- O placar liga `keepScreenOn` enquanto está visível e desliga ao sair.
- Telas de vínculo e de escolha (**Retornar** / **Parear outra quadra**) seguem o tempo normal de tela.

## Acceptance / Done Condition
- Dado o relógio no placar, quando passam 3 minutos sem toque, então a tela continua acesa no brilho normal e o primeiro toque marca o ponto.
- Quando o pulso abaixa e levanta, então o placar continua aceso.
- Quando sai para a tela de escolha, então a tela apaga no tempo normal.
- Cobrir com a palma apaga (gesto do sistema, aceito).

## Validation Route
[Roteiro](test-guide.md).

## Out of Scope
Modo ambiente, medição formal de bateria, envio em segundo plano (CV3.DS1.US4).

## Notes
- Substitui a decisão 3 do [plano do DS1](../../cv3-ds1-controle-pessoal-no-watch/plan.md) ("não manter tela permanentemente acesa por padrão"). Ver `tela-acesa-no-placar-do-relogio`.
- **Em aberto:** medir o gasto de bateria numa partida de 1 h com o placar aceso. O Navigator validou o comportamento e adiou a medição.
