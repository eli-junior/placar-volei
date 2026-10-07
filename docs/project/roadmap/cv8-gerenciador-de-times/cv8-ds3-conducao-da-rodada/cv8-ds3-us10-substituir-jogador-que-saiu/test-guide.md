# Guia de validação — CV8.DS3.US10

## Automatizado

`uv run pytest` (540, com `tests/test_substituicao.py`), `npm run check`, `npm run test:e2e`.

## Rota do Navigator

1. Com 9 presentes (ímpar), sorteie, confirme e jogue uma partida (Time 1 fica com 1 vitória).
2. No painel, **Substituir quem saiu**: quem saiu = um jogador do Time 1; quem entra = o jogador ímpar "aguardando na fila". **Esperado:** o Time 1 continua em quadra com 1 vitória, com o substituto; o time do ímpar some da fila; quem saiu aparece em Ausentes.
3. Repita escolhendo um eliminado como substituto. **Esperado:** "· escalado" ao lado do nome e ele sai de Eliminados.
4. Tente um substituto homem para uma dupla com homem havendo mulher elegível. **Esperado:** recusa com a explicação de H+H.
5. Chame uma partida e tente substituir. **Esperado:** o formulário some e a API recusa.
6. Em Ausentes, **Chegou atrasado** no que saiu. **Esperado:** volta como atrasado (reversível).

**Aprova:** tudo acima. **Reprova:** time perdendo vitórias/posição, H+H evitável, substituição com partida chamada.
