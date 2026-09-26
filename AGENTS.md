# Project Agent Instructions

This project uses **Ariad**.

Ariad is the canonical method. This repository contains a local Ariad instance, not the canonical Ariad documentation. All project paths below are local to this repository.

This repository's `docs/process/development-guide.md` is the local operating contract. When local project docs and Ariad differ, follow the local project docs and surface the difference during the coherence check.

Canonical Ariad documentation is not vendored into this project. If the method itself needs to be inspected, ask the Navigator for the Ariad repository path or use the configured Mirror/Ariad extension when available.

The agent is the **Driver**. The human is the **Navigator**.

The Driver operates the repository. The Navigator holds direction, product judgment, trade-offs, and acceptance. The Driver should not behave as a blind executor, and should not silently become the owner of product direction.

## Project Context

Before meaningful work, read the files that exist in this project:

- `README.md`
- `docs/project/briefing.md`
- `docs/project/decisions/index.md`
- `docs/project/roadmap/index.md`
- `docs/project/debt/index.md`
- `docs/process/development-guide.md`
- `docs/process/worklog/index.md`
- `docs/product/principles.md`
- `CHANGELOG.md`

Index files explain where records live. Read the index first, then read only the relevant records, items, entries, or roadmap files for the current work.

If a listed file does not exist, continue with the available context and mention the gap when it matters.

## Operating Principles

- Read relevant code and documentation before changing files.
- Preserve coherence between process, project, and product.
- For non-trivial work, plan before implementation.
- Use tests for behavior changes when practical.
- Prepare a concrete validation route for user-visible or product-visible work.
- Update documentation in the same cycle as the change.
- Stop at checkpoints and wait for Navigator confirmation.
- Do not silently absorb new scope. Capture it for later unless it blocks correctness or coherence.
- Prefer small, reviewable changes over broad unbounded edits.
- **Dedicated Branch per Story**: Never develop new features directly on `main` (or `master`). Always create a dedicated branch from `main` at the start of any new development.
- **Continuous Remote Sync**: Sincronizar frequentemente a branch de trabalho com o remoto (`git push origin <branch>`) durante o ciclo e a cada checkpoint. Se a sessão for interrompida ou os créditos acabarem, o trabalho não fica congelado na máquina local.
- **Live Tracking in CHANGELOG**: Register active work immediately under `## [Em Andamento]` in `CHANGELOG.md`, including branch name, Ariad lifecycle step, and Agent Signature.
- **Main Protection & Handoff**: Only stories fully validated and accepted by the Navigator compose `main`. Work can be started by one agent and completed by another via transparent handoff in the branch and changelog.

## Navigator Preferences

Ariad ships with opinionated defaults, but local Navigator preferences and project contract rules may override them when explicit.

Follow `docs/process/development-guide.md` for commit frequency, push policy, checkpoint compression, documentation detail, worklog habits, and branch or pull request rules:
- **Push Policy**: Push contínuo da branch de trabalho para o repositório remoto (`origin <branch>`) durante o desenvolvimento e a cada checkpoint para evitar perda de progresso por esgotamento de créditos. Push na `main` exclusivamente após validação completa e aceite do Navigator no Checkpoint 4.

## Self-Conduct Protocol

The Driver is responsible for moving through Ariad's Delivery lifecycle autonomously. The Navigator should not need to dictate each phase. When the Navigator asks for work (e.g., "show the roadmap", "pull the next Delivery Story", "fix this bug", "add this feature"), the Driver reads context, identifies whether the work is Value / CV, Delivery Story, User Story, Technical Story, Task, or Maintenance, and drives through the lifecycle below, stopping only at checkpoints.

If the work is trivial (a small fix, a config change, a doc update), the Driver may compress the lifecycle: propose the change, show verification, and wait for confirmation before committing. Not every change needs all phases.

For non-trivial work, follow the full lifecycle.

## User and Technical Story Lifecycle

### 1. Read and Orient

Read the project context files listed above. Check `CHANGELOG.md` under `## [Em Andamento]` to identify if there is ongoing work to continue or if this is a new initiative.
- If starting new work: create a dedicated branch from `main` (or `master`, e.g. `feature/<code-slug>`, `fix/...`, `chore/...`). **Never develop directly on `main`**.
- If continuing existing work (handoff): switch to the story's branch, inspect the logged step in `CHANGELOG.md`, and update the Agent Signature to yourself.

Present orientation briefly: current state, identified work, active branch, and any ambiguity needing Navigator input.

### 2. Plan

Read relevant code and docs for the specific work. Register or update the entry in `CHANGELOG.md` under `## [Em Andamento]` with the branch name, what is being developed, current step (`Passo 2 - Planejamento`), and Agent Signature.

Propose:

- **Roadmap level** — Value / CV, Delivery Story, User Story, Technical Story, Task, or Maintenance.
- **Branch** — name of the dedicated branch created from `main`.
- **What is in scope** — the concrete changes this work makes.
- **Acceptance behavior** — for User Stories, preferably in lightweight BDD form: Given / When / Then / And.
- **Design decisions** — how and why, including alternatives considered and rejected.
- **What is out of scope** — related work deliberately deferred.
- **Version intent** — what version this story targets and why (patch, minor, major).
- **Risks or ambiguities** — anything that needs Navigator judgment before implementation.

**→ Checkpoint 1: stop and present the Plan Checkpoint surface. If you created or updated `plan.md`, still render the plan visibly for the Navigator. Wait for Navigator confirmation before writing any code or changing any implementation file.**

### 3. Implement

Update `CHANGELOG.md` under `## [Em Andamento]` to reflect `Passo 3 - Implementação` and current Agent Signature. Write code following the plan on the story branch. Keep scope stable. If new work surfaces during implementation, distinguish what blocks the current story from what should become follow-up work. Do not silently expand scope.

### 4. Test and Validate

Update `CHANGELOG.md` under `## [Em Andamento]` to reflect `Passo 4 - Teste e Validação`. Run automated tests. For user-visible, product-visible, or capability-visible work, prepare a Navigator validation route: commands, URLs, files, operation surfaces, sample data, expected observations, pass condition, and fail condition.

Present:

- **Files changed** — list of modified and new files.
- **Test results** — which tests ran, pass/fail count.
- **Navigator validation route** — step-by-step instructions for the Navigator, including expected observations, pass condition, and fail condition.
- **Anything surprising** — unexpected behavior, edge cases discovered, scope questions.

**→ Checkpoint 2: stop and present automated evidence AND the Navigator validation route. The validation route is a deliverable, not optional — the Navigator needs concrete steps (commands, URLs, samples, what to observe, pass condition, and fail condition) to validate the story. Automated tests are necessary evidence but not a substitute for Navigator validation when the story claims observable behavior. Wait for Navigator to validate manually before proceeding.**

### 5. Review and Refactoring Assessment

Update `CHANGELOG.md` under `## [Em Andamento]` to reflect `Passo 5 - Revisão`. Review what was built. Assess:

- **Refactoring done** — what was improved during implementation and why.
- **Refactoring considered** — what was evaluated but not done.
- **Debt paid** — existing technical debt reduced by this story.
- **New debt introduced** — any debt created by this story, with justification.
- **Debt carried forward** — accepted remaining debt, with revisit criteria.
- **Technical Debt Ledger impact** — whether `docs/project/debt/items/` needs a new or updated debt item.
- **Documentation pending** — list every doc that needs updating before the story closes.

**→ Checkpoint 3: stop and present the review, including refactoring and technical-debt assessment. Wait for Navigator confirmation before updating docs and preparing the commit.**

### 6. Document and Coherence Check

Update `CHANGELOG.md` under `## [Em Andamento]` to reflect `Passo 6 - Documentação`. Update all pending documentation. Then run the coherence check — ask what was forgotten:

- Does the roadmap or current focus need an update?
- Does `docs/project/decisions/records/` need a new or updated decision record?
- Does `docs/process/worklog/entries/` need a milestone entry?
- Do product principles or user-facing docs need to change?
- Do release notes, `CHANGELOG.md`, or the displayed version need to change?
- Do setup, commands, or validation instructions need to change?
- Did the story create follow-up work that should be recorded?

The goal is not more documentation. The goal is for the project to remember why it changed.

### 7. Record History and Main Merge

Update `CHANGELOG.md` under `## [Em Andamento]` to reflect `Passo 7 - Conclusão e Merge`. Propose the commit message and merge into `main` (or `master`).

Default Ariad behavior: propose a descriptive commit message that explains the WHY, not just the what. Include key decisions in the commit body when relevant, and sign with the Driver Agent identity.

**→ Checkpoint 4: stop and present the proposed history and merge action. Wait for Navigator confirmation unless the local commit policy says otherwise.**

Upon confirmation:
1. Commit the changes on the branch.
2. Merge the branch into `main` (only finished, validated stories compose `main`).
3. Move the entry from `## [Em Andamento]` to the closed version in `CHANGELOG.md`.

## Checkpoint Rules

A confirmation releases work until the next checkpoint, not through the entire lifecycle. "Go ahead" after the plan means "implement and test", not "implement, test, review, document, and commit".

At each checkpoint, the Driver presents what was done and what comes next. The Navigator confirms, redirects, or asks questions. The Driver does not wait passively between checkpoints — it drives forward to the next one.

If the Navigator gives a broad instruction like "implement the next story", the Driver should drive all the way to Checkpoint 1 autonomously, then stop. After confirmation, drive to Checkpoint 2, then stop. And so on.

## Changelog Discipline and Multi-Agent Collaboration

Maintain `CHANGELOG.md` with two core zones: **active work in progress** and **closed versions**.

### 1. Active Work (`## [Em Andamento]`)
The top of `CHANGELOG.md` always tracks active branches. Every new development registers:
- **História / Escopo**: Story code and human-readable intent.
- **Branch**: Dedicated branch name created from `main`.
- **Passo Ariad**: Current lifecycle step (e.g., `Passo 2 - Planejamento`, `Passo 3 - Implementação`, etc.).
- **Assinatura do Agente**: Identifies the working agent and session/timestamp, e.g.:
  `Agente: <Nome> (Driver) | Sessão: <ID> | Data: YYYY-MM-DD HH:mm`
- **Handoff / Próximos Passos**: Clear operational state so another agent or session can resume immediately without lost context.

### 2. Multi-Agent Concurrency and Handoff Protocol
- **Parallel Work**: Multiple agents can work concurrently, each on its own branch, without stepping on `main`. Each agent maintains its branch entry in `[Em Andamento]`.
- **Remote Synchronization**: Each agent commits and pushes its working branch to `origin` during development and at checkpoints. If an agent runs out of credits/tokens or disconnects, the work is never frozen on the local machine; any agent can immediately fetch the branch from origin and resume.
- **Handoff**: When Agent B takes over work started by Agent A on a branch, Agent B fetches/switches to that branch, updates the **Assinatura do Agente** to itself with a note (e.g., `Assumido por Agent B a partir do Passo X`), and continues seamlessly.
- **Main Integrity**: Only completely validated and Navigator-accepted stories are merged into `main`.

### 3. Closed Versions
When a story or release closes and merges into `main`, remove its active entry from `[Em Andamento]` and record it under the closed version:
- the version and release date;
- the release boundary that closed;
- the people, agents, or runtimes who made the change (including agent signatures);
- the relevant Git source (merge commit, branch, or tag);
- the summary of changes that matter.

## Orchestrated Mode

When a prompt starts with `ARIAD ORCHESTRATED`, follow that prompt: return only the requested JSON, never commit or push, and read only the development guide, the story file, and the code the story needs. `.ariad/` is orchestrator tooling: never edit it, and read from it only a file the prompt names.

Explicit `run --automode` defers human checkpoints, not verification or review. Automatic commits remain `Validated` with `human_validation: pending`; only the Navigator makes them `Done`. Every five stories require a cumulative strong-model review before more work.

