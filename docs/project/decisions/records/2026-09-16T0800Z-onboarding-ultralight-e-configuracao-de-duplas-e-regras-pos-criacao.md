---
status: Decided
raised: 2026-09-16
decided: 2026-09-16
deciders:
  - Navigator
supersedes: docs/project/decisions/records/2026-09-15T1525Z-regras-da-partida-definidas-na-criacao-da-sala.md
related:
  - CV2.DS2
  - CV2.DS4
---

# Onboarding Ultralight na Criação da Sala e Configuração de Duplas e Regras In-Game e no Reinício

## Question

Onde e quando devem ser definidos os nomes das duplas e as regras de pontuação da partida (alvo, vantagem, teto)? Como equilibrar a agilidade de criação da sala com a flexibilidade de conduzir múltiplas partidas consecutivas sem forçar a recriação da quadra a cada rodada?

## Decision

1. **Onboarding Ultralight na Home**: A criação da quadra na tela inicial solicita estritamente o **apelido do criador** e o **nome opcional da quadra**, com regras padrão pré-definidas (12 pontos, vantagem de 2). Nenhuma dupla ou configuração avançada bloqueia o onboarding inicial.
2. **Configuração In-Game de Duplas e Regras**: O administrador ou controlador da quadra possui um botão acessível no topo e no placar ("Duplas & Regras") para abrir o modal de configuração a qualquer momento, podendo atualizar os nomes dos jogadores de cada time, a pontuação-alvo, a exigência de vantagem e o teto de pontos via endpoint `POST /api/quadras/{id}/configurar`.
3. **Múltiplas Partidas na Mesma Sala**: Ao encerrar um jogo, a próxima partida pode ser iniciada na mesma sala mantendo o mesmo código de 5 dígitos e os espectadores conectados. O modal de reinício (`POST /api/quadras/{id}/reiniciar`) permite trocar as duplas para a próxima rodada e ajustar as regras antes de zerar o placar para `0 x 0`.

## Rationale

Decisão de produto do Navigator (Product Owner).

No cenário real de quadras de vôlei e peladas de areia:
1. **Fricção zero na criação**: O organizador que chega à quadra quer criar a sala imediatamente para gerar o código e compartilhar com a galera. Forçar a digitação de 4 nomes de jogadores e configurações de regras antes de entrar atrasa o início do jogo.
2. **Dinâmica de rotação de duplas**: Em uma tarde ou noite na quadra, dezenas de partidas acontecem em sequência (rodízio de duplas ou "quem perde sai"). Ter que criar uma nova sala a cada 15 minutos forçaria todos os espectadores e participantes a saírem e digitarem um novo código no celular a cada rodada.
3. **Integridade da partida preservada**: O evento `REGRAS_CONFIGURADAS` e `PARTIDA_REINICIADA` é registrado de forma append-only no log de eventos do SQLite e transmitido via WebSocket, garantindo auditoria e sincronização em tempo real sem conflitos.

## Options Considered

- **Forçar configuração no formulário inicial**: Superada. Causava fricção no onboarding e exigia recriar a sala para trocar jogadores.
- **Onboarding ultralight com configuração pós-criação**: Escolhida. Criação imediata, máxima ergonomia na quadra e reuso contínuo da mesma sala para múltiplas rodadas com troca de duplas.

## Consequences

- `HomePlacar.svelte` mantém foco no onboarding limpo e no botão de alto contraste (Modo Sol).
- `app/api.py` disponibiliza `POST /api/quadras/{id}/configurar` e estende `ReiniciarPartidaBody` com `{ alvo, vantagem, teto, jogadores_a, jogadores_b }`.
- `ModalConfigurarPartida.svelte` atua como componente unificado tanto para ajuste em andamento quanto para início de nova partida.
- O código PIN de 5 dígitos permanece válido por toda a sessão da quadra, mantendo espectadores conectados durante toda a sequência de jogos.
