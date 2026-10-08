# Guia de validação — CV8.DS5.US14

## Automatizado

`tests/test_chamada.py` (o `estado_partida` leva `equipe_a`, `equipe_b`, `jogadores_a`, `jogadores_b` após **Chamar partida**). O relógio (Wear 0.27.0) já lê esses campos em `Scoreboard.kt` (`teamLabels`).

## Rota do Navigator (relógio físico)

1. Com o relógio pareado à quadra vinculada, chame uma partida no gerenciador. **Esperado:** o relógio mostra o nome de cada jogador da dupla, em linhas separadas, no lado de cada equipe. 2. Marque pontos e desfaça no relógio. **Esperado:** o controle de pontos funciona como antes.

**Aprova:** nomes das duplas no relógio e pontos normais. **Reprova:** "Equipe A/B" no lugar dos nomes, ou o toque de ponto quebrado.
