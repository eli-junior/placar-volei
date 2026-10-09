---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-09
related:
  - CV8.DS8.US22
  - rodada-triangular-de-3-times
---

# US22: rodada triangular de 3 times (0.49.0)

- **Pedido:** com 3 times, A vence B, B enfrenta C; se C vence B enfrenta A na final; só quem vence os dois é rei, senão termina sem rei (Navigator, 2026-10-09).
- **Entrega:** RN-18; `derivar` com o ramo triangular e a fase `sem_rei`; rota `encerrar-sem-campeao`; schema 12 (`rodadas.triangular`); painel com a etapa do triângulo e o fechamento manual; espectador com "Terminou sem rei."
- **Desvios do plano:** coluna nova no banco (o formato precisa ficar fixo na rodada) e vale só com 3 times completos (com incompleto, o parceiro jogaria contra o próprio time). Vaga aberta no triângulo ganhou a saída "Encerrar sem campeão".
- **Testes antigos adaptados:** três usavam 3 times para provar o rei da quadra e passaram a usar 4 (`test_encerramento`, `test_mata_mata`, e2e de encerrar partida e de retirar).
- **Ambiente:** o `pytest` completo cai com segfault nesta máquina; os testes rodaram por arquivo (541 + os novos), e um `axe` do e2e deu timeout na rodada longa e passou isolado.
- **Dívida:** `vaga-no-triangulo-nao-se-preenche` (nova) e `rodada-py-concentra-regras-painel-e-escalacao` (atualizada: 713 linhas).
- **Validação:** feita pelo Navigator em 2026-10-09.
