# Local Development Guide

This is the project-specific operating contract for agentic development.

Ariad is the canonical method. This file is the local instance of that method for this repository. It explains how the Driver and Navigator should work here, which commands matter, what validation means, and which project-specific rules override generic guidance.

Keep this file practical. It should help a future agent work correctly in this project without asking the Navigator to repeat the same context every session.

## Relationship to Ariad

This project uses Ariad as its human-agent development method.

When Ariad and this local guide differ, follow this local guide for project-specific work and surface the difference during the coherence check.

## Driver and Navigator

The agent is the **Driver**. The human is the **Navigator**.

The Driver reads context, proposes plans, changes files, runs checks, prepares validation routes, updates documentation, and stops at checkpoints.

The Navigator holds intent, trade-offs, product judgment, and acceptance.

## Project Commands

Comandos verificados na entrega da `CV1.DS1.TS1`. A seção de frontend e docker compose será confirmada em suas respectivas stories.

```bash
# instalar dependências
uv sync

# rodar testes
uv run pytest

# lint e formatação
uv run ruff check .
uv run ruff format --check .

# rodar o backend localmente
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# frontend (Svelte 5)
cd web && npm install
cd web && npm run dev      # dev server com proxy para o backend
cd web && npm run build    # gera os estáticos servidos pelo FastAPI
cd web && npm run check    # svelte-check
cd web && npm run test:e2e # build + Playwright/axe (sobe o FastAPI com SQLite descartável)
uv run python -m tests.paridade_fixtures # regera as fixtures de paridade Python↔JS (CV7.TS2)

# subir como roda no Mini PC
docker compose up -d --build
```

O `.env` é obrigatório para subir a aplicação. Ele guarda o segredo de owner e o caminho do arquivo SQLite. Existe um `.env.example` versionado; o `.env` real nunca é commitado.

Desde a `CV5.DS1.TS2`, o `docker compose` recusa subir sem `OWNER_SECRET`, e o app (com `PRODUCAO=true`) recusa o valor de exemplo. Para gerar um segredo: `openssl rand -base64 32`.

O banco é efêmero por decisão do Navigator: com `RESET_DB_ON_STARTUP=true` no compose, **todo start do contêiner** (deploy, `restart` ou reinício após falha) apaga salas, participantes e vínculos do relógio. Depois de cada start, é preciso recriar a quadra e parear o relógio de novo. `COOKIE_SECURE=true` (padrão no compose) exige HTTPS; o acesso é pelo túnel.

**Exceção durável (CV8.DS1.US1):** a base de jogadores mora em `gerenciador.db` (`GERENCIADOR_DB_PATH`), no volume nomeado `gerenciador-dados` (`/data-gerenciador`). Ela **sobrevive** ao `RESET_DB_ON_STARTUP`, a mudanças de schema das quadras e a `docker compose up --force-recreate`; só `docker compose down -v` (ou `docker volume rm`) a apaga. Não rode `down -v` sem autorização do Navigator. Mudanças de schema nela são migrações aditivas (`PRAGMA user_version`). A tela `/jogadores` exige o `OWNER_SECRET` e fica oculta no APK. Desde a 0.32.0 o arquivo está na versão de schema 2 (coluna `nota`, tabela `jogador_fotos`); a migração roda sozinha na subida e é idempotente. Fotos são JPEG de até 256 KB, guardadas como BLOB no mesmo arquivo — entram no backup do `gerenciador.db`. Desde a 0.33.0 o schema é a versão 3 (tabelas `sessoes` e `presencas`; uma sessão aberta por vez garantida por índice único parcial); as rotas `/api/sessao` e a tela do Joguinho (`/joguinho`, desde a 0.46.5; `/sessao` é o endereço antigo e redireciona) seguem o mesmo `OWNER_SECRET` e ficam ocultas no APK.

Desde a 0.34.0 o schema é a versão 4 (tabelas `rodadas`, `times` e `time_jogadores`; uma rodada em proposta ou em andamento por sessão, por índice único parcial). O sorteio mora em `app/sorteio.py` (puro, determinístico) e as regras da rodada em `app/rodada.py`; as rotas `/api/rodada/*` ficam em `app/sessao.py`. Conexão, esquema e erros comuns estão em `app/gerenciador_db.py`.

Desde a 0.35.0 o schema é a versão 5 (`sessoes.quadra_id` e a tabela `partidas_rodada`). A ponte com o placar está em `app/ponte.py`: o gerenciador guarda o código de uma quadra do placar e age como o ADMIN dela (via `executar_sync` com `autor_id`). Como o banco das quadras é efêmero e o do gerenciador não, o vínculo pode ficar "indisponível" depois de um reinício; é esperado. A sincronia entre aparelhos usa o WebSocket `/ws/gerenciador` (`app/sincronia.py`, hub próprio), com o `OWNER_SECRET` na primeira mensagem.

Desde a 0.36.0 as rotas da rodada estão todas em `app/rodada_rotas.py`. O encerramento de partida lê o placar da quadra vinculada (`ler_placar` em `app/ponte.py`) e só aceita uma partida terminada; cada evento da quadra vinculada avisa o gerenciador (`avisar_placar` em `app/sincronia.py`, chamado por `transmitir_estado`), o que mantém o placar ao vivo no painel. Não há migração de schema nesta versão (continua a versão 5).

Desde a 0.37.0 o schema é a versão 6 (`times.origem` e `time_jogadores.escalado`). A lista de escalação e o saldo da rodada são funções puras em `app/conducao.py`; `app/rodada.py` monta o painel e valida a escolha do parceiro na transação (`POST /api/rodada/escalar-parceiro`).

Desde a 0.38.0 o schema é a versão 7 (`rodadas.mata_mata_em`, `rodadas.campeao_time_id`, `partidas_rodada.fase`). O mata-mata é derivado em `app/conducao.py` (`derivar(..., mata_mata_iniciado)`); `POST /api/rodada/iniciar-mata-mata` o inicia e `registrar_campeao` (em `app/rodada.py`) encerra a rodada ao fim do último confronto.

Desde a 0.39.0 toda conexão do gerenciador grava com `PRAGMA synchronous=FULL` (o resultado de uma partida não se perde numa queda). **O que fica persistido:** a cada ação, na mesma transação, ficam gravados sessão, presenças, rodada (estado, `mata_mata_em`, `campeao_time_id`), times com os jogadores (nota e chegada do sorteio, marca de escalado) e cada partida (fase, placar, vencedor, horários de chamada e encerramento). Só a proposta de rodada descartada ou resorteada é apagada; cancelar a rodada ou encerrar a sessão mantém as partidas. Não há tela de histórico; `tests/test_persistencia.py` guarda esse contrato para o ranking futuro.

Desde a 0.46.3 a quadra de uma rodada `em_andamento` não expira por TTL: `ponte.manter_quadras_da_rodada` renova o `atualizado_em` dela na subida e a cada ciclo da limpeza (`min(300 s, QUADRA_TTL_SECONDS/2)`), sem mexer na regra do TTL. Todo estado do joguinho (`_estado` em `app/sessao.py`) passa por `ponte.reconciliar_vinculo`: vínculo com quadra que não existe mais é limpo, exceto com partida chamada (aí fica "indisponível" e a saída é anular). O reinício do contêiner continua apagando as quadras (decisão de 2026-09-27); o que mudou é o joguinho se reconciliar sozinho. Para validar sem esperar 1 h, suba com `QUADRA_TTL_SECONDS=60`.

Desde a 0.46.4 o aparelho só esquece o segredo do dono quando o servidor o recusa: **404 sem `erros`** (o mascarado de `validar_segredo_owner`) ou WebSocket fechado com **4401**. 404 com `erros[]` é erro de domínio; 429 (HTTP, com `Retry-After`) e **4429** (WebSocket) são bloqueio por tentativas e mantêm o segredo salvo. Requisição sem segredo (cabeçalho ausente ou vazio, ou primeira mensagem do WebSocket sem segredo) devolve o mesmo 404, mas não conta como tentativa no bloqueio por IP. No cliente, `ErroJogadores.recusado` é o único gatilho de `sair()`. Para validar o bloqueio sem esperar, 5 tentativas com segredo errado bloqueiam o IP por 5 min.

Desde a 0.46.5 as telas do app têm um mapa único em `web/src/lib/rotas.js` (`resolverRota`): `/` e `/index.html` (início), `/quadra/<id>`, `/joguinho` (e `/sessao`, que vira `/joguinho` por `replaceState`, preservando `?query` e `#hash`) e `/jogadores`; a barra final é ignorada. Qualquer outro caminho mostra "Página não encontrada" (`PaginaNaoEncontrada.svelte`); no APK só o início e a sala existem. O servidor continua devolvendo o SPA (200) para caminhos fora de `/api/*`; **uma tela nova precisa entrar nessa tabela**, senão cai em "não encontrada".

Desde a 0.47.0 `POST /api/sessao/encerrar` aceita o corpo opcional `{"cancelar_rodada": true}`: com rodada ativa, descarta a proposta ou cancela a rodada em andamento (apagando a partida chamada) e fecha o joguinho na mesma transação; sem o corpo (ou com `false`) o 409 `rodada_ativa` de sempre continua, então scripts e o MCP não mudam. A tela chama o botão de **Encerrar joguinho** e, com rodada ativa, a confirmação lista o que se perde (`web/src/lib/joguinho.js`, `oQueSePerde`) e vira **Cancelar rodada e encerrar**. Joguinho aberto em dia anterior (calendário do aparelho, `joguinhoVelho`) mostra um cartão com **Continuar** (guardado por aparelho e por id da sessão em `placar:joguinho_velho_visto`) ou **Encerrar**. Para testar o aviso sem esperar um dia, mude a data do aparelho ou, no e2e, `page.clock.setFixedTime`.

Desde a 0.48.0 o `gerenciador.db` está no schema 11 (tabela `ajustes_fila`, aditiva) e a condução tem duas ações novas, ambas do dono e só com rodada `em_andamento`: `POST /api/rodada/retirar` `{"jogador_id"}` (tira o jogador de todos os times dele e da presença; 409 `em_jogo` se o time tem partida chamada, 409 `fora_da_rodada` se ele não está na rodada) e `POST /api/rodada/pular-time` (manda o time com vaga e sem elegível para o fim da fila; 409 `ha_elegiveis`, `sem_incompleto` ou `sem_outro_time`). Time que fica sem jogadores e o "pular" são gravados como ajustes datados (`apos_partidas`) que `conducao.derivar` aplica na reconstrução; veja o registro `time-vazio-e-pular-viram-ajustes-da-fila`. A primeira subida em produção deve seguir o backup automático do `gerenciador.db`.

Desde a 0.49.0 o `gerenciador.db` está no schema 12 (coluna `rodadas.triangular`, aditiva; a migração roda sozinha e é idempotente). Com exatamente 3 times completos a rodada é triangular (RN-18): `rodada.confirmar` grava a marca e `conducao.derivar(..., triangular=True)` deriva o desfecho (fase nova `sem_rei`). A rota `POST /api/rodada/encerrar-sem-campeao` (só do dono, rodada `em_andamento`) fecha a rodada sem campeão quando ela terminou sem rei ou travou numa vaga sem elegível; fora desses estados responde 409 `fora_do_sem_rei`. Numa rodada triangular `POST /api/rodada/atrasado` responde 409 `rodada_triangular`. Veja o registro `rodada-triangular-de-3-times`.

Desde a 0.49.1 a quadra **vinculada** a um joguinho aberto segue o joguinho: `POST /api/quadras/{id}/reiniciar` e a mudança de `alvo`/`vantagem`/`teto` em `/configurar` respondem 409 (a chamada do joguinho passa `via_joguinho` e continua zerando o placar), e o snapshot da quadra traz `em_joguinho` (a web esconde os reinícios e a configuração de pontos e vantagem). O fim da partida só oferece o Próximo jogo: `POST /api/quadras/{id}/proximo-jogo` (ADMIN da quadra vinculada, sem `OWNER_SECRET`) encerra a partida chamada, se houver, e chama a próxima. Desvincular ou encerrar o joguinho devolve a quadra ao uso livre.

### Backup e restauração do `gerenciador.db` (CV8.TS1)

- **Automático:** o app grava uma cópia verificada na subida e a cada `GERENCIADOR_BACKUP_INTERVALO_HORAS` (6), mantendo as `GERENCIADOR_BACKUP_MANTER` (28) mais recentes. No compose, a pasta é `./backups` do host, montada em `/backups`, **fora** do volume `gerenciador-dados`. Sem `GERENCIADOR_BACKUP_DIR` o backup fica desligado (aviso no log). Falha de backup é logada e não derruba o app; uma cópia que falha na verificação nunca substitui nem faz podar as boas.
- **Primeira vez no Mini PC:** `mkdir backups && sudo chown 1001:1001 backups` (o contêiner roda como uid 1001). Sem isso o log mostra `Falha no backup do gerenciador: ... Permission denied`.
- **Sob demanda:** `docker compose exec placar python -m app.backup agora` (e `listar`).
- **Restaurar (com o app parado):**
  ```bash
  docker compose stop placar
  docker compose run --rm placar python -m app.backup restaurar /backups/<arquivo>.db
  docker compose up -d placar
  ```
  O banco atual fica como `gerenciador.db.antes-<data>` ao lado. Para **ensaiar** sem tocar no real: `... restaurar /backups/<arquivo>.db --destino /tmp/ensaio.db`.
- **Cuidado:** as cópias guardam fotos e dados dos jogadores; trate a pasta `backups/` como o volume. Ela é ignorada pelo git. Para levar as cópias a outro lugar (nuvem, outro disco), copie a pasta com `rsync`/`rclone`; isso fica fora do app.

## Aparelhos físicos (celular e relógio)

Para parear, conectar, compilar, instalar, capturar a tela, tocar e ler o log nos aparelhos físicos, **use o MCP `dispositivos`** (`tools/mcp-dispositivos/`, registrado no `.mcp.json`; ver o README dele), e não comandos de `adb` soltos. Ele já trata as armadilhas deste projeto: celular sempre com `--user 0` (Dual App do Samsung), release que não atualiza debug, porta do `adb` sem fio que muda, relógio que dorme, duas telas do Z Fold. Atalho para "gerar um APK novo e instalar": `compilar_e_instalar`.

Regras que valem com ou sem o MCP: nunca contornar o bloqueio de tela (peça ao Navigator para desbloquear); desinstalar um app apaga os dados dele (quadra local, vínculo), então só com autorização; o release do celular e do relógio precisam da mesma keystore.

## Verification

Trabalho verificado neste projeto significa as três coisas abaixo, não apenas a primeira.

**Verificação automatizada**

- `npm run check` sem erros no frontend.
- `npm run test:e2e` verde em mudança de interface: fluxos em navegador real, axe nos dois temas e ausência de requisições externas.

- `uv run pytest` verde.
- Toda mudança de comportamento tem teste. Regra de pontuação, projeção de eventos e permissão de papel não entram sem teste.
- A projeção do log é testada por sequência de eventos, incluindo pontos e desfazimentos intercalados, e precisa ser determinística: rodar duas vezes sobre o mesmo log produz o mesmo estado.

**Validação multi-dispositivo**

Este produto é sobre estado compartilhado. Validar numa aba só não prova nada.

- Toda User Story com efeito visível é validada em **pelo menos dois clientes simultâneos** (dois navegadores, um deles anônimo, ou dois celulares).
- Stories que envolvem presença, papéis ou sucessão exigem **três** clientes.
- A rota de validação da story precisa nomear o que observar em cada tela, a condição de aprovação e a condição de falha.

**Resiliência**

- Stories que tocam estado de partida são validadas com um restart do processo no meio (`docker compose restart`), confirmando que o placar volta idêntico.
- Stories que tocam conexão são validadas com um cliente em modo avião por ~30 segundos, confirmando reconciliação sem recarregar a página.

**Interface**

- Story com efeito visível não fecha sem a animação correspondente. A rota de validação precisa nomear qual transição observar.
- Validar com `prefers-reduced-motion` ativo: a informação continua legível sem o movimento.
- Validar em tela de celular real, não apenas no emulador de largura do navegador.

**Segurança**

- Toda restrição de papel é testada **contra o backend**, não contra a UI. Esconder o botão não é controle de acesso: a validação precisa incluir uma chamada forjada a partir de um cliente sem permissão.
- Antes de fechar qualquer story que toque o canal de owner: `grep` no log da aplicação procurando o segredo do `.env`. Aparecer é falha.

**Banco**

- O SQLite de desenvolvimento é descartável. O arquivo de produção no Mini PC nunca é alterado manualmente pelo Driver.
- Nenhuma migração destrutiva sobre o log de eventos. O log é append-only, inclusive em migração.

## Documentation Rules

Describe when documentation must be updated.

Common documentation surfaces:

- `README.md`
- `docs/project/briefing.md`
- `docs/project/decisions/index.md` and `docs/project/decisions/records/`
- `docs/project/roadmap/index.md` and roadmap item folders
- `docs/project/debt/index.md` and `docs/project/debt/items/`
- `docs/process/worklog/index.md` and `docs/process/worklog/entries/`
- `docs/product/principles.md`
- `CHANGELOG.md`

## Conflict-Resistant Project Memory

Use one file per durable artifact when the surface may be edited by multiple people or agents.

- Worklog milestones live in `docs/process/worklog/entries/`.
- Decision records live in `docs/project/decisions/records/` and use `status` for open or decided lifecycle state.
- Debt items in the Technical Debt Ledger live in `docs/project/debt/items/`.
- Roadmap items own their current `status` in frontmatter or in their own file, not in a central table.

Index files explain structure, naming, and templates. They should not maintain complete lists of every artifact unless this project explicitly accepts that coordination cost.

Prefer status metadata over directory moves for lifecycle state. Directory moves are acceptable for archival or deliberate reorganization, but state should remain explicit in the artifact so links and history stay understandable.

## Roadmap Taxonomy

Use Ariad's default taxonomy unless this project explicitly adapts it:

- Value / CV: major delivery stage with clear impact.
- Delivery Story: coherent delivery arc inside a Value / CV.
- User Story: atomic user-observable delivery that can be verified end to end through observable behavior or capability. For non-UI work, the validation route may be a dry-run, diagnostic, operation report, generated artifact, documented policy, runtime state, or other inspectable output.
- Technical Story: internal capability needed by a Delivery Story, still verified but not necessarily Navigator-visible by itself.
- Task: concrete work inside a User Story or Technical Story.
- Maintenance: legitimate work that may sit outside roadmap structure.

Do not inflate maintenance into the roadmap just to make it visible.

Use Ariad's default new-work codes unless this project explicitly adapts them: `CV<N>` for Values, `DS<N>` for Delivery Stories, `US<N>` for User Stories, and `TS<N>` for Technical Stories. Roadmap folders should use lowercase slugs such as `cv9-ds7-conversation-metadata-lifecycle` and child folders such as `cv9-ds7-us1-dry-run-metadata-lifecycle-decision-path`.

Use Ariad's default roadmap states unless this project explicitly adapts them: `Planned`, `Active`, `Blocked`, `Validated`, `Done`, `Deferred`, and `Dropped`. Store state in the roadmap item's own metadata or status section. When work cannot proceed, prefer `Blocked` with a reason over runtime warning labels such as `Attention`.

## Expand and Collapse

Use expand when work is blocked by ambiguity: separate concerns, name options, clarify scope, or expand a Delivery Story into User Stories.

Use collapse when work is lost in fragments: relate parts, update status, name emergent value, close a User Story or Technical Story, close a Delivery Story, or prepare a release boundary.

## User and Technical Story Lifecycle

For non-trivial work, follow the Ariad lifecycle:

- plan,
- name User Story acceptance behavior, preferably as Given / When / Then / And,
- implement,
- test and validate,
- document,
- review and coherence check,
- record project history according to the configured commit policy.

Add any project-specific story rules here.

## Technical Debt Tracking

Use the Technical Debt Ledger at `docs/project/debt/`, with debt items in `docs/project/debt/items/`, when debt should outlive one story's review notes.

During Review, name:

- debt paid;
- new debt introduced;
- debt carried forward;
- revisit trigger;
- whether a debt item should be created or updated in the Technical Debt Ledger.

Small local debt can be captured as follow-up. Debt that may affect future delivery, safety, maintainability, validation, operation, or product coherence should enter the ledger.

## Checkpoints

Stop for Navigator confirmation:

- after the Plan Checkpoint surface is shown; creating `plan.md` does not replace the visible checkpoint,
- after automated checks, with a concrete Navigator validation route that includes expected observations, pass condition, and fail condition,
- after review and refactoring assessment,
- before recording project history unless the local commit policy says otherwise.

Add any project-specific checkpoint rules here.

## Navigator Preferences

Ariad ships with opinionated defaults. Override them here when this project or Navigator has a better local answer.

- **Commit policy:** commit ao final de cada User ou Technical Story validada e aceita. Mensagem em português, explicando o porquê e identificando o agente Driver.
- **Push policy:** push contínuo e frequente da branch de trabalho para o repositório remoto (`origin <branch>`) durante o desenvolvimento e a cada checkpoint. Desta forma, se os créditos do agente se esgotarem ou a sessão for interrompida, o progresso não fica congelado na máquina local e outro agente pode assumir imediatamente pelo remote. Push na branch principal (`main`/`master`) ocorre exclusivamente após validação final e aprovação do Navigator no Checkpoint 4.
- **Checkpoint compression:** checkpoints completos para User e Technical Stories. Compressão permitida apenas para correção trivial, ajuste de configuração ou edição de documentação.
- **Documentation detail:** a menor atualização que mantém o projeto coerente. Documentação é atualizada no mesmo ciclo da mudança, nunca depois.
- **Worklog policy:** uma entrada por marco significativo — fechamento de Delivery Story, decisão relevante, mudança de rumo. Não uma entrada por commit.
- **Branch/PR habits:** sempre criar uma branch dedicada a partir da branch principal (`main` ou `master`) ao iniciar qualquer novo desenvolvimento (ex.: `feature/<codigo-slug>`, `fix/...`, `chore/...`). Trabalho direto na branch principal é proibido para novos desenvolvimentos. A `main` só recebe código finalizado e validado após aceitação no Checkpoint 4.
- **Changelog ativo:** manter registro obrigatório na seção `## [Em Andamento]` do `CHANGELOG.md` contendo a branch ativa, história, passo atual do ciclo Ariad, assinatura do agente e notas de handoff.
- **Assinatura do agente:** toda história ativa no changelog e mensagens de commit devem conter a identificação do agente (ex.: `Agente: <Nome> (Driver) | Sessão: <ID> | Data: YYYY-MM-DD HH:mm`).
- **Idioma:** documentação de projeto, mensagens de commit e comentários em português. Código, nomes de identificadores e nomenclatura estrutural do Ariad (`status`, `CV`, `DS`, `US`, `TS`, `Planned`, `Active`, `Done`) em inglês.
- **Escopo:** o Navigator é Product Owner de profissão e decide produto. O Driver propõe trade-offs técnicos, mas não fecha decisão de produto sozinho — registra como decisão `Open` e pergunta.

## Commit and Release Rules

Branches de trabalho nascem a partir da branch principal (`main` ou `master`).

Durante o ciclo de desenvolvimento, o agente Driver deve realizar commits parciais na branch e sincronizá-la frequentemente com o repositório remoto (`git push -u origin <branch>`), garantindo persistência remota contra esgotamento de créditos ou interrupção de contexto.

O trabalho ativo é registrado e atualizado na seção `## [Em Andamento]` do `CHANGELOG.md` a cada avanço no ciclo Ariad (Planejamento, Implementação, Validação, Revisão, Documentação, Merge).

Somente histórias completamente testadas, validadas com o Navigator e aprovadas compõem a branch principal (`main`).

Quando uma história ou versão é finalizada:
1. O commit na branch é consolidado com mensagem descritiva e assinatura do agente;
2. O merge é realizado na branch principal (`main`);
3. O bloco correspondente é removido de `## [Em Andamento]` e adicionado à seção da versão fechada correspondente no `CHANGELOG.md`;
4. O changelog da versão fechada registra versão, data, fronteira (Value, Delivery Story, etc.), fontes Git e os autores/agentes envolvidos.

## Local Exceptions

Desvios deliberados em relação ao Ariad ou a hábitos comuns de engenharia.

### Documentação de projeto em português

O Ariad e seus templates são em inglês; os documentos deste projeto são em português.

Motivo: o Navigator opera em português e a clareza da regra de negócio vale mais que a uniformidade com o método canônico. A nomenclatura estrutural do Ariad permanece em inglês para não quebrar buscas por `status: Active` e afins.

Revisitar se o projeto ganhar colaboradores que não falem português.

### Seção [Em Andamento] no changelog e branches por história

Desvio em relação ao Ariad padrão (que recomenda apenas versões fechadas no changelog e trabalho em branch única para desenvolvedor solo):

O projeto adota obrigatoriamente branches separadas para cada desenvolvimento e mantém a seção `## [Em Andamento]` no topo do `CHANGELOG.md`.

Motivo: permitir o trabalho concorrente de múltiplos agentes de IA (ex.: Claude, Antigravity), viabilizar o handoff transparente (um agente inicia e outro conclui a história sabendo exatamente em qual passo ela está) e proteger a integridade da branch principal (`main`), garantindo que apenas entregas prontas e validadas cheguem a ela.
