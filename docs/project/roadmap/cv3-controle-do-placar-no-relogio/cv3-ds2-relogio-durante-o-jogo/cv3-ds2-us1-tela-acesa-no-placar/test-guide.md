# Roteiro de validação — CV3.DS2.US1

APK `0.10.1`. O servidor não muda nesta HU.

## Preparação

No WSL, na raiz do projeto:

```sh
export JAVA_HOME=/home/eli/.sdkman/candidates/java/21.0.7-tem
export ANDROID_HOME=/home/eli/Android/Sdk
./wear/gradlew -p wear testDebugUnitTest assembleDebug lintDebug
export PATH=/home/eli/Android/Sdk/platform-tools:$PATH
adb connect IP_DO_WATCH:PORTA
adb -s IP_DO_WATCH:PORTA install -r wear/app/build/outputs/apk/debug/app-debug.apk
```

Se o Gradle falhar com `IllegalArgumentException: 25.0.4.1`, um daemon antigo está no JDK 25: rode `./wear/gradlew -p wear --stop` e repita.

## Passos

1. Abra o **Placar Vôlei**, toque em **Retornar** (ou vincule) e espere o placar.
2. Não toque no relógio por 3 minutos, com o braço parado.
   Passa: tela acesa no brilho normal, mostrando o placar; um toque marca o ponto. Falha: apaga, escurece para ambiente ou volta ao mostrador.
3. Abaixe o pulso por 30 s e levante.
   Passa: placar continua aceso.
4. Volte com o gesto de voltar até a tela de escolha e espere.
   Passa: a tela apaga no tempo normal do relógio.
5. No placar, cubra a tela com a palma.
   Aceito: apaga (gesto do sistema). Ao descobrir, o placar volta.
6. Opcional: bateria antes e depois de 20 min de placar aberto.

## Resultado

2026-09-26: passos 1–5 aprovados pelo Navigator no Galaxy Watch 8. Passo 6 adiado.
