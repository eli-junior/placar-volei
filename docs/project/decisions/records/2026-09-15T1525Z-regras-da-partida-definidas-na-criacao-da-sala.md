---
status: Decided
raised: 2026-09-15
decided: 2026-09-15
deciders:
  - Navigator
supersedes:
related:
  - CV1.DS3.US1
  - CV1.DS3
---

# Regras da partida definidas na criação da sala

## Question

Onde e quando as regras de pontuação (pontuação-alvo, vantagem de 2 e teto) devem ser configuradas pela quadra?

## Decision

As regras da partida são definidas **exclusivamente no início da jornada, na criação da sala** (`HomePlacar.svelte` / `POST /api/quadras`).

Caso o grupo decida alterar as regras da pelada (por exemplo, passar de 12 para 21 pontos ou desligar a vantagem), **deve-se criar uma nova sala**.

As regras definidas na criação são preservadas ao reiniciar partidas na mesma sala (`POST /api/quadras/{id}/reiniciar`).

## Rationale

Decisão de produto do Navigator (Product Owner).

Permitir a alteração de regras no meio de uma partida em andamento introduz complexidade operacional e cognitiva desnecessária à beira da quadra:
1. Risco de discussões ou disputas caso um administrador altere o alvo ou teto durante um rally ou em momentos críticos de pontuação;
2. Complexidade de lidar com tetos ou alvos alterados abaixo da pontuação já atingida no placar;
3. Criar uma nova sala com código PIN de 5 dígitos leva menos de 10 segundos e garante clareza total de que um novo contexto de jogo está iniciando.

## Options Considered

- **Alteração dinâmica com partida em andamento via modal no placar**: Rejeitado pelo Navigator. Gera atrito na experiência e ambiguidades durante o jogo.
- **Configuração exclusiva na criação da sala**: Escolhido. Mantém a interface do placar limpa, objetiva e sem distrações de configuração durante o rally.

## Consequences

- O formulário de criação de placar em `HomePlacar.svelte` ganha campos para escolha de pontuação-alvo (com atalhos rápidos 12, 15, 21, 25 e input numérico), interruptor de vantagem de 2 pontos e campo opcional de teto da vantagem.
- O endpoint `POST /api/quadras` valida e persiste `alvo`, `vantagem` e `teto` no evento `PARTIDA_INICIADA`.
- O endpoint `POST /api/quadras/{id}/reiniciar` preserva as regras originais da quadra para novas partidas.
- As telas de placar (`Placar.svelte`, `PlacarManual.svelte`, `SalaQuadra.svelte`) exibem de forma destacada e informativa as regras ativas da sala (ex: `Até 15 pts • Vantagem • Teto 18` ou `Até 21 pts • Sem vantagem`).
