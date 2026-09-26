---
id: tela-acesa-no-placar-do-relogio
status: Decided
raised: 2026-09-26
decided: 2026-09-26
deciders:
  - Eli (Navigator)
  - Claude Opus 5.5 (Driver)
supersedes: decisão 3 do plano CV3.DS1 ("não manter tela permanentemente acesa por padrão")
related:
  - CV3.DS2.US1
---

# Tela Acesa Enquanto o Placar do Relógio Está Visível

## Question

O plano do CV3.DS1 decidiu não manter a tela do relógio acesa por padrão, para poupar bateria. No uso real, a tela apagava no meio do jogo e o primeiro toque só acordava o relógio. Manter a tela acesa?

## Decision

- O placar liga `keepScreenOn` na própria view enquanto está visível (`DisposableEffect` em `ScoreScreen`) e desliga ao sair.
- Telas de vínculo e de escolha seguem o tempo normal de tela.
- Cobrir com a palma continua apagando: é gesto do sistema e fica aceito.

## Rationale

- Durante a partida o toque precisa estar pronto; perder o primeiro toque atrapalha mais que o gasto de bateria de 1 h de tela.
- A regra fica no placar: a flag some junto com a tela, sem estado espalhado pela atividade.

## Options Considered

- Modo ambiente (tela escurece e mostra o placar): exige um toque extra para acordar antes de marcar. Não escolhido pelo Navigator.
- Tela acesa mais ambiente como reserva: não pedido.
- Ligar a flag no `MainActivity` pelo estágio: espalha a regra.

## Consequences

- Gasto de bateria maior com o placar aberto. Medição adiada pelo Navigator.
- Com a tela sempre acesa, o placar fica em primeiro plano durante o treino do Samsung Health (CV3.DS2.US2).

## Review Trigger

Se a bateria não aguentar uma pelada inteira, ou se o modo ambiente entrar no escopo.
