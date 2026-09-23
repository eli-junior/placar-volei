# Placar Vôlei — Wear OS

APK de teste pessoal para **acompanhar e marcar o placar pelo Galaxy Watch**. O relógio é vinculado à sala pelo telefone e entra nela como o participante **Eli (Relógio)**. Ele marca e desfaz pontos quando o admin passa o controle para ele (`CV3.DS1.US2`–`US3`, versão `0.9.0`). O servidor deve executar a mesma versão do APK: o desfazer precisa da `0.9.0` no servidor.

## WSL / Android Studio

Ambiente preparado nesta sessão:

- Android Studio: `/home/eli/.local/opt/android-studio/bin/studio.sh` (Quail 4 Patch 1, Linux, WSLg).
- SDK: `/home/eli/Android/Sdk` (API 35, build-tools 35.0.0, platform-tools).
- JDK de build: `/home/eli/.sdkman/candidates/java/21.0.7-tem`. **O JDK 25 embutido no Studio não é compatível com este Gradle.**
- AGP 8.9.2, Gradle 8.11.1, Kotlin 2.1.20; versões fixadas nos arquivos de build.

No Android Studio, abra a pasta `wear`. Em **Settings → Build, Execution, Deployment → Build Tools → Gradle → Gradle JDK**, selecione o JDK 21 acima. Configure o SDK em `/home/eli/Android/Sdk`. `local.properties` e configurações locais do IDE não são versionados.

Pelo terminal WSL, na raiz do projeto:

```sh
export JAVA_HOME=/home/eli/.sdkman/candidates/java/21.0.7-tem
export ANDROID_HOME=/home/eli/Android/Sdk
./wear/gradlew -p wear testDebugUnitTest assembleDebug lintDebug
```

Saída: `wear/app/build/outputs/apk/debug/app-debug.apk`. Credenciais não são incluídas no APK. O endereço é `https://placar.elijunior.click`, confirmado pelo Navigator, e fica fixo no APK: o relógio não tem campo para editá-lo. Para outro servidor, compile com:

```sh
./wear/gradlew -p wear assembleDebug -PserverUrl=https://SEU-SERVIDOR
```

APK debug permite HTTP para validação local; o manifest principal exige HTTPS. O cliente não segue redirecionamentos com sua credencial.

## Instalar no Watch via Wi-Fi

1. No relógio, habilite opções de desenvolvedor e **Depuração sem fio**. Mantenha PC e Watch na mesma rede Wi-Fi durante instalação.
2. Escolha **Parear novo dispositivo**, anote IP/porta de pareamento e o código. A porta de conexão exibida na tela anterior é diferente da porta de pareamento.
3. No WSL:

```sh
export PATH=/home/eli/Android/Sdk/platform-tools:$PATH
adb pair IP_DO_WATCH:PORTA_DE_PAREAMENTO
# Digite o código solicitado; não é o código do Placar.
adb connect IP_DO_WATCH:PORTA_DE_CONEXAO
adb devices
adb -s IP_DO_WATCH:PORTA_DE_CONEXAO install -r wear/app/build/outputs/apk/debug/app-debug.apk
```

Abra **Placar Vôlei** na lista de apps do relógio. A primeira tela oferece só **Gerar código**. Esse código de 8 dígitos é aprovado no site pelo telefone em **Relógio**.

Referência: [depuração Wear OS por Wi-Fi](https://developer.android.com/training/wearables/get-started/debug-wifi).

## Sincronizar o backend no Mini PC

No repositório do Mini PC, com a árvore de trabalho limpa e **fora de uma partida**:

```sh
git fetch origin
git switch master
git pull --ff-only origin master
grep WATCH_AUTO_GRANT .env   # se aparecer eli.relogio, troque para eli ou apague a linha
docker compose up -d --build placar
curl -fsS https://placar.elijunior.click/health
```

Passa: `/health` mostra a versão esperada. O compose atual guarda o SQLite dentro do contêiner: recriá-lo apaga as salas (`debt-banco-de-producao-sem-volume-persistente`). Crie a sala de teste **depois** de subir o contêiner.

## Habilitar e vincular

1. No telefone, crie a sala (ou entre nela) como **`eli`**, em qualquer caixa. A sala mostra **Eli**, que já fica habilitado para o relógio. A lista vem de `WATCH_AUTO_GRANT` (padrão `eli`, separada por vírgulas). Outros apelidos veem "Em breve…" no ícone do relógio.
2. No relógio, abra **Placar Vôlei** → **Gerar código**. No telefone, toque no **ícone de relógio** e digite o código de 8 dígitos (vale 5 minutos).
3. A lista de presentes passa a mostrar **Eli (Relógio)**, como espectador. O relógio mostra o placar com os botões travados.

O vínculo exige papel ADMIN ou CONTROLADOR do dono. Quem cria a sala já é ADMIN.

Sem `WATCH_AUTO_GRANT`, habilite pelo terminal, uma vez por sala (o segredo de owner é pedido sem eco):

```sh
python3 scripts/watch_access.py https://placar.elijunior.click PIN_DA_SALA
```

## Marcar pelo relógio

1. Com o app aberto no relógio, na lista de presentes do telefone: **Tornar controlador** em Eli (Relógio) e depois **Passar controle**.
2. O site deixa de mostrar +1/Desfazer, e o relógio libera as duas metades: **Nós** (equipe A, à esquerda) e **Eles** (equipe B, à direita). Com jogadores cadastrados, aparecem as iniciais (ex.: EC × RM).
3. Cada toque é gravado no relógio antes de vibrar. Enquanto o servidor não confirma, o número fica apagado, com um traço embaixo, e o alto da tela mostra "N pendentes".
4. Sem rede, os toques ficam na fila e são enviados em ordem quando a rede volta, com o app aberto. O envio em segundo plano é da US4.
5. Se o servidor recusar um lance (partida nova, controle retomado, partida encerrada), a fila pausa e o relógio pede **Descartar**, com confirmação.

## Desfazer pelo relógio

1. O botão **↶**, no centro inferior, desfaz o último ponto que o relógio mostra. É um toque, sem confirmação. A vibração é diferente da do ponto, e o número desce.
2. Funciona também com o lance ainda pendente, sem rede. Ao reconectar, o ponto e o desfazer são enviados em ordem e aparecem os dois na linha do tempo.
3. O botão fica apagado quando não há ponto para desfazer e continua ativo com a partida encerrada. Desfazer o ponto da vitória reabre a partida.
4. Se o placar mudou no servidor antes do envio, o desfazer é recusado ("O placar mudou; este desfazer não foi aplicado."), nenhum outro ponto é tocado, e a fila pede **Descartar**.

O controle nas mãos do relógio não volta sozinho quando a tela apaga. Para retomar pelo telefone, use **Assumir o controle**.

Revogar: no telefone, **ícone de relógio → Revogar acesso**. O Eli (Relógio) sai da sala, e o controle volta para o Eli. Vincular outro relógio revoga o anterior e mantém o papel e o controle já dados ao relógio.

## Validação

Siga o [roteiro da US3](../docs/project/roadmap/cv3-controle-do-placar-no-relogio/cv3-ds1-controle-pessoal-no-watch/cv3-ds1-us3-desfazer/test-guide.md) e, para a pontuação, o [roteiro da US2](../docs/project/roadmap/cv3-controle-do-placar-no-relogio/cv3-ds1-controle-pessoal-no-watch/cv3-ds1-us2-ver-e-marcar/test-guide.md). O [roteiro da US1](../docs/project/roadmap/cv3-controle-do-placar-no-relogio/cv3-ds1-controle-pessoal-no-watch/cv3-ds1-us1-vincular-relogio/test-guide.md) traz instruções para testar localmente sem alterar produção.

O tráfego Wear OS normalmente usa o telefone pareado como proxy Bluetooth; a plataforma gerencia as redes disponíveis. Suspensão em background pode adiar rede: a presença via WebSocket e o envio de lances funcionam enquanto a tela do app está ativa. [Referência de rede Wear OS](https://developer.android.com/training/wearables/data/network-communication).
