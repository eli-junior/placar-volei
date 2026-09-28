# Plano aceito — CV6.DS2.US4

User Story de CV6.DS2. Branch `feature/cv6-ds2-us4-repouso-e-retomada`, criada de `master` após US3 aceita. Plano aceito pelo Navigator; implementação concluída. A revisão registra uma parte do plano não implementada (pausa de animação e sensor no repouso) e os limites da validação física aceita.

## Evidência inicial

- Galaxy Watch SM-L330: Android 16/API 36; timeout de tela informado pelo sistema: 60 s. Consulta somente leitura via ADB em 2026-09-28. Gesto e Always On Display ainda precisam ser conferidos no aparelho; `doze_enabled` retornou null, insuficiente para inferir configuração.
- MainActivity executa `observeWhileVisible()` somente em RESUMED. Ao pausar, WatchModel cancela envio e fecha WebSocket.
- ScoreScreen mantém `keepScreenOn` por até 10 min sem mudanças. HeartRate tem ciclo de vida próprio e não deve virar gravação de treino.
- Wear OS controla modo ambiente e retorno ao mostrador. Ongoing Activity pode manter uma tarefa visível por mais tempo; tarefas de rede ainda estão sujeitas a restrições de energia.

## Implementação proposta

1. Investigar no aparelho as transições de atividade, ambiente e tela apagada, com AOD e levantar pulso; registrar apenas eventos técnicos, sem credenciais. Confirmar o comportamento antes de consolidar a arquitetura.
2. Remover a trava de tela acesa no placar. Respeitar tempo de tela e gesto do sistema. Para tela completamente apagada, validar com AOD desligado; não alterar preferências globais automaticamente.
3. Separar a duração da sessão de placar da atividade visível: transporte e fila com um único proprietário, evitando sockets ou envios concorrentes ao recriar a tela.
4. Propor serviço em primeiro plano e Ongoing Activity durante o acompanhamento da quadra. Notificação discreta permite voltar ao placar e **Encerrar acompanhamento**, encerrando transporte local sem apagar vínculo/fila nem encerrar a partida. Início a partir do app visível, sem autoarranque no boot. Encerrar também ao revogar vínculo ou trocar de quadra. Confirmar o tipo de serviço adequado após a investigação (possível specialUse com justificativa explícita de acompanhamento de partida); não declarar treino/áudio fictícios para manter processo vivo.
5. Retorno ao levantar o pulso deve reaproveitar a sessão, sem escolher sala novamente. **Pendente:** parar animações e leitura ativa de batimento durante repouso e retomá-las quando interativo; manter Samsung Health independente. Essa parte não entrou na implementação e não foi validada.
6. Preservar fila e idempotência existentes. Queda real de rede reconcilia automaticamente; distinguir isso de desconexão causada pelo próprio ciclo de vida.

## Aceite

- Dado placar aberto e gesto habilitado, ao repousar a tela apaga; ao levantar o pulso, volta direto ao placar.
- Com rede disponível, mensagens recebidas durante repouso atualizam o estado e o transporte permanece conectado. Comprovar por eventos de abertura/fechamento e recebimento enquanto a tela está apagada.
- Com queda real de 30 s, restauração da rede reconcilia pontos sem duplicação e sem intervenção manual.
- Vínculo, fila e quadra preservados. Encerrar acompanhamento encerra a sessão local de maneira explícita.
- Treino do Samsung Health continua. Medição inicial de bateria sem carregador e sem ADB contínuo; não prometer autonomia sem medir.

## Validação

Automatizar transições de sessão, início/parada idempotentes, recriação de tela e reconciliação com servidor falso. Executar testes, builds e lint Wear; testar backend se houver mudança de protocolo, que não está prevista.

Roteiro completo em `test-guide.md`. Evidência aceita pelo Navigator: Galaxy Watch SM-L330/Android 16 entrou em Dozing via ADB; serviço foreground e WebSocket permaneceram ativos por 60 s sem evento de fechamento. Não foram observados gesto físico, atualização remota durante repouso, queda/restauração de rede, treino ativo ou bateria. A aceitação dessa evidência limitada não equivale à execução dos demais cenários.

Falha: retorno à escolha/pareamento, necessidade de abrir o app, socket encerrado só por apagar a tela, perda/duplicação, treino interrompido ou sessão impossível de encerrar. Permanecem como critérios para validação futura os cenários físicos ainda não observados.

## Alternativas e limites

- Só remover keepScreenOn: insuficiente, porque o transporte atual é cancelado em onPause.
- Só reconectar no retorno: não satisfaz o critério de conexão mantida.
- Ongoing Activity sozinha: ajuda a retomada visual, mas não é garantia de rede permanente.
- WorkManager: não fornece conexão de baixa latência contínua; não é substituto do socket durante a partida.
- Doze pode adiar rede mesmo com sessão em andamento. Se o aparelho não permitir o aceite integral, apresentar evidência e alternativa ao Navigator antes de mudar o critério. Não pedir isenção de bateria nem manter CPU acordada continuamente sem avaliar necessidade e custo.

## Escopo e versão

Versão entregue: Wear **0.25.0**, minor por adicionar acompanhamento com sessão em segundo plano. Backend/web permanecem 0.24.0; o protocolo não mudou.

Fora do escopo: novas regras de pontuação, alterações de permissões de quadra, novo treino de saúde, suporte garantido a todo fabricante, operação após encerramento forçado do app e sincronização por serviço externo. Revisitar somente se bloquear o aceite, com decisão explícita.

## Fontes oficiais

- [Modo ambiente e duração na tela](https://developer.android.com/training/wearables/always-on).
- [Ongoing Activity](https://developer.android.com/training/wearables/notifications/ongoing-activity).
- [Rede em Wear OS e restrições no repouso](https://developer.android.com/training/wearables/data/network-communication).
- [Tipos de serviço em primeiro plano](https://developer.android.com/develop/background-work/services/fgs/service-types).
- [Doze e App Standby](https://developer.android.com/training/monitoring-device-state/doze-standby).
