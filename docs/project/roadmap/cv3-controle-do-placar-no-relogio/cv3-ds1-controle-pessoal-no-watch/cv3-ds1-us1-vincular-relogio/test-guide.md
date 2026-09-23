# Checkpoint 2 — Validação de CV3.DS1.US1

## Objetivo
Validar o vínculo no Watch real, mantendo eli como uma pessoa na sala, autorizando pelo telefone e revogando sem desconectar o telefone. Este APK ainda não tem botões de ponto/desfazer.

## Preparação isolada no WSL
Na raiz do projeto, com frontend já compilado:

```sh
DB_PATH=/tmp/placar-watch-us1.db OWNER_SECRET=watch-validacao-local .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Esse comando usa banco descartável e segredo exclusivo de teste. Não use o segredo de exemplo em servidor público. Abra `http://localhost:8001` no computador. Para reconstruir o frontend: em `web`, `npm ci`, `npm run build`, usando Node Linux 24; nesta sessão o binário está em `/tmp/placar-watch-tools/node-v24.14.0-linux-x64/bin` (temporário).

Use **três clientes**: telefone de Eli, Watch e navegador anônimo como espectador. Instale o APK conforme `wear/README.md`.

### Como alcançar o backend local
Se telefone e Watch alcançam diretamente o computador pela rede, use `http://IP_DO_COMPUTADOR:8001`. No WSL em modo NAT pode ser necessário encaminhar a porta no Windows; não presumir que o IP privado do WSL seja acessível pelo telefone.

Alternativa para validar sem mudar firewall: com os dispositivos Android conectados ao ADB do WSL (depuração sem fio), execute:

```sh
/home/eli/Android/Sdk/platform-tools/adb devices
/home/eli/Android/Sdk/platform-tools/adb -s SERIAL_DO_WATCH reverse tcp:8001 tcp:8001
/home/eli/Android/Sdk/platform-tools/adb -s SERIAL_DO_TELEFONE reverse tcp:8001 tcp:8001
```

Use `http://127.0.0.1:8001` no app do Watch e no navegador do telefone. O serial é o mostrado por `adb devices`. Para telefone sem ADB, use acesso LAN configurado no Windows. O túnel ADB valida a funcionalidade, **não prova transporte Bluetooth**; esse cenário requer posteriormente servidor HTTPS acessível aos dispositivos com ADB desligado.

## Cenário 1 — vínculo e nome público
1. No telefone, crie a sala com apelido `eli` e configure equipes/regras.
2. No navegador anônimo, entre pelo PIN como `Torcida`.
3. No WSL, habilite o participante daquela sala:
   `python3 scripts/watch_access.py http://127.0.0.1:8001 PIN_DA_SALA`.
   Informe `watch-validacao-local` quando solicitado.
4. No Watch, informe endereço acessível, toque **Gerar código** e leia os 8 dígitos.
5. No telefone, abra **Relógio**, digite o código e confirme o vínculo.
6. Observe a transição da mensagem no Watch para **Vinculado como eli / Sala XXXXX**; no telefone, aparece o dispositivo para revogação. Na torcida, deve continuar existindo apenas um `eli`.
7. Feche e reabra o app: deve recuperar o vínculo sem novo código.

Passa: três clientes concordam sobre sala/identidade, sem participante `eli-smartwatch` público nem segredo exposto. Falha: credencial visível, pessoa duplicada, sala errada ou reentrada obrigatória após fechar.

## Cenário 2 — telefone bloqueado e perda de rede
1. Com Watch no app e telefone bloqueado por mais de dois minutos, confira se eli continua presente e o vínculo válido no Watch; a torcida deve continuar vendo uma pessoa.
2. Desative a rede do Watch por ~30 segundos, reative e volte ao app. Deve reconectar sem gerar outro código.
3. Repita com servidor HTTPS acessível e depuração ADB desligada, Watch usando Bluetooth com o telefone. Não considerar este item aprovado usando `adb reverse`.

Passa: recuperação preserva identidade/vínculo; nenhuma permissão indevida. Falha: precisa parear de novo ou entra em outra sala. A atividade pode ser suspensa ao sair do app; controle de pontuação em modo ambiente não faz parte desta HU.

## Cenário 3 — revogação e limites
1. No telefone, clique **Revogar acesso**. O Watch deve indicar vínculo indisponível ao receber fechamento do socket ou na próxima consulta (até 15 s enquanto ativo).
2. O telefone deve continuar conectado e apto a marcar pontos normalmente; a torcida recebe os pontos. O relógio revogado não deve receber novos snapshots.
3. Gere novo código, espere mais de cinco minutos e tente aprová-lo: deve recusar como expirado. Gere outro válido e aprove; reutilizar o código deve falhar.
4. Em outro navegador como espectador, tente `POST /api/quadras/PIN/watch/approve` com JSON `{"code":"12345678"}` e sua própria sessão. Esperado: 403. Nem apelido eli nem código conhecido autorizam participante não habilitado.
5. Tente cinco códigos inválidos pelo telefone: rejeição. A tentativa seguinte deve responder 429 e informar espera. Evite fazer isso antes dos demais cenários, pois bloqueia temporariamente o pareamento.

## Cenário 4 — restart e ergonomia
1. Com vínculo ativo, interrompa e execute novamente o mesmo comando uvicorn, com mesmo DB_PATH e versão. Watch deve recuperar o vínculo; pontos já confirmados pelo telefone permanecem.
2. Verifique no telefone real, nos modos Sol/Noite, que código, botões e mensagens são legíveis e o modal não corta os controles.
3. Ative movimento reduzido no navegador e desative animações nas opções de acessibilidade/desenvolvedor do relógio: vínculo deve permanecer legível sem depender da animação.

## Evidência automatizada
Resultados finais, commit e eventuais avisos ficam registrados no handoff e no changelog ativo. Comandos reproduzíveis:

```sh
.venv/bin/pytest -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
# Em web/: npm run check; npm test; npm run build
JAVA_HOME=/home/eli/.sdkman/candidates/java/21.0.7-tem ./wear/gradlew -p wear testDebugUnitTest assembleDebug lintDebug
```

O teste `test_owner_secret_and_device_token_do_not_appear_in_logs` inspeciona os logs capturados das operações reais de vínculo e provisionamento. Não colar segredo de produção em comandos, URL, relato ou screenshot.

## Resultado manual
Pendente: Navigator executa e informa aprovado ou falhas observadas. Nenhum teste físico foi afirmado pelo Driver. Após aprovação manual, seguir para Checkpoint 3 de revisão, sem merge automático.

## Arquivos desta entrega
- `.gitignore`, `CHANGELOG.md`: exclusões Android e tracking do ciclo.
- `app/db.py`, `app/watch.py`, `app/hub.py`, `app/main.py`: persistência, autorização e transporte do dispositivo.
- `tests/test_watch_pairing.py`: 16 novos cenários de integração e segurança.
- `web/src/components/ModalRelogio.svelte`, `web/src/components/SalaQuadra.svelte`: vínculo e revogação pelo telefone.
- `scripts/watch_access.py`: habilitação pessoal pelo operador.
- `wear/`: projeto Gradle/Wrapper, manifests, MainActivity, WatchModel, CredentialStore, ServerAddress, recursos de ícone/backup, testes e README.
- Roadmap CV3/DS1/HUs, plano técnico, este roteiro e handoff: escopo aprovado e estado de retomada.

## Resultado automatizado de 2026-09-23
130 testes Python, 21 frontend e 3 Android aprovados. Ruff, Svelte check e builds passaram. Lint Android: zero erros e sete avisos (cinco sobre versões mais recentes disponíveis e dois sugerindo KTX; commit síncrono com retorno verificado foi mantido deliberadamente).

APK: `wear/app/build/outputs/apk/debug/app-debug.apk`
SHA-256: `e9971e64af674555e0c7f869a51b5a521025242a0d01980f268c13e56a3d263e`.

### Revalidação do endereço (correção do primeiro teste físico)
Reinstale o APK atualizado com `adb install -r`. Sem endereço, observe campo com borda e exemplo `https://seu-placar`, e botão Gerar código desabilitado. Toque no campo e informe a origem HTTPS real do servidor que executa esta branch, sem `/quadra/PIN`. O botão deve habilitar. Falha: campo invisível ou tentativa de gerar com endereço vazio. Os cinco testes Android passaram após esta correção.

O APK atualizado traz `https://placar.elijunior.click` por padrão. Em 2026-09-23, essa origem respondeu normalmente, mas seu OpenAPI ainda não expunha rotas `watch`. Não considerar erro de conexão/vínculo contra esse backend antigo como falha do campo de endereço; primeiro disponibilizar esta branch no ambiente de teste. Para testar vazio, apague o endereço pré-preenchido.
