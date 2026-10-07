---
status: Accepted
date: 2026-10-07
related:
  - CV8.DS2.US4
---

# Reequilíbrio entre rodadas

## Decisão

- Da rodada 2 em diante o sorteio usa a nota efetiva da RN-14, calculada só com partidas de rodadas **encerradas** (com campeão) da sessão. Rodada cancelada não conta, nem para o saldo nem para as duplas anteriores, e não bloqueia um novo sorteio.
- A ordem de chegada ordena a fila em todas as rodadas; o ímpar continua sendo o último a chegar (RN-05, RN-13).
- Evitar dupla repetida é só desempate entre combinações equivalentes (amplitude até `TOLERANCIA`), abaixo do gênero e do equilíbrio.
- A nota efetiva fica gravada em `time_jogadores.nota` (sem schema novo); a cadastrada é lida de `jogadores.nota` como `nota_base`.

## Alternativas rejeitadas

- Bloquear o sorteio após rodada cancelada: travaria a sessão, já que só há uma rodada ativa por vez.
- Repetição como peso no objetivo: poderia piorar o equilíbrio além da tolerância.

## Consequências

O cálculo mora em `app/reequilibrio.py`. Resultado determinístico e reproduzível.
