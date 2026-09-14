---
date: 2026-09-14T02:15:00Z
author: Antigravity (Driver)
kind: milestone
related:
  - CV1.DS1.US3
verification:
  - uv run pytest (34 testes verdes)
  - npm --prefix web run build (frontend Svelte 5 compilado limpo)
  - validação manual e multi-papel pelo Navigator
---

# Desfazer ponto a ponto e permissões de controle (CV1.DS1.US3)

## What changed

Entrega da terceira User Story de `CV1.DS1 - Núcleo da Partida`, incorporando refinamentos de permissões e capacidade solicitados pelo Navigator:
- **Desfazer Ponto a Ponto (`POST /api/quadras/{id}/desfazer`):**
  - Anulação atômica via evento append-only `PONTO_DESFEITO` referenciando `ref_seq` do último ponto ativo no log.
  - Recálculo determinístico da projeção: se o ponto anulado era o match point da vitória, a partida é automaticamente reaberta (`encerrada=False`, `vencedor=None`).
  - Broadcast em tempo real para todos os clientes conectados via WebSocket (`PLACAR_ATUALIZADO`).
  - Erro 400 caso o placar já esteja em 0 × 0.
- **Controle de Acesso por Papel:**
  - Apenas `ADMIN` e `CONTROLADOR` têm autorização para marcar pontos ou desfazer (retorna HTTP 403 Forbidden para espectadores).
  - A interface adapta-se ao papel: espectadores têm visão limpa focada no placar (sem botões de controle, sem aviso intrusivo).
- **Limites de Capacidade da Instância:**
  - Configurados limites em `app/config.py` para proteger o SQLite/instância local: máximo de 50 arenas, 20 quadras por arena e 50 participantes por quadra (retornando HTTP 400 Bad Request se excedido).
- **Ergonomia e Persistência:**
  - Preenchimento automático do apelido no modal a partir do `localStorage`.
  - Botão de desfazer ergonômico, com proteção de debounce contra clique duplo e feedback tátil.
- **Suíte de Testes Automatizados:**
  - 34 testes automatizados em `pytest` cobrindo fluxo normal, anulação sucessiva até zerar, reabertura de partida, rejeição quando zerado, restrições por papel (403 para espectadores) e limites de capacidade.

## Why it matters

- Respeita o princípio de produto *"Corrigir é tão barato quanto marcar"*, sem janelas de tempo, sem confirmações burocráticas e com preservação total do histórico de auditoria (nada é apagado no banco).
- Garante a integridade da pelada: apenas quem controla pode pontuar ou reverter.
- Protege a infraestrutura do Mini PC de abuso ou vazamento de recursos.

## Verification

- `uv run pytest`: 34 testes passando.
- `uv run ruff check .` e `uv run ruff format --check .`: código limpo e formatado.
- `npm --prefix web run build`: bundle Svelte 5 compilado limpo em `app/static/`.
- Validado pelo Navigator via navegador com múltiplos papéis (Admin e Espectador).

## Follow-up

- Puxar a próxima story solicitada pelo Navigator: `CV1.DS4.US1` — Linha do tempo da partida (exibindo a evolução ponto a ponto da pontuação e eventos anulados).
