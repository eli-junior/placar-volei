---
date: 2026-09-14T02:35:00Z
author: Antigravity (Driver)
kind: milestone
related:
  - CV1.DS4
  - CV1.DS4.US1
  - CV1.DS1.TS2
verification:
  - uv run pytest (38 testes verdes)
  - npm --prefix web run build (frontend Svelte 5 compilado limpo em 437ms)
  - validação manual e multi-tela em tempo real pelo Navigator
---

# Linha do tempo da partida e empacotamento Docker (CV1.DS4.US1 & CV1.DS1.TS2)

## What changed

Entrega completa da linha do tempo da partida e do empacotamento para deploy:
- **Linha do Tempo Determinística (`app/projecao.py`):**
  - Função pura `projetar_linha_do_tempo` gerando a reconstituição cronológica de todos os lances a partir do log append-only.
  - Placar resultante individual por lance, crachá por equipe, autor da marcação e horário legível.
  - Identificação de pontos desfeitos (`anulado=True`), exibidos com estilo riscado e evento de anulação associado.
- **Sincronização em Tempo Real (REST e WebSocket):**
  - Endpoint `GET /api/quadras/{quadra_id}/linha-do-tempo`.
  - Inclusão de `linha_do_tempo` no `ESTADO_INICIAL` e no broadcast `PLACAR_ATUALIZADO` do WebSocket, permitindo atualização ao vivo para espectadores e controladores sem recarregar.
- **Interface Svelte 5 (`web/src/components/LinhaDoTempo.svelte` e `Placar.svelte`):**
  - Botão **"📜 Linha do Tempo"** no cabeçalho do placar, democrático para todos os papéis.
  - Modal/gaveta responsivo com animações do Svelte (`fly`/`slide`), auto-scroll suave e acessibilidade (role dialog, tabindex e escape).
- **Empacotamento de Produção (`Dockerfile` e `docker-compose.yml`):**
  - Build multi-estágio: Node compila estáticos Svelte em `app/static/`, uv prepara venv Python, runtime final Debian slim sem Node ou npm.
  - Compose configurado com volume persistente para banco SQLite (`placar-dados:/data`) e healthcheck integrado.
- **Suíte de Testes:**
  - 38 testes automatizados (`uv run pytest`) passando em 1.4s, incluindo `tests/test_linha_do_tempo.py`.

## Why it matters

- Cumpre a promessa do produto de *Auditoria Visível*: nenhuma dúvida sobre quem marcou determinado ponto ou se uma anulação ocorreu fica sem resposta imediata na tela.
- Permite que o projeto seja colocado em produção imediatamente no servidor ou Mini PC com `docker compose up -d --build`.

## Verification

- `uv run pytest`: 38 testes passando.
- `uv run ruff check .` e `uv run ruff format --check .`: 100% limpo.
- `npm --prefix web run build`: bundle compilado sem avisos em 437ms.
- Validado ao vivo pelo Navigator em múltiplas telas e abas.
