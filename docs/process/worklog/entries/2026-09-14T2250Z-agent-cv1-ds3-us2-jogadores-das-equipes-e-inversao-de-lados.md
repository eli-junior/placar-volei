---
date: 2026-09-14T22:50:00Z
author: Antigravity (Driver)
kind: milestone
related:
  - CV1.DS3.US2
  - CV1.DS3
verification:
  - pytest tests/test_jogadores_e_inversao.py
  - pytest
  - validacao multi-dispositivo conforme test-guide.md
---

# Jogadores das Equipes e Inversão de Lados (CV1.DS3.US2)

## What changed

- **Identificação de Jogadores Reais na Partida:**
  - `HomePlacar.svelte`: novo bloco de campos para definir Jogador 1 (obrigatório) e Jogador 2 (opcional) para cada time no momento de criação da sala.
  - Validação estrita no frontend: criação bloqueada caso o Jogador 1 de qualquer time não esteja preenchido.
  - `app/api.py`: helper `formatar_nome_equipe` padroniza a montagem de nomes de equipes no formato `"Jogador 1"` (dupla individual) ou `"Jogador 1 / Jogador 2"` (dupla completa), mantendo fallbacks retrocompatíveis para clientes legados.
  - `app/projecao.py` e `app/quadras.py`: persistência e projeção de `jogadores_a` e `jogadores_b` no evento `PARTIDA_INICIADA` e em `EstadoPartida`.
  - Linha do tempo, banners de vitória e botões do placar passaram a refletir imediatamente os nomes dos jogadores (ex: `"Eli marcou para Carlos / Daniel"`).
  - Reinício de partida (`POST /api/quadras/{id}/reiniciar`) suporta tanto novos nomes de jogadores quanto preservação automática dos times da partida anterior.

- **Inversão de Lados por Perspectiva Local:**
  - Botão `⇄ Inverter Lados` adicionado em `Placar.svelte` (controlador), `PlacarManual.svelte` (espectador) e `SalaQuadra.svelte` (topo).
  - Implementação visual com CSS Grid (`grid-template-areas: "time-b divisor time-a"`):
    - Permuta as colunas de time, cartões dobráveis e botões de `+1` instantaneamente.
  - Persistência desacoplada em `localStorage` por ID de quadra (`placar:lados_invertidos:<quadraId>`):
    - A inversão é 100% individual por dispositivo/navegador, permitindo que cada pessoa ajuste o placar à sua posição física ao redor da quadra sem afetar nenhum outro participante.

## Why it matters

- Remove os rótulos genéricos "Equipe A" e "Equipe B", tornando a pelada personalizada e fácil de acompanhar para quem está jogando ou assistindo.
- Resolve a ambiguidade física de pontuação na quadra: quem opera com uma mão pode sempre manter o botão `+1` alinhado ao time físico que está do seu lado esquerdo ou direito.

## Verification

- 77 testes automatizados passando no pytest (`uv run pytest`), incluindo novos testes em `tests/test_jogadores_e_inversao.py`.
- Formatação e linter 100% limpos com `uv run ruff check .` e `uv run ruff format --check .`.
- Roteiro de validação manual aprovado pelo Navigator com validação em múltiplos navegadores e confirmação do isolamento local da perspectiva.
