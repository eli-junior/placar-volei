---
date: 2026-09-14T03:00:00Z
author: Antigravity (Driver)
kind: milestone
related:
  - CV1.DS1
  - CV1.DS1.US5
verification:
  - uv run pytest (38 testes verdes)
  - npm --prefix web run build (bundle compilado limpo em 493ms)
  - validação manual e multi-tela em tempo real pelo Navigator
---

# Modo Imersivo e Placar Dobrável Manual para Espectador (CV1.DS1.US5)

## What changed

Entrega da experiência do espectador com visual retrô e foco total no jogo:
- **Componente `CartaoDobravel.svelte`:**
  - Placa de pontuação no estilo dos placares manuais clássicos de quadra esportiva.
  - Anéis metálicos superiores com ilhoses vazados, vinco central horizontal e tipografia atlética de alto contraste.
  - Animação de virada tridimensional em CSS puro (`flipCardDown` no ponto marcado e `flipCardUp` no ponto desfeito com perspectiva `rotateX` e sombra de folha).
  - Compartilhado tanto pelo placar do espectador quanto pelo do controlador.
- **Componente `PlacarManual.svelte`:**
  - Montagem completa do cavalete de mesa/bancada com trilho metálico de anéis, etiquetas das equipes em relevo esportivo, divisor central, placas de regras do set e banner comemorativo de vitória.
- **Modo Imersivo Dinâmico (`SalaQuadra.svelte`):**
  - Ativado por padrão para espectadores: oculta cabeçalho, botão voltar e lista de participantes, centralizando o placar na tela.
  - Interação por toque/clique: ao tocar em qualquer local da tela, sai instantaneamente do modo imersivo e exibe os controles (botão de voltar, Linha do Tempo e participantes).
  - Temporizador de inatividade de 3 segundos: retorna ao modo imersivo após 3s sem toques (suspenso quando o modal da Linha do Tempo estiver aberto).
- **Identidade e Favicon:**
  - Adição de `favicon.svg` com bola de vôlei estilizada e painéis nas cores das equipes (Ciano e Laranja).
- **Ergonomia do Controlador Preservada:**
  - O controlador e admin mantêm seus botões táteis grandes de marcação rápida e desfazer sempre à mão, sem ocultação automática.

## Why it matters

- Eleva a sensação de presença e prazer visual para quem está na beira da quadra ou na arquibancada apenas acompanhando o jogo pelo celular.
- Respeita os princípios de produto: animação com significado funcional ("O movimento conta o que mudou"), alta legibilidade à distância e simplicidade operacional.

## Verification

- `uv run pytest`: 38 testes passando em 1.23s.
- `npm --prefix web run build`: 0 erros, 0 avisos.
- `uv run ruff check .` e `uv run ruff format --check .`: 100% limpo.
- Validado pelo Navigator em navegador e dispositivos móveis.
