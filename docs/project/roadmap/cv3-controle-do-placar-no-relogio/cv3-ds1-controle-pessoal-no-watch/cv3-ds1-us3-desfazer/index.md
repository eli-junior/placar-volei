---
code: CV3.DS1.US3
level: User Story
status: Done
status_reason: Validada no relógio real e entregue na 0.9.0 (2026-09-23)
updated: 2026-09-23
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

## Notes
- Entregue pelo [plano](plan.md) com alvo explícito: o desfazer aponta para o ponto que o relógio viu (seq confirmado ou id do lance da fila), e o servidor só aplica se ele ainda for o último ponto ativo. Ver o registro de decisão `desfazer-do-relogio-com-alvo-explicito-e-registro-antes-do-envio`.
- No teste físico, o Navigator pediu a faixa inferior inteira para o desfazer (some sem o controle) e a bolinha colorida de conexão. Ver o [roteiro](test-guide.md).
- A tela de vínculo perdeu o campo de servidor. Retomar ou trocar de quadra ficou para a [US5](../cv3-ds1-us5-um-vinculo-por-vez/index.md).
- O envio continua só com o app aberto; em segundo plano, na US4.
