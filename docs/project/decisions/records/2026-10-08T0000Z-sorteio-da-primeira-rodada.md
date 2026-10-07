---
id: sorteio-da-primeira-rodada
status: Decided
raised: 2026-10-07
decided: 2026-10-07
deciders:
  - Eli (Navigator)
  - Claude Sonnet 5.5 (Driver)
related:
  - CV8.DS2.US3
  - sessao-unica-presenca-e-ordem-de-chegada
---

# Sorteio da Primeira Rodada

## Question

Como sortear duplas equilibradas pela nota, com o gênero prevalecendo, fila pela ordem de chegada e um "resortear" que faça sentido sem aleatoriedade?

## Decision

- **Ímpar:** o último a chegar fica sozinho num time incompleto, por último na fila (RN-05).
- **Gênero (RN-01):** o número de duplas H+H é o mínimo possível, `max(0, (H − M) / 2)` entre os que formam dupla; M+M é livre. O gênero prevalece sobre o equilíbrio.
- **Equilíbrio (RN-14):** módulo puro `app/sorteio.py`, determinístico. Parte de um pareamento já com o número certo de duplas H+H (serpentina por nota) e melhora por **trocas de jogadores entre duplas** que preservam esse número, minimizando a soma dos quadrados das somas das duplas. É **heurístico**: conferido contra força bruta até 10 jogadores, sem prova para mais.
- **Fila (RN-13):** times completos ordenados pela menor ordem de chegada; o incompleto por último. Os dois primeiros jogam a primeira partida.
- **Resortear:** percorre as combinações com amplitude até **3 pontos** pior que a melhor, em ordem determinística, e volta ao início ao esgotá-las. Se só há uma, o botão fica desabilitado.
- **Proposta persistida** (schema 4: `rodadas`, `times`, `time_jogadores`), com a nota e a chegada usadas gravadas. Uma rodada ativa por sessão, garantida por índice no banco.
- **Presença travada** durante a proposta e a rodada em andamento (RN-15); inativar quem está na rodada é recusado; encerrar a sessão exige cancelar antes.
- **Extras necessários:** *Descartar* a proposta e *Cancelar* a rodada, para a sessão nunca ficar presa antes de a DS3 permitir jogar.
- **Alvo** 10 ou 12 escolhido antes do sorteio (padrão 10); trocar exige descartar e sortear de novo na tela.

## Rationale

- Combinação-base determinística atende "equilibrar sem ser aleatório" (Navigator); o resortear percorre alternativas equivalentes em vez de embaralhar.
- Garantir o gênero por construção (e nunca violá-lo nas trocas) torna a RN-01 uma invariante, não uma preferência da busca.
- Persistir a proposta permite que outro aparelho a veja e sobrevive a reinício.

## Options Considered

- Busca exata por enumeração: explode com 20+ jogadores e não gera variantes naturais.
- Sorteio aleatório: contraria a RN-14.
- Resortear refazendo a serpentina: daria sempre o mesmo resultado.
- Escolher o ímpar pela nota ou aleatoriamente: premia/pune sem relação com a chegada.
