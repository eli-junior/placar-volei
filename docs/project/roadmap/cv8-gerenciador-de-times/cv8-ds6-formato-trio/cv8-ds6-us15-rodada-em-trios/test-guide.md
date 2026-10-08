# Guia de validação — CV8.DS6.US15

## Automatizado

`uv run pytest` (569, com `tests/test_trio.py`), `npm run check`, `npm run test:e2e` (80, com 2 testes do formato trio).

## Rota do Navigator

1. Na Sessão, marque 9 presentes (misture homens e mulheres) e escolha **Trios** em "Formato dos times". **Esperado:** botão "Sortear trios"; com menos de 6 presentes ele fica desabilitado.
2. Sorteie. **Esperado:** 3 trios, cada um com homem e mulher, somas de nota parecidas; "Resortear" traz outra combinação.
3. Confirme, vincule a quadra e chame a primeira partida. **Esperado:** o placar mostra "A + B + C" e, no relógio, 3 nomes em linhas (confira se cabem na tela).
4. Repita com 7 presentes. **Esperado:** 2 trios e o último a chegar como "Incompleto". Jogue até a vez dele: a tela pede **2 parceiros**; escolha um por vez. **Esperado:** o trio só chama a partida depois do 2º; a lista não deixa fechar o trio só de um sexo havendo alternativa.
5. Com 8 presentes: o último par é um time de 2 que escolhe **1** parceiro.
6. Jogue até o campeão, desfaça a última partida e abra a tela do espectador. **Esperado:** fila, reis e campeões com 3 nomes.

**Aprova:** tudo acima. **Reprova:** trio de um sexo havendo alternativa, partida chamada com time incompleto, nome cortado no relógio ou regressão nas duplas.
