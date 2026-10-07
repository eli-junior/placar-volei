# Guia de validação — CV8.DS4.US12 Persistir sessão

## Automatizado

`uv run pytest` — 521 testes (`tests/test_persistencia.py` é o novo). Não há mudança de interface, então `npm run test:e2e` segue como na 0.38.0.

## Rota do Navigator

1. Jogue uma rodada de 10 presentes até o meio do mata-mata.
2. Reinicie só o gerenciador **sem apagar o volume**: `docker compose restart placar`.
   - **Esperado:** a tela Sessão volta igual: fila, reis, histórico com placares e a partida do mata-mata onde parou. A quadra do placar é efêmera: recrie e vincule de novo, como sempre.
3. Termine o mata-mata, reinicie de novo.
   - **Esperado:** "Campeões da rodada 1" continua na tela.
4. Opcional (no Mini PC): `docker compose exec placar sqlite3 /data-gerenciador/gerenciador.db "select ordem, fase, placar_a, placar_b from partidas_rodada order by ordem"` — uma linha por partida, com placar.
5. Cancele uma rodada com partidas jogadas e repita o item 4: as partidas continuam lá.

**Aprova:** tudo igual após cada reinício. **Reprova:** qualquer partida, placar ou campeão que sumir.
