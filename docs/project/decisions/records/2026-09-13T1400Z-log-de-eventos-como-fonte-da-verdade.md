---
status: Decided
raised: 2026-09-13
decided: 2026-09-13
deciders:
  - Navigator
supersedes:
related:
  - CV1.DS1
  - CV1.DS4
---

# Log de eventos append-only como fonte da verdade do placar

## Question

O placar deve ser um contador mutável no banco, ou uma projeção de um log de eventos imutável?

## Decision

O placar é uma **projeção** de um log de eventos append-only. Nenhum contador de pontos é atualizado diretamente.

Eventos previstos no MVP: `PONTO_MARCADO`, `PONTO_DESFEITO`, `REGRA_ALTERADA`, `PARTIDA_ENCERRADA`, `PARTIDA_INICIADA`, `PAPEL_ALTERADO`, `ADMIN_SUCEDIDO`, `ADMIN_ASSUMIDO`.

Cada evento carrega: id, quadra, partida, tipo, payload, autor (participante), timestamp UTC e sequência monotônica dentro da partida.

## Rationale

Três requisitos do MVP dependem disso e nenhum deles é satisfeito por um contador:

1. Desfazer ponto a ponto, sem limite, até zerar.
2. Linha do tempo mostrando como o placar foi construído.
3. Sobrevivência a restart do processo, reconstruindo o estado do disco.

O custo é baixo nesta escala — dezenas de eventos por partida — e o modelo elimina a classe inteira de bugs de contador dessincronizado entre clientes.

## Options Considered

- **Contador mutável + tabela de auditoria paralela** — rejeitado: dois lugares para a mesma verdade divergem, e a auditoria vira opcional na prática.
- **Log em memória com snapshot periódico** — rejeitado: complexidade de snapshot sem ganho de desempenho relevante nesta escala.

## Consequences

- Desfazer **não apaga** o evento anulado; grava `PONTO_DESFEITO` referenciando-o.
- Toda mutação de estado passa obrigatoriamente pelo append no log. Código que altere estado sem gravar evento é bug, mesmo que a tela fique correta.
- A projeção precisa ser determinística e reproduzível a partir do log.
- Snapshot/compactação fica fora do escopo até que o volume justifique.

## Review Trigger

Se uma partida passar a acumular eventos suficientes para tornar a reconstrução perceptível ao usuário (ordem de milhares), reavaliar snapshot periódico.
