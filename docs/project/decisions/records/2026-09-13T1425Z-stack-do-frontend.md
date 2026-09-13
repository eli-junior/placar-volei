---
status: Decided
raised: 2026-09-13
decided: 2026-09-13
deciders:
  - Navigator
  - Driver
supersedes:
related:
  - CV1.DS1
  - CV1.DS4
---

# Stack do frontend: Svelte 5

## Question

O frontend é JavaScript puro servido pelo FastAPI, ou uma aplicação com build step?

## Decision

**Svelte 5**, compilado em build time e servido como estáticos pelo próprio FastAPI.

O Navigator delegou a escolha ao Driver, com um requisito explícito: interface bem trabalhada, com animação na interação. Esse requisito é o que decide.

Complementos:

- **Motion nativo do Svelte** — `transition:`, `animate:flip`, `crossfade`, `spring` e `tween`. Sem biblioteca de animação adicional.
- **CSS puro** para micro-interações (estados de toque, feedback de botão). Sem framework de CSS.
- **Build isolado no Docker** — estágio `node` compila, estágio `python` só recebe os estáticos. Node não roda no Mini PC.

## Rationale

A tela do placar é pequena em superfície e densa em movimento: número de ponto que troca, evento que entra na linha do tempo, participante que aparece ou some da lista, anúncio de vitória, troca de admin. Todos são transições de estado empurradas pelo servidor.

Svelte resolve exatamente essa classe de problema no núcleo da linguagem, não numa biblioteca por cima:

- `transition:` e `crossfade` dão entrada e saída de elementos sem gerenciar ciclo de vida na mão.
- `animate:flip` anima reordenação de lista — a linha do tempo recebendo eventos ao vivo é o caso de uso literal.
- `spring` e `tween` animam o próprio valor numérico do placar, que é o movimento mais visível do produto.
- Reatividade por runes casa direto com um cliente que é projeção de eventos WebSocket: `$state` recebe o evento, a UI reage.

O compilador entrega um bundle pequeno, o que importa para celular em rede de quadra.

O custo real é um estágio de build com Node. Ele fica confinado ao `docker build`: o contêiner que roda no Mini PC continua sendo só Python servindo estáticos, sem Node, sem `node_modules`, sem processo extra. A premissa de simplicidade de operação é preservada — o que ela protege é a máquina ligada 24/7, não a máquina de desenvolvimento.

## Options Considered

- **JS puro + CSS** — deploy mais simples de todos, mas animar entrada, saída e reordenação de listas ao vivo na mão é justamente onde código sem framework degrada rápido. Contra o requisito de interface trabalhada, deixa de ser o caminho barato.
- **React + framer-motion** — resolve animação bem, mas exige biblioteca extra para o que Svelte tem embutido, bundle maior e mais cerimônia para uma UI de cinco telas.
- **Alpine ou htmx** — bons para interatividade leve; fracos exatamente em animação coreografada e em estado empurrado por WebSocket.
- **Vue com Transition** — alternativa legítima e próxima. Svelte vence pelo bundle menor e pelo `animate:flip`, que a linha do tempo usa diretamente.

## Consequences

- Entra Node no ambiente de desenvolvimento e no `docker build`. Não entra no runtime do Mini PC.
- A restrição "sem build step obrigatório" no briefing deixa de valer e foi removida.
- O contrato de eventos WebSocket permanece o limite entre backend e frontend — trocar o frontend depois não deve exigir mudança no backend.
- Animação passa a ser critério de aceite de story visível, não polimento opcional. Ver o princípio de produto correspondente.
- O bundle compilado é versionado como artefato de build, não commitado.

## Review Trigger

Se o build passar a atrapalhar o ciclo de desenvolvimento a ponto de o Navigator evitar mexer no frontend, reavaliar.
