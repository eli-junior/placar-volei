# Retomada — CV3.DS1.US1

## Atualização 2026-09-23 — API em produção

- A API de vínculo foi extraída para `feature/cv3-ds1-us1-api-relogio` e mesclada na master (`a4b59ae`); essa master foi mesclada nesta branch. Backend (`app/`, `tests/`, `web/`, `scripts/`) desta branch é idêntico ao da master.
- Produção confirmada: `/openapi.json` de `https://placar.elijunior.click` lista `/api/owner/watch-access`, `/api/watch/pairing`, `/api/watch/session`, `/api/watch/state` e as rotas `/api/quadras/{court}/watch*`. A etapa "sincronizar no Mini PC" do roteiro abaixo **já foi cumprida**.
- `29d70d7` (habilitação automática via `WATCH_AUTO_GRANT`) está apenas na branch da API, fora da master. Não foi incorporado aqui: muda o desenho aprovado (habilitação explícita do owner). Aguarda decisão do Navigator.
- Pytest após o merge: 130 passaram. APK local inalterado (SHA-256 `e9971e64…263e`).
- Próximo passo: validação física (itens 4–8 abaixo).
- Teste físico em 2026-09-23: o relógio gerou o código, mas o site recusou `15056015` com “É preciso que o formato corresponda ao exigido”. Causa: em template Svelte, `{8}` no atributo é expressão, então `pattern="[0-9]{8}"` saía como `[0-9]8`. Corrigido para `pattern={'[0-9]{8}'}`, com teste de regressão (`web/tests/modal-relogio.test.js`). A correção é só no frontend e precisa chegar à produção (master) para o teste continuar.

## LEIA PRIMEIRO — transferência solicitada pelo Navigator

**Branch de trabalho: `feature/cv3-ds1-us1-vincular-relogio`.**

O Navigator pediu para salvar e transferir a tarefa a outro agente. Não houve deploy no Mini PC nem merge na master. O próximo agente deve retomar esta branch, não iniciar uma feature nova nem implementar US2 ainda.

### Situação real no momento da transferência
1. O Navigator instalou o primeiro APK no Watch e recebeu “Use o endereço HTTPS do placar” ao gerar código.
2. Corrigimos o campo vazio pouco visível: borda, placeholder, instrução e bloqueio de envio vazio. O Navigator confirmou a URL **https://placar.elijunior.click**, agora padrão no APK.
3. **O backend público ainda não tinha as rotas watch na última consulta.** `/health` e `/openapi.json` responderam 200, versão 0.6.1, nenhuma rota watch. Portanto, só atualizar o APK não basta.
4. O Navigator esclareceu: **fazer ajustes e push neste repositório; a sincronização e execução ocorrem depois no Mini PC**. Não é necessário pedir SSH para preparar o repositório. Não presumir autorização para merge da master ou que o deploy remoto já ocorreu.
5. Foi adicionada seção de sincronização em `wear/README.md` e exclusão de `wear/`, `.gradle/`, `.kotlin/` no `.dockerignore`. O módulo Android local tinha ~80 MB; contexto Docker verificado ficou em ~1,08 MB.
6. **Imagem Docker construída e validada com sucesso** no WSL: `placar-volei:watch-us1-validation`. Um contêiner temporário `--rm --network none` passou por health, frontend HTML, OpenAPI com rotas watch, criação da sala eli, habilitação pelo owner, geração de código, aprovação, consulta de vínculo/estado, identidade única e revogação (401 depois). Logs sem token/segredo. O contêiner terminou; não há servidor de validação deixado rodando por esse teste.
7. Ainda falta **sincronizar/subir esta branch no Mini PC, habilitar eli na sala e repetir a validação física**. Depois do aceite manual, seguir Checkpoint 3; não avançar automaticamente para US2 ou merge.

### Próximos passos concretos do agente que assume

1. Leia este handoff, `wear/README.md`, o plano e o test-guide da US1. Execute `git status`/`git log`; faça fetch e use a branch acima. Atualize assinatura no changelog.
2. Oriente a sincronização no Mini PC (com árvore limpa):

```sh
git fetch origin
git switch feature/cv3-ds1-us1-vincular-relogio
git pull --ff-only origin feature/cv3-ds1-us1-vincular-relogio
docker compose up -d --build placar
docker compose ps placar
```

**Atenção concreta:** o compose atual não monta volume para `/data`; recriar o contêiner descarta as salas anteriores. Fazer fora de partida ativa e criar a sala de teste depois. Não alterar persistência ou configuração de produção silenciosamente.

3. Reconsulte `https://placar.elijunior.click/openapi.json` e confirme `/api/watch/pairing`, `/api/watch/session`, `/api/owner/watch-access`. `/health` sozinho não diferencia a branch, pois o servidor permanece 0.6.1 nesta fase. O comando pronto está em `wear/README.md`.
4. Reinstalar o **APK atualizado** (já compilado) no relógio, usando ADB `install -r`. Artefato local: `wear/app/build/outputs/apk/debug/app-debug.apk`. SHA-256 atual: `e9971e64af674555e0c7f869a51b5a521025242a0d01980f268c13e56a3d263e`. Não está no Git; fontes e wrapper estão. Se necessário reconstruir, usar JDK 21 (comandos abaixo).
5. No telefone, recarregar site e criar sala como **eli**. No terminal do operador, dentro do repo sincronizado:

```sh
python3 scripts/watch_access.py https://placar.elijunior.click PIN_DA_SALA
```

O utilitário pede o segredo de owner via getpass. Não pedir segredo no chat nem embutir no APK. A habilitação é por participante/sala e precisa ser refeita se criar outra sala.
6. Watch → Gerar código; telefone → Relógio → aprovar os 8 dígitos. Esperado: Watch mostra Vinculado como eli e sala correta; demais clientes veem apenas um eli.
7. Cumprir demais cenários de `cv3-ds1-us1-vincular-relogio/test-guide.md`: reabrir app, telefone bloqueado, desconexão, revogação, expiração de código, presença em três clientes. **O APK desta HU ainda NÃO pontua, NÃO desfaz e NÃO tem fila offline**; isso está planejado nas US2–US4.
8. Se houver falha, corrigir na mesma branch e salvar/push frequente. Aceite do Checkpoint 1 já existe; não voltar a pedir plano. Após o Navigator aprovar o teste físico (Checkpoint 2), apresentar revisão/refatoração/dívida no Checkpoint 3, conforme contrato local.

### Verificações consolidadas
- Backend: 130 testes (16 novos) passaram; Ruff passou.
- Frontend: 21 testes, check sem erros/avisos, build passaram.
- Android mais recente: **5 testes**, build e lint passaram; lint com zero erros e sete avisos conhecidos (dependências/KTX).
- Docker: build real + smoke de vínculo/revogação passaram, sem tocar produção.
- Teste físico completo: **pendente**; primeiro teste identificou o problema de endereço e a correção ainda precisa ser revalidada com backend novo.

---

## Estado atual: Checkpoint 2, aguardando validação manual
- Plano e regra de revisão pelo telefone em conflitos offline aprovados pelo Navigator em 2026-09-22.
- Branch `feature/cv3-ds1-us1-vincular-relogio`, criada da master em `638469d`. Nenhum merge na master.
- US1 implementada: vínculo pessoal e revogável, UI web e APK Wear OS. **Pontuação, desfazer e fila offline ainda não implementados** (US2–US4).
- Próximo passo: Navigator valida no Watch, telefone e terceiro cliente usando `cv3-ds1-us1-vincular-relogio/test-guide.md`. Depois do aceite manual, conduzir revisão no Checkpoint 3. Não repetir Checkpoint 1 nem avançar automaticamente para merge.
- Preferência explícita: Android Studio no WSL; commits e pushes parciais frequentes.

## Artefatos
- APK local: `wear/app/build/outputs/apk/debug/app-debug.apk` (ignorado no Git; reconstruível pelo wrapper).
- Instalação, build, provisionamento pessoal: `wear/README.md`.
- Roteiro manual: `cv3-ds1-us1-vincular-relogio/test-guide.md`.
- Plano técnico: `cv3-ds1-us1-vincular-relogio/plan.md`.
- Backend: `app/watch.py`, schema em `app/db.py`, integração em `app/main.py` e `app/hub.py`.
- Web: `ModalRelogio.svelte`, integrado a `SalaQuadra.svelte`.
- Provisionamento: `scripts/watch_access.py` (segredo do owner solicitado sem eco, não vai ao site/APK).

## Ambiente pronto no WSL
- WSL2/WSLg em PREDATOR-JR, x86_64.
- Android Studio Quail 4 Patch 1: `/home/eli/.local/opt/android-studio/bin/studio.sh`. Instalador oficial Linux verificado por SHA-256; processo gráfico iniciado.
- SDK `/home/eli/Android/Sdk`, API 35, build-tools 35.0.0, platform-tools.
- **JDK de build 21** em `/home/eli/.sdkman/candidates/java/21.0.7-tem`. JDK 25 do Studio/default falhou com Gradle 8.11.1; selecionar JDK 21 nas configurações Gradle do IDE.
- Gradle Wrapper versionado em `wear/`; AGP 8.9.2, Kotlin 2.1.20, Gradle 8.11.1.
- Node Linux 24.14.0 temporário em `/tmp/placar-watch-tools/node-v24.14.0-linux-x64/bin`. O npm do PATH original é Windows e não funciona no WSL. Instalar Node Linux durável se /tmp for limpo.
- `web/node_modules` instalados pelo lockfile. Frontend compilado em `app/static/` (ignorado no Git).
- Nenhuma instância de validação foi deixada rodando pelo Driver; roteiro fornece comando com banco em /tmp. Nenhum deploy de produção.

## Evidência automatizada
- `.venv/bin/pytest -q`: **130 passaram**, incluindo 16 testes novos de vínculo, permissão, concorrência, revogação, presença, migração aditiva e ausência de segredos nos logs. Quatro avisos de depreciação já existentes nas dependências/testes.
- Ruff check e format --check: passaram.
- Frontend: check sem erros/avisos, **21 testes passaram**, build passou.
- Android: **5 testes passaram**, assembleDebug e lintDebug passaram. Lint avisa sobre versões mais novas de dependências e sugere KTX para SharedPreferences; uso de commit com retorno verificado é deliberado. Total final: zero erros e sete avisos. Relatório `wear/app/build/reports/lint-results-debug.txt`.
- `git diff --check`: passou.
- Não foi executado teste físico nem emulador. Bluetooth, tela circular, modo ambiente e Keystore no aparelho precisam do aceite manual.

## Desenho e limites
- `watch_grants` autoriza participante específico; `watch_devices` guarda hash da credencial criada no relógio, código temporário em hash, expiração e revogação.
- Identificador interno eli-smartwatch; participante público eli único. Habilitação pessoal precisa ser feita em cada sala pelo operador; aprovação do código pelo próprio participante requer papel ADMIN/CONTROLADOR.
- WebSocket por Bearer, sem segredo na URL. Revogação fecha somente sockets do dispositivo; telefone conserva sua sessão. Token do relógio não é sessão administrativa do navegador.
- Credencial local cifrada por AES-GCM/Android Keystore e excluída de backup/transferência. Presença ativa usa WebSocket; consultas de estado recuperam vínculo após retomada.
- Código de oito dígitos dura cinco minutos; limites de criação e aprovação em memória, máximo de 20 pedidos pendentes. Reavaliar rate limiting persistente na revisão se o recurso deixar de ser pessoal.
- App inicial não suporta manter atividade de rede em modo ambiente/background. Não afirmar entrega da operação offline completa.
- Modelo do telefone e tamanho do Watch não informados; orientar instalação e validar ergonomia real com o Navigator.
- README/briefing gerais ainda indicam 0.4.2 e changelog fecha 0.6.1: pendência para coerência documental após Checkpoint 3, não reescrita ampla nesta fase.

## Operação segura
- Não pedir ao Navigator segredo de owner no chat. Usar utilitário com getpass.
- Não usar banco de produção para teste. Roteiro usa `/tmp/placar-watch-us1.db`.
- Metadados Git, cache uv, Gradle/SDK e interface gráfica precisam de execução escalada no sandbox desta sessão.
- Pytest dentro do sandbox travou sem saída; fora do sandbox passou em segundos. Usar timeout em diagnósticos, sem ficar repetindo execuções.
- Houve ajuste automático de versão no uv.lock pelo uv; revertido por ser anterior e fora do escopo. Servidor continua 0.6.1; APK se identifica como 0.7.0-us1.

## Correção após primeiro teste físico
Navigator instalou o APK, mas Gerar código mostrou apenas “Use o endereço HTTPS do placar”. O APK não tinha serverUrl configurado e o campo vazio não possuía borda/placeholder. Corrigido: campo com borda, alvo mínimo de 48 dp, placeholder e instrução para tocar; envio desabilitado com endereço vazio; mensagem específica para ausência de endereço. Cinco testes Android passaram; build e lint passaram. Endereço real confirmado posteriormente: https://placar.elijunior.click, já configurado no APK atual. Não houve deploy do backend. Revalidar preenchimento e geração antes de seguir no Checkpoint 2.

## Endereço confirmado e bloqueio de integração
Navigator confirmou `https://placar.elijunior.click`. O APK agora usa essa origem como padrão (ainda sobrescrevível por `-PserverUrl`). Build, lint e cinco testes Android passaram. Consulta pública em 2026-09-23: `/health` HTTP 200, `/openapi.json` HTTP 200, versão 0.6.1, nenhuma rota contendo `watch`. O servidor público ainda não executa esta implementação; reinstalar o APK sozinho não habilita vínculo. Necessário disponibilizar backend de teste acessível ao relógio. Navigator esclareceu posteriormente que os ajustes e o push são feitos neste repo e sincronizados no Mini PC. Nenhum deploy remoto foi executado; seguir o roteiro do topo deste handoff. O compose atual não persiste `/data` em volume: recriar o contêiner pode perder salas ativas; preferir ambiente de validação separado ou acordar janela/banco antes de substituir produção.
