# Placar Vôlei — Wear OS (US1)

APK de teste pessoal para **vincular o Galaxy Watch à sala configurada no telefone**. Esta entrega ainda não marca pontos: essa função começa na US2. O servidor deve executar a branch `feature/cv3-ds1-us1-vincular-relogio`.

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

Saída: `wear/app/build/outputs/apk/debug/app-debug.apk`. Credenciais não são incluídas no APK. O endereço padrão é `https://placar.elijunior.click`, confirmado pelo Navigator. Pode ser alterado no relógio ou sobrescrito no build:

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

Abra **Placar Vôlei** na lista de apps do relógio. A primeira tela pede o endereço do servidor e oferece **Gerar código**. Esse código de 8 dígitos é aprovado no site pelo telefone em **Relógio**.

Referência: [depuração Wear OS por Wi-Fi](https://developer.android.com/training/wearables/get-started/debug-wifi).

## Sincronizar o backend no Mini PC

O APK usa endpoints novos desta branch. Fazer pull apenas da `master` não os disponibiliza. Para o teste da HU1, no repositório do Mini PC, com a árvore de trabalho limpa:

```sh
git fetch origin
git switch feature/cv3-ds1-us1-vincular-relogio
git pull --ff-only origin feature/cv3-ds1-us1-vincular-relogio
docker compose up -d --build placar
docker compose ps placar
```

O compose atual guarda o SQLite dentro do contêiner: recriá-lo inicia sem as salas anteriores. Faça essa atualização fora de uma partida e crie a sala de teste **depois** de subir o contêiner. Nenhuma configuração de `.env` ou Cloudflare precisa mudar para usar o mesmo domínio.

Confira se a API pública já expõe o vínculo, sem criar dados:

```sh
curl -fsS https://placar.elijunior.click/openapi.json | python3 -c 'import json,sys; paths=json.load(sys.stdin)["paths"]; required={"/api/watch/pairing", "/api/watch/session", "/api/owner/watch-access"}; missing=required-set(paths); print("Backend do relógio disponível" if not missing else "Faltam rotas: " + ", ".join(sorted(missing))); sys.exit(bool(missing))'
```

Passa: imprime `Backend do relógio disponível`. Se faltarem rotas, confira a branch ativa e se o contêiner foi reconstruído. A partir da `0.7.0`, `/health` também indica o backend com o relógio.

Recarregue o site no telefone e entre na sala seguindo a habilitação abaixo.

## Habilitar o relógio

Crie a sala (ou entre nela) pelo telefone com o apelido-senha **`eli.relogio`**. A sala mostra só **eli**; o sufixo não é gravado nem exibido. Quem entra com esse apelido já fica habilitado para vincular relógio, sem segredo de owner. O apelido-senha vem de `WATCH_AUTO_GRANT` (padrão `eli.relogio` no compose; lista separada por vírgulas). Digitar apenas `eli` **não** habilita o relógio.

O vínculo exige papel ADMIN ou CONTROLADOR. Quem cria a sala já é ADMIN; quem entra depois precisa ser promovido.

Alternativa sem apelido-senha (`WATCH_AUTO_GRANT` vazio): crie a sala como **eli** e habilite pelo terminal, uma vez por sala (o segredo é solicitado sem eco):

```sh
python3 scripts/watch_access.py https://placar.elijunior.click PIN_DA_SALA
```

Nos dois casos, o relógio ainda precisa ser aprovado pelo código temporário no navegador desse participante. O segredo de owner não deve ser colocado no relógio nem no site.

Revogar o dispositivo: **Relógio → Revogar acesso**, no telefone. Desabilitar também futuros vínculos naquela sala:

```sh
python3 scripts/watch_access.py https://placar.elijunior.click PIN_DA_SALA --disable
```

Um revínculo revoga o dispositivo anterior. Internamente, o dispositivo é `eli-smartwatch`; na presença e no histórico permanece o único participante **eli**. Trocar de sala exige novo vínculo. Códigos expiram em cinco minutos, e as tentativas são limitadas.

## Validação

Siga o [roteiro da HU1](../docs/project/roadmap/cv3-controle-do-placar-no-relogio/cv3-ds1-controle-pessoal-no-watch/cv3-ds1-us1-vincular-relogio/test-guide.md), incluindo instruções para testar localmente sem alterar produção.

O tráfego Wear OS normalmente usa o telefone pareado como proxy Bluetooth; a plataforma gerencia as redes disponíveis. Suspensão em background pode adiar rede: nesta HU, presença via WebSocket é mantida enquanto a tela do app está ativa. [Referência de rede Wear OS](https://developer.android.com/training/wearables/data/network-communication).
