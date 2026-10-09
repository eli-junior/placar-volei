---
id: rodada-triangular-de-3-times
status: Decided
raised: 2026-10-09
decided: 2026-10-09
deciders:
  - Eli (Navigator)
  - Claude Sonnet 5.5 (Driver)
related:
  - CV8.DS8.US22
---

# Rodada triangular de 3 times: fixada ao confirmar, só com times completos, fechamento manual

## Question

Com 3 times o rei da quadra deixa o perdedor da primeira partida jogando uma vez só. Como o Navigator quer o desfecho (A vence B; B enfrenta C; só quem vence os dois é rei) e como isso convive com atrasado, escalação, retirada e desfazer?

## Decision

1. A regra é a RN-18: partida 1 dos dois primeiros; o perdedor contra o terceiro; final só se o terceiro vencer; **qualquer outro desfecho termina sem rei e a rodada se encerra sem campeão**.
2. Vale **só com exatamente 3 times completos**, sem escolha do operador.
3. O formato é **fixado ao confirmar** (`rodadas.triangular`, schema 12, aditiva), não deduzido do número de times, porque atrasado, escalação e retirada mudam a contagem e o flag `incompleto` durante a rodada.
4. O fechamento "sem rei" é **manual** ("Encerrar sem campeão"), como o início do mata-mata; o desfazer segue valendo até ele.
5. Atrasado não entra numa rodada triangular; "pular" não se aplica; time que fica sem jogadores encerra sem rei.

## Rationale

Derivar o formato do número de times mudaria a regra no meio da partida (atrasado cria o 4º time). Com time incompleto, o parceiro vem do time que espera a final e jogaria contra o próprio time, então ali vale a RN-02. O fechamento manual evita que um engano de placar feche a rodada sem volta.

## Consequences

- Vaga aberta num time em quadra no triângulo não tem quem a preencha (ninguém é eliminado antes da final): a saída é "Encerrar sem campeão" e sortear de novo (dívida `vaga-no-triangulo-nao-se-preenche`).
- `derivar` ganhou o parâmetro `triangular` e a fase `sem_rei`; `ultimo_campeao` não mostra o campeão de uma rodada anterior quando a última terminou sem rei.
- Qualquer novo formato de rodada deve seguir o mesmo caminho: gravado ao confirmar, derivado em função pura.
