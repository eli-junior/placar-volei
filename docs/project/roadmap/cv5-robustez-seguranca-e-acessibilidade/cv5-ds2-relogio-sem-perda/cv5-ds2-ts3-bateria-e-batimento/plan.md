# Plano — CV5.DS2.TS3 Bateria e sensor de batimento

- **Nível:** Technical Story · **Branch:** `feature/cv5-ds2-ts3-bateria-e-batimento` · **Versão:** patch (APK)

## Correção da revisão
O `targetSdk` é 35, não 36 (`build.gradle.kts`). A permissão granular `READ_HEART_RATE` só vira obrigatória ao subir para 36. Esse item passa para a `CV5.DS2.TS4`.

## Scope
1. Sensor de batimento ligado só com a Activity em STARTED: `rememberHeartRate` troca o `DisposableEffect(granted)` por `LifecycleStartEffect(granted)` (`HeartRate.kt:52`). Ao sair do app pelo botão, o callback é removido.
2. Sem polling com o socket aberto: no `observeWhileVisible` (`WatchModel.kt:491`), com `linked && socket != null`, o laço só acorda por `poke` (fechamento, falha ou ação), sem `refresh()` a cada 15 s. Reconexão com backoff (2 s → 30 s) quando o socket cai.
3. **Tela do placar (decisão do Navigator):** recomendo manter acesa (a US1 da DS2 da CV3 pediu isso para o toque estar pronto), mas liberar depois de **10 min sem toque e sem mudança de placar**, com o placar ainda na tela. Alternativa: modo ambient com placar em contorno (mais trabalho, exige `AmbientLifecycleObserver`).
4. Medir bateria antes e depois: 30 min de placar aberto com batimento, `adb shell dumpsys batterystats`.

## Acceptance
- Dado o placar aberto, quando aperto o botão lateral e saio do app, então o sensor para em até 2 s (log do callback).
- Dado o socket conectado por 5 min, então não há chamadas a `/api/watch/session` nem `/state` no log do servidor.
- Dado 10 min sem atividade, então a tela pode apagar; um toque volta ao placar.

## Out of Scope
Ambient mode completo (se o Navigator escolher o timeout); permissão granular (TS4).

## Risks
Sem refresh periódico, uma revogação só chega pelo socket (`4401`), que o servidor já envia. Conferir que a sucessão de controle também chega por snapshot.

## Validation
Logs do servidor e do relógio; batterystats antes/depois; roteiro físico de 30 min.
