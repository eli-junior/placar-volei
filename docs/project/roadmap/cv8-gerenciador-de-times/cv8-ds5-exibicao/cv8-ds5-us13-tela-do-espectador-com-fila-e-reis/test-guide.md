# Guia de validação — CV8.DS5.US13

## Automatizado

`uv run pytest` (552, com `tests/test_exibicao.py`), `npm run check`, `npm run test:e2e` (teste "espectador vê a fila e os reis").

## Rota do Navigator

1. Com a sessão e a rodada em andamento, crie e vincule a quadra do placar. 2. Em outro aparelho (ou aba anônima), abra `/quadra/<código>` e entre como espectador. **Esperado:** abaixo do placar, a faixa "Fila: … · Reis: nenhum" com os nomes das duplas. 3. Toque na tela para sair do modo imersivo. **Esperado:** o cartão completo (em quadra, fila, reis). 4. No gerenciador, chame e encerre partidas. **Esperado:** a fila e os reis do espectador andam sozinhos, sem recarregar. 5. Termine a rodada. **Esperado:** "Campeões da rodada N".

**Aprova:** tudo acima, sem notas nem dados pessoais à mostra. **Reprova:** fila desatualizada, nota visível ou faixa cobrindo o placar.
