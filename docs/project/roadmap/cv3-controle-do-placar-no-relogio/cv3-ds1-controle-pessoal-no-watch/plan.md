# Checkpoint 1 — Plano aprovado pelo Navigator em 2026-09-22

## Direção confirmada pelo Navigator
Uso enquanto joga; Galaxy Watch 8 Bluetooth; telefone prepara a sala; identificador `eli-smartwatch`, exibição pública `eli`; ver placar, +1 por equipe e desfazer; dois botões grandes; registrar offline; distribuição privada por APK de teste.

## Arquitetura proposta
- App nativo Kotlin / Compose para Wear OS, em módulo próprio no repositório. Versões de SDK e ferramentas serão verificadas ao iniciar a implementação.
- Reutilizar FastAPI, SQLite e log append-only como autoridade. HTTP autenticado para comandos e canal de estado autenticado para atualizações.
- Rede gerida pelo Wear OS, normalmente usando proxy Bluetooth do telefone; não exigir app Android acompanhante inicialmente. Preparação da sala continua no Svelte existente.
- Vínculo por código temporário mostrado no relógio e aprovado no telefone; credencial restrita, própria do dispositivo, revogável, armazenada com proteção da plataforma. URL do servidor será configurada na instalação de teste, sem embutir segredo.
- Identidade interna do dispositivo separada do nome público. Proposta: dispositivo vinculado ao participante Eli existente, contabilizando presença por participante com múltiplos dispositivos; perda de uma conexão não torna Eli ausente se outra estiver viva. Rever hub, sucessão e devolução de controle nessa integração.
- Autorizar a funcionalidade pessoal por mecanismo no servidor, sem confiar no texto `eli-smartwatch`; habilitação inicial controlada pelo operador da instância. Detalhar provisionamento sem expor o segredo de owner ao APK.
- Fila local transacional durável, comandos com identificador único e recibos persistidos atomicamente com eventos. Reenvio verifica duplicata antes de reaplicar efeitos, mantendo autenticação. IDs pertencem à credencial/sala/partida e payload divergente com mesmo ID é rejeitado.
- Desfazer referencia evento confirmado ou comando anterior da fila; projeção respeita regras de encerramento e reabertura.
- Reconciliação verifica estado-base e mudanças relevantes; presença isolada não deve criar conflito falso. Aplicações parciais têm recibos individuais e retomada determinística.

## Decisões aprovadas
1. Modelar o relógio como dispositivo de Eli, sem participante duplicado.
2. Em conflito real, preservar fila e revisar no telefone antes de aplicar/descartar; aprovado pelo Navigator.
3. Interface ativa com toque simples e desfazer visível; sem marcação em modo ambiente. Não manter tela permanentemente acesa por padrão. Validar ergonomia real antes de fechar.

## Alternativas consideradas
- Página web no relógio: não escolhida para o plano por depender de navegador, armazenamento e ciclo de vida menos controláveis para fila offline.
- App Android acompanhante / Data Layer: adiado; rede nativa permite testar o fluxo com o site existente. Reavaliar somente se teste no hardware demonstrar necessidade.
- Sincronizar cegamente pontos offline: rejeitado, pois pode duplicar contagem humana ou desfazer um lance concorrente.
- Criar conta privilegiada a partir do apelido: rejeitado; nome não é autenticação.

## Ordem e branches
Branch de planejamento: `feature/cv3-planejamento-controle-relogio`, criada de `master` em `638469d`.
Implementar sequencialmente US1, US2, US3 e US4, cada uma em branch própria a partir da master aceita, com checkpoints completos. US2 estabelece a gravação durável/idempotência necessária; US4 conclui reconciliação e revisão. Não anunciar entrega offline completa antes da US4. Cada HU terá plano técnico detalhado antes de código.
Primeira branch de implementação prevista: `feature/cv3-ds1-us1-vincular-relogio`.

## Versão
Intenção: `0.7.0`, minor por nova capacidade de controle no pulso. Não alterar versão durante planejamento. Limites intermediários de release serão definidos nos checkpoints das HUs. Em 2026-09-23 o Navigator fechou a `0.7.0` já na US1; as US2–US4 seguem como novas versões.

## Validação
- Backend: permissões, vínculo, expiração/revogação, identidade pública, múltiplas conexões, idempotência concorrente, ordem, desfazer dirigido, rollback, troca de partida e regras, sucessão/devolução e reinício.
- Frontend: verificações existentes e testes das novas superfícies de vínculo/revisão.
- Wear: testes de projeção/fila persistente/reabertura, build do APK e teste no hardware.
- Comandos existentes: `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`; em `web`, `npm test`, `npm run check`, `npm run build`. Comandos Android e instalação serão documentados após preparação do módulo.
- Roteiro integrado: telefone admin, Watch e navegador espectador; vincular, bloquear telefone, marcar A/A/B, desfazer e conferir 2×0; perder rede, marcar A/B, reabrir app, reconectar e conferir 3×1 sem duplicatas. Repetir com operador concorrente, revogação, sala expirada e partida nova: exigir aviso e nenhuma aplicação indevida.
- Passa: efeitos únicos e auditáveis, fila preservada, convergência após confirmação, controles utilizáveis no Watch real. Falha: perda silenciosa, duplicação, alteração de outro ponto/partida, permissão indevida ou dependência da página aberta para pontuar.

## Riscos e informações pendentes
- Modelo do celular e tamanho exato do Watch pendentes para instalação e ergonomia.
- Confirmar comportamento com telefone bloqueado, Bluetooth fora de alcance, suspensão do Wear OS e consumo de bateria. Não prometer sincronização imediata em background.
- Instalação Android/SDK e acesso ao relógio real ainda não verificados.
- Atualmente o controle retorna ao admin após ausência do controlador; reconciliação não pode contornar autorização vigente.
- README/briefing indicam 0.4.2, changelog fecha 0.6.1. Registrar a divergência na coerência e corrigir referências relevantes ao documentar a entrega, sem ampliar para revisão geral.

## Fora de escopo
Publicação em loja, suporte geral a outros usuários/relógios, botões físicos, gestos, configurações de partida no pulso e sincronização offline irrestrita entre múltiplos operadores.

## Fontes técnicas consultadas em 2026-09-22
- https://developer.android.com/training/wearables/data/network-communication — rede nativa, proxy via telefone e limites de background.
- https://developer.android.com/training/wearables/get-started/debug-wifi — instalação e depuração sem fio no dispositivo real.
