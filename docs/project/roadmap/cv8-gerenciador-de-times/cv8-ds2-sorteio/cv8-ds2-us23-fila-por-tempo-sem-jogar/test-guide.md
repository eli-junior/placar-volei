---
code: CV8.DS2.US23
status: Validated
updated: 2026-10-15
---

# Roteiro de validação — Fila por tempo sem jogar

1. `make dev`, abra `/joguinho` com o segredo do dono e marque 10 presentes.
2. Sorteie a rodada 1 (alvo 6), confirme, vincule a quadra e jogue até o campeão, anotando em que partida cada dupla jogou por último.
3. Sorteie a rodada 2. **Passa** se a 1ª partida tem principalmente quem saiu cedo da rodada 1, o campeão e o último confronto ficam no fim da fila, e as duplas continuam equilibradas e mistas. **Falha** se um time cujos dois jogadores jogaram a última partida abre a fila, ou se as duplas desequilibram.
4. **Cancelada:** jogue uma partida da rodada 2, cancele e sorteie de novo: quem jogou essa partida vai para o fim.
5. **Ímpar:** com 11 presentes o último a chegar segue sozinho no fim (esperado; US24).

Automático: `uv run pytest tests/test_sorteio.py tests/test_reequilibrio.py`.
