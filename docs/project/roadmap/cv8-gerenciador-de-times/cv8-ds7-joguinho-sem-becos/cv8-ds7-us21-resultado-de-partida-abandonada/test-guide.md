---
code: CV8.DS7.US21
status: Validated
updated: 2026-10-17
---

# Roteiro de validação — Vitória por W.O.

1. `make dev`, `/joguinho`: sorteie com 8 presentes, confirme, vincule a quadra e chame a partida.
2. Marque 4 × 2 para o Time 1 no placar e toque em **Dar a vitória (W.O.)**: o Time 1 vem marcado.
3. Troque para o Time 2 e confirme **Sim, vitória do Time 2**. **Passa** se o histórico mostra "Time 1 [4 × 2] Time 2 · W.O. · Time 2 venceu", o Time 1 está em Eliminados, a próxima partida pode ser chamada, a nota não mudou e o saldo não conta o W.O. **Falha** se a nota mudar, o Time 1 seguir em quadra ou a Resenha contar a partida.
4. **Desfazer última partida**: volta a partida e os dois times.
5. **Resenha:** uma partida jogada até o fim e outra por W.O. → a Resenha conta 1 partida.

Automático: `uv run pytest tests/test_wo.py`; e2e `npx playwright test e2e/conducao.spec.js -g "W.O."` (com `npm run build` antes).
