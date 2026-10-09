---
code: CV8.DS8.US22
status: Planned
updated: 2026-10-09
---

# Plano — Rodada triangular de 3 times

Origem: pedido do Navigator em 2026-10-09. Decisões de produto do mesmo dia: (1) com B vencendo C não há rei; (2) vale **só com exatamente 3 times**, sem escolha do operador; (3) rodada sem rei **encerra sem campeão**.

## Regra proposta (RN-18)

Com exatamente 3 times na rodada (o incompleto conta), a fila não segue a RN-02:

1. **Partida 1:** os dois primeiros da fila. Chamo de V1 o vencedor e P1 o perdedor.
2. **Partida 2:** **P1 × o terceiro time (T3)**. V1 espera, sem sair da rodada.
3. **Partida 3 (final), só se T3 venceu a partida 2:** **T3 × V1**.
   - T3 vence: T3 é o **rei** (campeão, sem mata-mata, já que não há outros reis).
   - V1 vence: **termina sem rei**.
4. Se P1 venceu T3 na partida 2: **termina sem rei**, sem final.

Resumo: só é rei o time que vence os dois outros em sequência (T3 contra P1 e depois contra V1). Cada time joga ao menos 1 partida e o T3 pode jogar até 2.

Todas as partidas contam no saldo (RN-10, RN-14). Placar, RN-09 e "Desfazer a última partida" valem como hoje.

## Acceptance (Given / When / Then)

- **Dado** uma rodada com 3 times **quando** o Time 1 vence o Time 2 **então** a próxima partida é Time 2 × Time 3 e o Time 1 aparece esperando.
- **Dado** a partida 2 **quando** o Time 3 vence **então** a próxima partida é Time 3 × Time 1, avisada como final.
- **Dado** a final **quando** o Time 3 vence **então** o Time 3 é o rei e o painel oferece "Coroar campeão", que encerra a rodada com ele.
- **Dado** a final **quando** o Time 1 vence, **ou** na partida 2 o Time 2 vence o Time 3, **então** o painel mostra "Termina sem rei" e oferece "Encerrar sem campeão"; a rodada fecha sem campeão e o sorteio seguinte é liberado.
- **Dado** qualquer etapa **quando** o operador desfaz a última partida **então** o painel volta à etapa anterior, inclusive da final ou do "sem rei".
- **Dado** uma rodada com 4 times ou mais **então** nada muda (regressão da RN-02).

## Design

- **`app/conducao.py`:** `derivar` ganha um ramo para `len(times) == 3`, com a sequência acima derivada dos resultados (módulo puro, sem estado novo). Reaproveita `fase="fim_da_fila"` com `desafiante` = o rei e sem rivais para o caso do rei (já oferece "Coroar campeão" e `registrar_campeao`). Nova fase `sem_rei` para o fim sem campeão. Os resultados continuam em `partidas_rodada` com `fase="fila"`; sem coluna nova, **sem migração** (schema 11).
- **`app/rodada.py` e rota:** `registrar_sem_campeao` fecha a rodada (`estado='encerrada'`, `campeao_time_id` nulo) por uma ação manual do operador, no mesmo espírito do início manual do mata-mata (RN-04), o que também mantém o "Desfazer" possível até o fim. Verificar tudo que lê `campeao_time_id` de rodada encerrada (`ultimo_campeao`, exibição) para aceitar nulo.
- **Web (`PainelConducao`, espectador):** faixa de etapa ("Final do triângulo", "Time 1 espera") e o botão "Encerrar sem campeão". Textos do mata-mata não aparecem neste formato.
- **Alternativa descartada:** formato escolhido pelo operador no sorteio (fica para depois se pedirem; exigiria coluna nova em `rodadas`).

## Casos de borda e padrão proposto

- **Jogador retirado, time sem ninguém (US19/TS3):** o triângulo deixa de valer; com 2 times restantes a rodada fecha como "sem rei" se faltar partida, ou segue com o vencedor registrado quando já houver rei. Cobrir com teste.
- **Vaga aberta e substituição:** funcionam como hoje, na vez do time entrar em quadra.
- **"Pular o Time N":** não é oferecido, porque a ordem das partidas no triângulo é fixa.
- **Time incompleto (ímpar):** conta como um dos 3 times e escolhe o parceiro na sua vez.

## Fora de escopo

- Rodadas de 4+ times; escolha do formato no sorteio; histórico/ranking (fase 2).

## Versão

**0.49.0** (minor: comportamento novo visível; backend, web e APK sobem juntos, `versionCode` 33; Wear OS inalterado).

## Testes previstos

- `tests/test_conducao.py`: as 5 sequências do triângulo (rei, sem rei duas vezes, desfazer, vencedor invertido na partida 1) e o caso de 4 times.
- `tests/test_rodada.py`/e2e: rodada de 3 times até "Coroar campeão" e até "Encerrar sem campeão", com o saldo somando as partidas.

## Validação do Navigator (preparar no Checkpoint 2)

Sortear 3 times (6 presentes em duplas), conduzir os dois desfechos e o desfazer, conferir os textos.
