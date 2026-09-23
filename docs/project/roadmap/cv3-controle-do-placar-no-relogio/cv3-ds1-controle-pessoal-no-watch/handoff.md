# Retomada — CV3.DS1.US1

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
- Android: **3 testes passaram**, assembleDebug e lintDebug passaram. Lint avisa sobre versões mais novas de dependências e sugere KTX para SharedPreferences; uso de commit com retorno verificado é deliberado. Total final: zero erros e sete avisos. Relatório `wear/app/build/reports/lint-results-debug.txt`.
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
Navigator instalou o APK, mas Gerar código mostrou apenas “Use o endereço HTTPS do placar”. O APK não tinha serverUrl configurado e o campo vazio não possuía borda/placeholder. Corrigido: campo com borda, alvo mínimo de 48 dp, placeholder e instrução para tocar; envio desabilitado com endereço vazio; mensagem específica para ausência de endereço. Cinco testes Android passaram; build e lint passaram. Endereço real solicitado ao Navigator para pré-configurar o próximo APK; resposta ainda pendente. Não houve deploy do backend. Revalidar preenchimento e geração antes de seguir no Checkpoint 2.
