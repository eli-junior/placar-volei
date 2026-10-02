# Placar Vôlei — Wear OS

> **0.27.0 (CV7.US2):** o relógio marca a **quadra local do celular** sem internet. O celular decide o modo: com a sala local aberta nele, o app do relógio mostra a quadra local (tag **LOCAL**, mesmo placar, fila offline e desfazer de sempre, com fila própria); fora disso é o servidor, como antes. Se o celular fecha a sala o relógio volta ao servidor; sem sinal do celular por 90 s também volta, a não ser que haja lances na fila (aí ele mantém a quadra local com o anel vermelho até enviá-los). Para o celular, deixe a tela acesa durante a partida local (`CV7.TS3`, plano B).

> **0.26.0 (CV7.TS3):** o `applicationId` passou de `br.com.placarvolei.watch` para **`br.com.placarvolei`**, o mesmo do app do celular (o Wearable Data Layer exige o mesmo id e a mesma assinatura nos dois). Para atualizar, **desinstale o app antigo do relógio** e instale este; o vínculo com o servidor é zerado e as quadras precisam ser vinculadas de novo. A ponte com a quadra local do celular existe como contrato e transporte (`CelularLink`); a tela do relógio para ela chega na CV7.US2. Nas builds **debug** há um disparador por `adb` para exercitá-la:
>
> ```bash
> DBG="-n br.com.placarvolei/br.com.placarvolei.watch.DebugCelular"
> adb -s <relógio> shell am broadcast $DBG -a br.com.placarvolei.watch.DEBUG_ESTADO
> adb -s <relógio> shell am broadcast $DBG -a br.com.placarvolei.watch.DEBUG_PONTO --es equipe A
> adb -s <relógio> shell am broadcast $DBG -a br.com.placarvolei.watch.DEBUG_DESFAZER
> adb -s <relógio> logcat -d -s CelularDebug
> ```
>
> Em release, o relógio e o celular precisam ser assinados com a mesma keystore.

APK de teste pessoal para **acompanhar e marcar o placar pelo Galaxy Watch**. O relógio é vinculado à sala pelo telefone e entra nela como o participante **Eli (Relógio)**. Ele marca e desfaz pontos quando o admin passa o controle para ele (`CV3.DS1.US2`–`US3`) e, sem rede, segue marcando e sincroniza depois, mesmo após reabrir o app (`CV3.DS1.TS1`). Na `0.20.0` (CV5), o relógio se recupera de vínculo ou fila ilegíveis, não trava a fila em recusas passageiras, desliga sensor e polling quando não precisa, pede dois toques para "Nova" e tem build de release com R8. O APK 0.24.1 é compatível com o servidor 0.24.0; esta atualização muda a interface do relógio e não exige deploy do servidor.

## WSL / Android Studio

Ambiente preparado nesta sessão:

- Android Studio: `/home/eli/.local/opt/android-studio/bin/studio.sh` (Quail 4 Patch 1, Linux, WSLg).
- SDK: `/home/eli/Android/Sdk` (API 35, build-tools 35.0.0, platform-tools).
- JDK de build: `/home/eli/.sdkman/candidates/java/21.0.7-tem`, padrão do `sdk` desde 2026-09-26. **O JDK 25 embutido no Studio não é compatível com este Gradle.**
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

### APK de release (CV5.DS2.TS4)

O release passa pelo R8 (cerca de 3,4 MB contra 26,6 MB do debug) e é assinado com uma keystore **fora do repositório**. Uma vez só:

```bash
keytool -genkeypair -v -keystore ~/.android/placar-release.jks -alias placar -keyalg RSA -keysize 4096 -validity 10000
```

Em `~/.gradle/gradle.properties`:

```properties
placarKeystore=/home/eli/.android/placar-release.jks
placarKeystorePassword=...
placarKeyAlias=placar
placarKeyPassword=...
```

Depois: `./wear/gradlew -p wear assembleRelease` gera `wear/app/build/outputs/apk/release/app-release.apk`. Sem essas propriedades, sai `app-release-unsigned.apk`, que não instala. Instalar o release sobre o debug exige desinstalar antes (assinaturas diferentes) e parear de novo.

`targetSdk` 36: no Wear OS 6 o app pede a permissão granular de frequência cardíaca (`READ_HEART_RATE`); em versões anteriores, `BODY_SENSORS`.

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

Abra **Placar Vôlei** na lista de apps do relógio. Sem vínculo, a primeira tela oferece só **Ingressar numa quadra**, na faixa inferior. Esse código de 8 dígitos é aprovado no site pelo telefone em **Relógio**.

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
2. No relógio, abra **Placar Vôlei** → **Ingressar numa quadra**. No telefone, toque no **ícone de relógio** e digite o código de 8 dígitos (vale 5 minutos).
3. A lista de presentes passa a mostrar **Eli (Relógio)**, como espectador. O relógio mostra o placar com os botões travados.

O vínculo exige papel ADMIN ou CONTROLADOR do dono. Quem cria a sala já é ADMIN.

## Retomar ou trocar de quadra

O relógio fica vinculado a uma quadra por vez (`CV3.DS1.US5`). Ao reabrir o app (sair com o gesto de voltar e abrir pelo ícone), ele pergunta:

- **Retornar**: volta ao placar da quadra guardada, cujo nome aparece no botão. Funciona sem rede.
- **Parear outra quadra**: gera um código novo, aprovado no telefone da outra quadra. O vínculo atual só cai na aprovação; **Voltar para <quadra>** desiste e cancela o código. Com lances pendentes, o relógio avisa quantos serão abandonados antes de gerar.

A tela que só apagou e acendeu no meio do jogo volta direto ao placar.

Sem `WATCH_AUTO_GRANT`, habilite pelo terminal, uma vez por sala (o segredo de owner é pedido sem eco):

```sh
python3 scripts/watch_access.py https://placar.elijunior.click PIN_DA_SALA
```

## Marcar pelo relógio

1. Com o app aberto no relógio, na lista de presentes do telefone: **Tornar controlador** em Eli (Relógio) e depois **Passar controle**.
2. O site deixa de mostrar +1/Desfazer, e o relógio libera as duas metades: **Equipe A** (azul, à esquerda) e **Equipe B** (laranja, à direita). Com jogadores cadastrados, aparece um nome completo por linha.
3. Cada toque é gravado no relógio antes de vibrar. Enquanto o servidor não confirma, o número fica apagado, com um traço embaixo. O status da tela indica o estado: verde conectado, amarelo enviando ou reconectando, vermelho sem conexão. O status acessível informa quantos lances estão pendentes.
4. Sem rede, os toques ficam na fila e são enviados em ordem quando a rede volta, com o app aberto. O envio em segundo plano é da US4.
5. Conflito não se revisa (`CV3.DS1.US4`, `0.24.0`): se o controle foi para outra pessoa, começou partida nova, o placar mudou por fora ou o vínculo caiu, a fila inteira é descartada. O relógio mostra por 3 s um aviso como “3 lances não enviados · controle com Ana” e volta ao placar do servidor.

## Desfazer pelo relógio

1. A faixa **Voltar Ponto**, na parte de baixo da tela, desfaz o último ponto que o relógio mostra. É um toque, sem confirmação. A vibração é diferente da do ponto, e o número desce.
2. Funciona também com o lance ainda pendente, sem rede. Ao reconectar, o ponto e o desfazer são enviados em ordem e aparecem os dois na linha do tempo.
3. A faixa fica apagada quando não há ponto para desfazer, some quando o controle não está no relógio e continua ativa com a partida encerrada. Desfazer o ponto da vitória reabre a partida.
4. Se o placar mudou no servidor antes do envio, o desfazer é recusado ("O placar mudou; este desfazer não foi aplicado."), nenhum outro ponto é tocado, e a fila é descartada com o aviso de 3 s.

## Tela acesa

Enquanto o placar está visível, a tela não apaga sozinha (`CV3.DS2.US1`, `0.10.1`): o toque já marca, sem acordar o relógio. Cobrir com a palma ainda apaga. As telas de vínculo e de escolha seguem o tempo normal de tela.

O controle nas mãos do relógio não volta sozinho quando a tela apaga. Para retomar pelo telefone, use **Assumir o controle**.

## Leitura do placar (CV6.DS2.US1)

Os números usam uma cópia local da fonte Teko, ajustada para caber no mostrador circular inclusive com três dígitos. A fonte acompanha o APK sob a SIL Open Font License; o relógio não baixa fontes durante o uso. O indicador de batimentos fica centralizado no topo quando a permissão está disponível. Sem leitura aparece `♥ --`; sem permissão, o indicador fica oculto.

Na faixa inferior, a correção aparece como **Voltar Ponto**. A descrição acessível ainda informa a equipe do último ponto. Ao fim da partida, **Nova** fica verde e exige dois toques dentro de três segundos.

Revogar: no telefone, **ícone de relógio → Revogar acesso**. O Eli (Relógio) sai da sala, e o controle volta para o Eli. Vincular outro relógio revoga o anterior e mantém o papel e o controle já dados ao relógio.

## Validação

Siga o [roteiro da US3](../docs/project/roadmap/cv3-controle-do-placar-no-relogio/cv3-ds1-controle-pessoal-no-watch/cv3-ds1-us3-desfazer/test-guide.md) e, para a pontuação, o [roteiro da US2](../docs/project/roadmap/cv3-controle-do-placar-no-relogio/cv3-ds1-controle-pessoal-no-watch/cv3-ds1-us2-ver-e-marcar/test-guide.md). O [roteiro da US1](../docs/project/roadmap/cv3-controle-do-placar-no-relogio/cv3-ds1-controle-pessoal-no-watch/cv3-ds1-us1-vincular-relogio/test-guide.md) traz instruções para testar localmente sem alterar produção.

O tráfego Wear OS normalmente usa o telefone pareado como proxy Bluetooth; a plataforma gerencia as redes disponíveis. Suspensão em background pode adiar rede: a presença via WebSocket e o envio de lances funcionam enquanto a tela do app está ativa. [Referência de rede Wear OS](https://developer.android.com/training/wearables/data/network-communication).

## Retorno ao pontuar (CV6.DS2.US3, Wear 0.24.1)

Após gravar o ponto localmente, a equipe recebe destaque breve, vibração e som de toque conforme preferências do sistema. A bola animada indica o último ponto válido e acompanha desfazer, pontos do telefone e lances pendentes. Ao zerar, desaparece. Reenvios não repetem o sinal de toque. Som e movimento podem ser desativados pelo sistema; o marcador permanece legível.

[Roteiro de validação](../docs/project/roadmap/cv6-ajustes-de-uso-em-quadra/cv6-ds2-placar-no-relogio/cv6-ds2-us3-retorno-ao-pontuar/test-guide.md).
