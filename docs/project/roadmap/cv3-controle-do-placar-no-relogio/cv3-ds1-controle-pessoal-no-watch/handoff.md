# Retomada — CV3.DS1.US1

## Autorização e estado
- Navigator aprovou o Checkpoint 1 e a proposta de revisão pelo telefone em conflitos offline.
- Implementação autorizada até Checkpoint 2 da US1; não pedir aprovação de plano novamente.
- Branch: `feature/cv3-ds1-us1-vincular-relogio`, criada da `master` em `638469d`. Planejamento trazido da branch `feature/cv3-planejamento-controle-relogio` (commit `cda5415`). Não houve merge na master.
- Preferência adicional: usar WSL para rodar Android Studio; salvar e fazer push frequente do progresso.
- Em 2026-09-22, início do registro: apenas documentação. Atualização de progresso abaixo substitui o estado inicial.

## Ambiente verificado
- Já estamos em WSL2: host PREDATOR-JR, kernel microsoft-standard-WSL2, x86_64.
- Java disponível em `/home/eli/.sdkman/candidates/java/current/bin/java`.
- `adb`, `gradle`, `studio` e `studio.sh` não encontrados no PATH; não há `/home/eli/Android` nem `/home/eli/.gradle`.
- Diretório padrão Windows `/mnt/c/Program Files/Android` não existe; isso não exclui instalação em outro lugar.
- `/tmp/placar-watch-tools` criado e vazio no último exame.
- Download de command-line tools falhou por DNS do sandbox. Pedido escalado de download foi interrompido pelo Navigator antes de executar. Não tratar ferramentas como instaladas.
- Escritas Git requerem execução escalada (index.lock protegido). Criação da branch já foi autorizada/executada.

## Inspeção e desenho técnico para continuar
- `app/comandos.py`: autentica sessão do navegador por hash; exige controle_id e controle_versao para pontos/desfazer. Não conceder permissão pelo apelido.
- `app/main.py`: WebSocket autentica só cookie, envia snapshot e registra presença. Nova conexão nativa deve usar credencial própria e verificar revogação, sem publicar token em URL ou snapshots.
- `app/hub.py`: já agrega vários sockets por participante; adaptar invalidação de conexões do dispositivo sem derrubar a sessão do telefone.
- `app/sucessao.py`: devolve controle após 15 s de ausência, sucessão após 120 s. Não confundir tela desligada com revogação; verificar presença de outros sockets.
- Proposta de schema aditivo: autorização pessoal por participant_id e dispositivos com hash de token, hash de código temporário, expiração, participante vinculado, criação/aprovação/revogação. Patch não foi aplicado antes da interrupção.
- Habilitação inicial pelo operador via autenticação de owner no servidor; credencial owner nunca vai para o APK. Participante Eli já existente recebe vínculo; todos continuam vendo apenas eli.
- Código temporário no relógio aprovado na UI web autenticada. Limitar tentativas, expirar código, consumir uma vez, permitir revogação, preservar segurança contra concorrência.
- Para sobreviver a resposta perdida: relógio pode gerar e persistir sua credencial antes de pedir código; servidor guarda somente hash. Poll autenticado retorna estado do vínculo, nunca precisa devolver segredo novamente.
- US1 inclui APK de vínculo e superfície web; pontuação/desfazer/fila completa pertencem às próximas HUs. Não apresentar esta HU como controle completo do placar.

## Próximos passos
1. Preparar Android Studio/SDK no WSL conforme orientação do Navigator, verificar instalação existente antes de baixar. Documentar versões e comandos reproduzíveis.
2. Implementar vínculo, autorização restrita, testes do backend, UI web e app Wear OS de vínculo.
3. Testar build APK, pytest, Ruff e frontend; registrar limitações reais de acesso ao hardware.
4. Produzir roteiro manual concreto no Watch, telefone e terceiro cliente e parar no Checkpoint 2.
5. Commit e push parciais frequentes. Não integrar master nem avançar checkpoints sem aceite.

## Pendências do Navigator
Modelo do telefone e tamanho do Watch não informados. Não bloqueiam backend e estrutura inicial; serão necessários para validar ergonomia e instalação real.

## Progresso salvo em 2026-09-23
- Android Studio Quail 4 Patch 1 instalado em `/home/eli/.local/opt/android-studio`, arquivo oficial verificado por SHA-256. Processo gráfico iniciado via WSLg.
- SDK em `/home/eli/Android/Sdk`; API 35/build-tools 35.0.0/platform-tools instalados. Gradle 8.11.1 em `/tmp/placar-watch-tools/gradle-8.11.1`.
- Backend inicial em `app/watch.py`, schema aditivo, autenticação WS nativa e revogação no hub implementados. UI `ModalRelogio.svelte` adicionada.
- 114 testes existentes passaram antes dos novos testes; 13 testes novos passaram após integração do backend. Ruff sem erros nos arquivos Python alterados.
- Execução de pytest no sandbox ficou travada; executada fora do sandbox com sucesso.
- Node Linux em preparação: npm do PATH é Windows e falha. Download v24.14.0 em `/tmp/placar-watch-tools`.
- Ainda faltam módulo Wear/APK, validação frontend, revisão da implementação e roteiro manual. Não é Checkpoint 2.
