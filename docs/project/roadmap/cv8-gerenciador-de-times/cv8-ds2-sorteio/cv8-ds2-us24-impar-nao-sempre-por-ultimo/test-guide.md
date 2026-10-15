---
code: CV8.DS2.US24
status: Validated
updated: 2026-10-15
---

# Roteiro de validação — Ímpar não fica sempre por último

1. `make dev`, abra `/joguinho` e marque 11 presentes (6 H e 5 M), com uma mulher por último.
2. Sorteie a rodada 1: o ímpar é o **último homem** a chegar, todas as duplas mistas, o incompleto no fim.
3. Jogue até o campeão e anote quem jogou a última partida.
4. Sorteie a rodada 2. **Passa** se o ímpar é o homem que jogou mais recentemente, está no fim da fila e as duplas saem mistas e equilibradas. **Falha** se aparecer H+H, se o ímpar for uma mulher (com mais homens) ou se o incompleto não estiver no fim.
5. Sem excesso de homens (5 H e 6 M): o ímpar da rodada 2 é quem jogou por último, de qualquer gênero.
6. Trio com 8 presentes: a sobra de 2 é de quem jogou por último, sem trio de um sexo só, e fica no fim.

Automático: `uv run pytest tests/test_sorteio.py tests/test_reequilibrio.py`.
