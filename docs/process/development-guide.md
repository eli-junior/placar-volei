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

# subir como roda no Mini PC
docker compose up -d --build
```

O `.env` é obrigatório para subir a aplicação. Ele guarda o segredo de owner e o caminho do arquivo SQLite. Existe um `.env.example` versionado; o `.env` real nunca é commitado.

## Verification

Trabalho verificado neste projeto significa as três coisas abaixo, não apenas a primeira.

**Verificação automatizada**

- `npm run check` sem erros no frontend.

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
