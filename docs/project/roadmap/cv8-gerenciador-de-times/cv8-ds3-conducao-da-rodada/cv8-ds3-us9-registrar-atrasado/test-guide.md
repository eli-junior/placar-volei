# Guia de validação — CV8.DS3.US9

## Automatizado

`uv run pytest` (537, com `tests/test_atrasado.py`), `npm run check`, `npm run test:e2e` (77).

## Rota do Navigator

1. Com 8 presentes e um jogador cadastrado ausente, sorteie e confirme a rodada.
2. Em Ausentes, toque **Chegou atrasado** nesse jogador. **Esperado:** ele entra em Presentes com a última chegada e aparece um time incompleto só dele no fim da fila.
3. Registre um segundo atrasado. **Esperado:** outro time incompleto separado; ao chegarem à quadra, nenhum aparece na lista de escalação do outro.
4. Jogue até a vez do atrasado. **Esperado:** a lista de escalação (eliminados) aparece e só depois dá para chamar a partida.
5. Inicie o mata-mata e tente registrar outro atrasado. **Esperado:** o botão some e a API recusa; o jogador entra no próximo sorteio.

**Aprova:** tudo acima. **Reprova:** atrasado pareado com outro atrasado, ou entrada após o mata-mata.
