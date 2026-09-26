---
code: CV3.DS1.TS1
level: Technical Story
status: Planned
status_reason: criada pela divisão da CV3.DS1.US4 aprovada em 2026-09-26
updated: 2026-09-26
---

# CV3.DS1.TS1 — Fila offline e reenvio sem duplicar

## Intent

Base técnica para a CV3.DS1.US4: o relógio registra toques sem conexão e os entrega depois exatamente uma vez.

## Scope

- Separar o `WatchModel` em vínculo × placar/fila (recomendação do handoff) e criar `conftest` comum aos testes do relógio.
- Fila persistente no relógio com ID único por comando, sala, partida, ordem e versão/base de estado; sobrevive ao reinício do app.
- Placar previsto local e contagem de pendentes, distintos do estado confirmado.
- Reenvio idempotente sobre `watch_recibos` (`device_id`, `comando_id`): resposta perdida após gravar recupera o resultado original.
- Sem snapshot inicial não há partida offline; fila de outra partida nunca é aplicada à nova.
- Devolução automática de controle ao relógio aceita com token válido (decisão do Navigator).

## Acceptance / Done Condition

Given sala vinculada com snapshot local; When o relógio perde conexão e marca A, B, A e desfaz; Then a projeção local soma 1 para A e 1 para B e a fila sobrevive ao reinício; And ao reconectar sem conflito cada comando produz no máximo um efeito, inclusive quando a resposta do servidor se perdeu.

## Validation Route

Testes do servidor para reenvio idempotente e partida trocada; testes do `WatchModel` com servidor falso; relógio físico em modo avião por 30 s, reinício do app e do backend após confirmação.

## Out of Scope

Detecção e revisão de conflitos pelo telefone (CV3.DS1.US4). Sincronização offline entre múltiplos operadores.
