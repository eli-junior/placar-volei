---
status: Decided
raised: 2026-09-28
decided: 2026-09-28
deciders:
  - Eli (Navigator)
  - Claude Code (Driver)
related:
  - CV6.DS1.US7
  - CV6.DS1.US8
---

# Padrão de 10 pontos e liberação imediata da quadra

## Decision

Quadras novas valem 10 pontos com vantagem de 2. O alvo se ajusta por slider de 6 a 20, ou por número livre de 1 a 100 em Personalizado. Só o admin libera a quadra; a liberação apaga tudo na hora, sem histórico, e derruba todos os aparelhos conectados.

## Rationale

10 é o alvo mais usado nas partidas do grupo; o slider cobre a faixa real e o Personalizado cobre o resto. Liberar reaproveita a rotina da expiração, então não existe um segundo jeito de apagar uma quadra.

## Consequences

Testes que dependem de vitória informam o alvo explicitamente. Quem estiver offline na hora da liberação vê a mensagem genérica de sala expirada ao reconectar.

## Review Trigger

Pedido de recuperar uma quadra liberada por engano ou de ver o histórico dela.
