---
code: CV1.DS4.US1
level: User Story
status: Planned
status_reason:
updated: 2026-09-13
related:
  - 2026-09-13T1400Z-log-de-eventos-como-fonte-da-verdade
---

# CV1.DS4.US1 — Linha do tempo da partida

## Intent

Ver como o placar foi construído, ponto a ponto.

## Scope

Botão na tela do placar que abre a linha do tempo da partida corrente, listando os eventos em ordem cronológica com placar resultante, tipo de evento, time, autor e horário. Atualiza em tempo real enquanto aberta.

## Acceptance / Done Condition

Given uma partida com oito pontos marcados, dois desfeitos e uma mudança de regra
When um participante abre a linha do tempo
Then vê os onze registros em ordem, cada ponto com o placar resultante e o apelido de quem marcou
And os pontos desfeitos aparecem identificados como anulados, não sumidos da lista
And um novo ponto marcado por outra pessoa entra na linha do tempo com transição de entrada, sem recarregar
And um espectador consegue abrir a linha do tempo do mesmo jeito que um controlador.

## Validation Route

Duas telas: uma na linha do tempo aberta, outra marcando pontos e desfazendo. Conferir a atualização ao vivo e o cotejo com a tabela de eventos no SQLite.

## Out of Scope

Partidas arquivadas, exportação, filtro por participante.

## Notes

A linha do tempo é leitura direta da projeção; não deve existir consulta paralela ao estado que possa divergir do log.
