---
status: Decided
raised: 2026-09-14
decided: 2026-09-14
deciders:
  - Eli (Navigator)
  - Antigravity (Driver)
supersedes:
related:
  - docs/process/development-guide.md
  - AGENTS.md
  - CHANGELOG.md
---

# Branches por História, Tracking Ativo no Changelog, Assinatura de Agentes e Sincronização Remota

## Question

Como viabilizar o trabalho simultâneo de múltiplos agentes de IA (ex.: Claude, Antigravity) no repositório, garantindo que a branch principal (`main`/`master`) só receba código finalizado e validado, e permitindo que uma história seja iniciada por um agente e concluída por outro com total clareza de estado mesmo diante de esgotamento de créditos?

## Decision

Alterar as diretrizes operacionais do Ariad neste repositório para adotar quatro práticas obrigatórias a partir de 2026-09-14:

1. **Branches Dedicadas por Desenvolvimento:**
   - Sempre que um novo desenvolvimento for iniciado, uma branch dedicada deve ser criada a partir da branch principal (`main` ou `master`), no padrão `feature/<codigo-ou-slug>`, `fix/...`, `chore/...` ou `tech/...`.
   - É terminantemente proibido commitar desenvolvimentos de novas histórias diretamente na branch principal.
   - Apenas histórias com validação completa e aceitas pelo Navigator no Checkpoint 4 podem ser integradas à branch principal.

2. **Registro de Trabalho em Andamento no `CHANGELOG.md`:**
   - O `CHANGELOG.md` passa a conter a seção `## [Em Andamento]` no topo do arquivo.
   - Toda branch ativa deve manter uma entrada informando: história/escopo, nome da branch, passo atual do ciclo Ariad (1. Orientação a 7. Merge), assinatura do agente ativo e notas para handoff / próximos passos.
   - Quando a história é validada, aceita e integrada à branch principal, o bloco é removido de `[Em Andamento]` e incorporado à versão fechada correspondente.

3. **Assinatura do Agente e Protocolo de Handoff:**
   - Todo trabalho ativo no changelog e mensagens de commit na branch devem registrar a assinatura do agente responsável (ex.: `Agente: Antigravity (Driver) | Sessão: <ID> | Data: YYYY-MM-DD HH:mm`).
   - Se outro agente assumir o trabalho em uma branch existente, ele deve atualizar a assinatura para si próprio, registrar que assumiu a partir do passo X e prosseguir a partir do estado documentado.

4. **Sincronização Contínua com o Repositório Remoto (Push Policy):**
   - Durante o ciclo de desenvolvimento e a cada checkpoint, o agente Driver deve commitar suas alterações parciais e dar push contínuo na branch remota (`git push -u origin <branch>`).
   - Garante que, se os créditos de IA acabarem ou a sessão for interrompida, o trabalho não fica congelado na máquina local: qualquer outro agente ou o Navigator pode puxar a branch do GitHub e continuar sem perda de trabalho.
   - Push na branch principal (`main`/`master`) segue restrito exclusivamente ao fechamento final da história no Checkpoint 4.

## Rationale

- O fluxo anterior do Ariad (trabalho direto na branch principal para desenvolvedor solo e sem seção de "Unreleased" no changelog) partia da premissa de um único agente por vez e sem paralelismo.
- Com diferentes agentes operando no projeto (ex.: Claude criando uma branch e Antigravity operando outra), o risco de conflito na branch principal e a opacidade sobre "o que está sendo feito e em qual passo está" tornou-se crítico.
- Ter a seção `[Em Andamento]` no topo do `CHANGELOG.md` oferece aos agentes e ao Navigator um painel de controle imediato em arquivo versionado, dispensando adivinhação sobre o status de cada branch.

## Options Considered

- **Manter apenas arquivos de plano (`plan.md`) nas pastas do roadmap:** Rejeitado como solução única, pois os planos ficam distribuídos em diretórios profundos (`docs/project/roadmap/cv1/...`) e não oferecem visão centralizada imediata de quais branches estão ativas e quem está trabalhando nelas.
- **Usar issues ou PRs no GitHub:** Embora útil, agentes operando localmente no terminal sem integração direta de API de PRs precisam de uma fonte de verdade no próprio sistema de arquivos do repositório.
- **Registro centralizado no `CHANGELOG.md` com branch e passo:** Aprovado pelo Navigator como método ágil, transparente e direto.

## Consequences

- O `AGENTS.md` e o `docs/process/development-guide.md` passam a exigir o cumprimento dessas regras para qualquer nova tarefa.
- A branch principal do repositório permanece estável e funcional a todo momento.
- Handoffs entre sessões ou modelos de IA tornam-se seguros e sem atrito.
