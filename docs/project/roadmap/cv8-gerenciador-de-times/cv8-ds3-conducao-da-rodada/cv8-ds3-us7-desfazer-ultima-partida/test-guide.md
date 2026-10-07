# Guia de validação — CV8.DS3.US7

## Automatizado

`uv run pytest` (548, com `tests/test_desfazer_partida.py`), `npm run check`, `npm run test:e2e`.

## Rota do Navigator

1. Com 10 presentes, jogue 2 partidas de modo que o Time 1 vire rei. Em "Partidas encerradas", toque **Desfazer última partida** e confirme. **Esperado:** o Time 1 volta à quadra com 1 vitória, a fila, os reis e os eliminados como antes da 2ª partida; o histórico perde a 2ª.
2. Tente desfazer de novo. **Esperado:** o botão não aparece (um nível só). Jogue outra partida: ele volta.
3. Chame uma partida e desfaça. **Esperado:** a partida chamada é descartada junto e a anterior volta a ser a próxima a jogar.
4. Termine uma rodada no mata-mata e, no cartão "Campeões da rodada", toque **Desfazer a última partida**. **Esperado:** a rodada reabre no mata-mata; dá para terminar de novo.

**Aprova:** tudo acima. **Reprova:** estado diferente do anterior, segundo desfazer seguido permitido, ou campeão que não reabre.
