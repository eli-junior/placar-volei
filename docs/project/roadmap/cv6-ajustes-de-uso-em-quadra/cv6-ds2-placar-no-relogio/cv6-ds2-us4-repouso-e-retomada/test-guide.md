# CV6.DS2.US4 — Teste e validação

Checkpoint 2: APK instalado no Galaxy Watch SM-L330 (Android 16/API 36); validação física pendente.

## Preparação

- APK release 0.25.0, versionCode 13: `wear/app/build/outputs/apk/release/app-release.apk`.
- APK instalado via `adb install -r`, mantendo vínculo/fila. Backend/web não mudam.
- Abrir Placar Vôlei e aceitar **Permitir notificações** quando o sistema perguntar. Isso habilita a Ongoing Activity e a ação de encerramento.
- Vincular o Watch a uma quadra de teste. Usar também o telefone na mesma quadra; passar o controle conforme necessário. Não reiniciar o servidor: em produção, start limpa salas e vínculos.
- Confirmar que **Levantar pulso para ativar** está ligado. Para observar tela totalmente preta, desligar Always On Display; com AOD ligado, o Wear OS pode mostrar a tela escurecida em vez de apagá-la. Anotar timeout de tela e restaurar a configuração inicial ao fim.

## Repouso e retomada

1. Com placar conectado, observar a notificação de baixa prioridade **Placar em acompanhamento** e o ponto de retorno no mostrador. Conferir que tocar a notificação volta ao app.
2. Abrir um log de diagnóstico antes do ciclo: `adb -s <watch> logcat -s WatchSession:I`. Anotar a linha `WebSocket conectado`.
3. Abaixar o pulso e aguardar mais que o timeout (60 s no aparelho consultado). A tela deve apagar se AOD estiver desligado. Não tocar no relógio.
4. Com a tela apagada, pelo telefone marcar um ponto na equipe de teste. Levantar o pulso. O Watch volta ao placar e mostra o mesmo ponto sem escolher sala nem parear. A linha de log `snapshot recebido pelo WebSocket` deve ser posterior a `Activity pausada pelo sistema`; a conexão não deve ter linha `WebSocket fechado` no intervalo.
5. Repetir dez ciclos de baixar/levantar, incluindo tela escurecida com AOD ligado. Cada retomada deve ir direto ao placar.
6. Com o Watch novamente repousado, interromper a rede do relógio por 30 s (modo avião), marcar um ponto no telefone e restaurar a rede. Deve surgir `WebSocket indisponível`/reconexão, seguido de `WebSocket conectado`; placar reconcilia automaticamente e sem duplicação. Confirmação do servidor após a retomada é reconexão, evidência distinta da continuidade no cenário 4.
7. Repetir com Samsung Health gravando um treino. Confirme que o app não encerra nem assume a sessão de treino.
8. Por fim, abrir a notificação, tocar **Encerrar acompanhamento** e confirmar remoção da notificação e fechamento do WebSocket. Abrir Placar Vôlei novamente: sessão reinicia e o vínculo volta direto ao placar.

Para coletar o recorte depois dos ciclos: `adb -s <watch> logcat -d -s WatchSession:I`. Logs não incluem token, URL ou identificador da quadra. A conexão ADB ativa pode afetar o repouso; repetir o ciclo sem executar comandos ADB entre apagar e levantar o pulso, e consultar os logs só depois.

## Aceite

**Aprova:** notificação e retorno em um toque, tela segue preferências de repouso/gesto, conexão fica sem fechamento durante o repouso com rede disponível, mudanças recebidas enquanto apagada, reconexão automática após queda real, fila íntegra e treino independente. Observar consumo por 20–30 min sem carregar, comparando com repouso normal; não usar isso como medição laboratorial.

**Falha:** Activity encerra socket ao pausar, Watch volta para escolha/pareamento, pontos somem ou duplicam, requer ação manual após rede retornar, notificação não pode ser encerrada, treino para, ou custo de bateria inviável. Se Doze do dispositivo adiar WebSocket apesar da sessão ativa, registrar logs e comportamento; não alterar o aceite sem Navigator.

## Evidência automatizada e limite

Comando: `JAVA_HOME=/home/eli/.sdkman/candidates/java/21.0.7-tem ./wear/gradlew -p wear testDebugUnitTest assembleDebug lintDebug assembleRelease`.

59 testes JVM cobrem fila, reenvio e reconciliação existentes. Debug/release e lint devem terminar verdes. A conexão em ambiente/Doze, permissão, notificação, gesto, treino e bateria exigem este teste no relógio real.
