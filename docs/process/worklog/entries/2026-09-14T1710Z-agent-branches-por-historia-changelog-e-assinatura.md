---
date: 2026-09-14T17:10:00Z
author: Antigravity (Driver)
kind: milestone
related:
  - docs/process/development-guide.md
  - AGENTS.md
  - CHANGELOG.md
  - docs/project/decisions/records/2026-09-14T1710Z-branches-por-historia-registro-changelog-e-assinatura-de-agentes.md
verification:
  - revisao de coerencia com AGENTS.md e development-guide.md
  - secao [Em Andamento] ativa e estruturada no CHANGELOG.md
  - adr registrado em docs/project/decisions/records/
---

# Governança do Ariad: Branches Dedicadas por História, Tracking Ativo no Changelog e Assinatura de Agentes

## What changed

- **Branches Dedicadas a Partir da Main:**
  - Atualização dos princípios operacionais e regras do Ariad em `AGENTS.md` e `docs/process/development-guide.md`.
  - Proibido o trabalho direto na branch principal para novas histórias.
  - Toda nova tarefa deve nascer em uma branch dedicada a partir de `main` (ou `master`).
  - A branch principal passa a receber apenas histórias finalizadas e validadas com o Navigator.

- **Tracking em Tempo Real no `CHANGELOG.md` (`## [Em Andamento]`):**
  - Criação de uma seção dedicada no topo de `CHANGELOG.md` para monitoramento em tempo real de todas as branches ativas.
  - Cada entrada registra: branch, código e objetivo da história, passo atual no ciclo Ariad (Passo 1 a Passo 7), assinatura do agente e notas operacionais de handoff.
  - Ao finalizar e integrar o código na main, o registro é transferido de `[Em Andamento]` para a versão fechada correspondente.

- **Assinatura de Agentes e Handoff Seguro:**
  - Todo trabalho ativo no changelog e commits de branch deve conter a assinatura do agente responsável (`Agente: <Nome> (Driver) | Sessão: <ID> | Data: <Timestamp>`).
  - Permite que múltiplos agentes (ex.: Claude, Antigravity) trabalhem simultaneamente em branches separadas ou assumam a mesma branch em handoff transparente, bastando atualizar a assinatura no changelog e continuar do passo indicado.

- **Sincronização Remota Contínua (Push Policy):**
  - O agente Driver deve dar push contínuo de sua branch para `origin` durante o ciclo e a cada checkpoint, evitando que o progresso fique congelado localmente caso a sessão caia ou os créditos de IA se esgotem.

- **Registro de Decisão Arquitetural (ADR):**
  - Registrado em `docs/project/decisions/records/2026-09-14T1710Z-branches-por-historia-registro-changelog-e-assinatura-de-agentes.md`.

## Why it matters

- Elimina o risco de conflitos entre múltiplos agentes trabalhando em paralelo.
- Fornece um painel de bordo imediato no `CHANGELOG.md` sobre quem está fazendo o quê e em que estágio do desenvolvimento cada tarefa se encontra.
- Garante total estabilidade e integridade da branch principal `main`.
