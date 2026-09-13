---
status: Decided
raised: 2026-09-13
decided: 2026-09-13
deciders:
  - Navigator
  - Driver
supersedes:
related:
  - CV1.DS1.US1
---

# Arenas como agrupador de múltiplas quadras

## Question

Como estruturar o sistema para refletir a realidade física das peladas, onde um clube, arena ou complexo esportivo abriga várias quadras simultâneas?

## Decision

Criar a entidade **Arena** como agrupador de **Quadras**.

O fluxo do usuário passa a ser:
1. Selecionar ou criar uma **Arena** (ex: *"T9 Beach Club"*, *"CT Aricanduva"*).
2. Dentro da Arena selecionada, visualizar as **Quadras** ativas (ex: *"Quadra 1"*, *"Quadra Central"*) ou criar uma nova quadra.
3. Entrar na quadra informando o apelido, mantendo todas as regras de papéis (`ADMIN` para o primeiro, `ESPECTADOR` para os seguintes) e propagação em tempo real.

## Rationale

Na prática, as pessoas não jogam em "quadras soltas no éter". Elas combinam de ir a uma arena específica, que possui múltiplas quadras de areia ou quadras poliesportivas. Agrupar quadras por arena:
- Evita uma lista única global desordenada misturando jogos de locais diferentes;
- Facilita encontrar o jogo em andamento no clube onde a pessoa está fisicamente presente;
- Permite que um mesmo complexo esportivo rode múltiplos placares independentes sob o mesmo teto.

## Options Considered

- **Quadras sem agrupador (lista plana global)** — Rejeitado pelo Navigator: em locais com múltiplas quadras (como o T9 Beach Club), a lista fica confusa e não reflete a experiência do jogador.
- **Hierarquia rígida com login/cadastro de dono de arena** — Rejeitado: viola o princípio de zero fricção e zero cadastro do MVP. Qualquer pessoa presente pode criar uma arena e suas quadras.

## Consequences

- O schema do SQLite ganha a tabela `arenas` e a tabela `quadras` passa a ter a chave estrangeira `arena_id`.
- A tela inicial do frontend passa a listar as Arenas disponíveis, com navegação intuitiva para as quadras do local selecionado.
- Links diretos para quadras continuam funcionando perfeitamente sem exigir seleção manual da arena.
