---
code: CV3.DS1.US3
level: User Story
status: Planned
status_reason: Descoberta registrada; aguardando aceite do Checkpoint 1
updated: 2026-09-22
---

# CV3.DS1.US3 — Desfazer o último ponto pelo relógio

## Intent
Como Eli, quero desfazer o último ponto pelo relógio para corrigir um toque sem buscar o celular.

## Scope
Ação acessível na mesma tela. Desfazimento identifica o ponto exato visto na projeção local, nunca um ponto novo de outro operador por efeito de atraso.

## Acceptance / Done Condition
- Dado um ponto confirmado, quando desfazer, então uma correção append-only referencia aquele ponto e todas as telas convergem.
- Dado ponto local pendente, quando desfazer, então a fila mantém intenção e ordem sem causar ponto ou correção duplicados.
- Se não existir ponto ativo, desfazer fica indisponível.
- Se o ponto alvo já mudou no servidor, a correção não afeta outro lance: sinaliza conflito e preserva a intenção para revisão.
- Desfazer o ponto de vitória reabre a partida conforme as regras existentes.

## Validation Route
Marcar A, B e desfazer: obter 1×0. Repetir offline, reabrir o app e reconectar. Simular ponto concorrente e verificar que ele não é desfeito silenciosamente.
