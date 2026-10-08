---
code: CV8.DS7.TS3
level: Technical Story
status: Active
status_reason: implementando junto da US19 (mesma branch)
updated: 2026-10-08
related:
  - ../cv8-ds7-us19-retirar-jogador-no-meio-da-rodada/index.md
---

# Ajustes da fila: remover e pular time na derivação

## Intent

A condução (`app/conducao.py::derivar`) é uma função pura que **reconstrói** quem está em quadra, na fila e nos reis a partir da ordem do sorteio e dos resultados. Retirar o último jogador de um time (o time deixa de existir) e pular um time sem substituto mudam a fila **no meio da história**; se isso mudasse só o estado final, a reconstrução dos resultados já gravados falharia ("resultado de uma partida que não estava em quadra").

## Escopo

- Tabela `ajustes_fila` (schema 11, aditiva): `rodada_id`, `apos_partidas` (quantas partidas encerradas já existiam), `tipo` (`remover` | `pular`), `time_id`.
- `derivar(..., ajustes)`: aplica cada ajuste logo depois da partida de número `apos_partidas` (fila e mata-mata contadas juntas) e antes de encher a quadra de novo.
- Invariantes testadas: time removido não aparece em quadra, fila, reis, rivais, desafiante nem campeão; ninguém duplicado; sem ajustes o resultado é idêntico ao de hoje; desfazer a última partida continua coerente.

## Acceptance / Done Condition

Testes puros de `derivar` cobrem: remover time da fila, da quadra (vencedor que fica), rei e desafiante; pular time da fila, da quadra e rival do mata-mata; ajuste depois de partidas; e a mesma entrada sem ajustes dando a mesma saída de antes.
