---
date: 2026-09-13T23:25:00Z
author: Antigravity (Driver)
kind: milestone
related:
  - CV1.DS1.US1
verification:
  - uv run pytest (22 testes verdes)
  - npm run build (frontend Svelte 5 compilado limpo)
  - validação visual e multi-cliente pelo Navigator
---

# Criar arena, quadra e entrar por apelido (CV1.DS1.US1)

## What changed

Entrega da primeira User Story observável do produto:
- **Hierarquia Arena → Quadra:** introduzida a entidade `Arena` (ex: "T9 Beach Club") agrupando múltiplas quadras no banco SQLite (`arenas` e `quadras.arena_id`), com migração automática idempotente.
- **Backend REST e WebSocket:**
  - `GET /api/arenas`, `POST /api/arenas`, `GET /api/arenas/{id}/quadras`, `POST /api/arenas/{id}/quadras`.
  - Entrada atômica por apelido (`POST /api/quadras/{id}/entrar`) com emissão de cookie `HttpOnly` (`session_id`), atribuindo `ADMIN` ao 1º participante e `ESPECTADOR` aos demais.
  - Restauração de sessão sem login via `GET /api/quadras/{id}/eu`.
  - WebSocket `/ws/{quadra_id}` enviando `ESTADO_INICIAL` e transmitindo `PRESENCA_ATUALIZADA` em tempo real.
  - FastAPI servindo os estáticos compilados e fallback SPA para `index.html`.
- **Frontend Svelte 5:**
  - Aplicação moderna em `web/` usando runes (`$state`, `$props`), transições nativas Svelte (`slide`, `fade`), tema escuro esportivo de alto contraste e modais acessíveis.
  - Telas de lista de arenas, quadras da arena selecionada, modal de apelido e sala da quadra com indicador online verde.
- **Suíte de Testes:** 22 testes automatizados (`uv run pytest`) passando em 0.48s.

## Why it matters

Transforma a fundação técnica em produto tangível:
1. Reflete a experiência presencial real (as pessoas vão a uma arena/clube como o T9 Beach Club onde há várias quadras);
2. Mantém a premissa de zero fricção: sem cadastro e sem senha, apenas apelido;
3. O primeiro participante assume a gestão da quadra como Admin;
4. Todos veem quem está presente na quadra em tempo real;
5. F5 ou recarregamento acidental não perde o papel nem o apelido.

## Verification

- `uv run pytest`: 22 testes passando.
- `uv run ruff check .` e `uv run ruff format --check .`: código limpo e formatado.
- `npm run build`: bundle Svelte 5 compilado limpo em `app/static/`.
- Testado e validado pelo Navigator no navegador local.

## Follow-up

- Puxar a próxima story: `CV1.DS1.US2` — Marcar ponto em tempo real (botões de toque grandes para marcar ponto e propagação do placar ao vivo).
