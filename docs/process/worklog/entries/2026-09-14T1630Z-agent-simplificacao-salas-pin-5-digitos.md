---
date: 2026-09-14T16:30:00Z
author: Antigravity (Driver)
kind: milestone
related:
  - CV1.DS1
  - CV1.DS1.US1
verification:
  - uv run pytest (51 testes verdes em 2.23s)
  - uv run ruff check . ; uv run ruff format --check . (100% limpo)
  - npm --prefix web run build (sucesso em 467ms)
  - rota de validacao manual executada e aprovada pelo Navigator
---

# Simplificação da Entrada: Salas com Código PIN de 5 Dígitos (CV1.DS1.US1)

## What changed

- **Novo Modelo de Salas por Código PIN:**
  - Substituição do modelo aninhado de arenas pela criação e ingresso direto via código numérico aleatório de 5 dígitos (`10000` a `99999`).
  - Criador da sala é automaticamente registrado como `ADMIN`.
  - Ingressantes via código entram como `ESPECTADOR`.
- **Limites e Ciclo de Vida (TTL):**
  - Teto de no máximo 20 salas ativas simultâneas (`max_quadras = 20`).
  - Teto de no máximo 20 participantes por sala (`max_participantes_por_quadra = 20`).
  - Expiração e limpeza automática em cascata (partidas, eventos e participantes) de salas sem atualização há mais de 1 hora (`quadra_ttl_seconds = 3600`).
  - Rotina assíncrona periódica no `lifespan` do FastAPI para expurgo em segundo plano.
- **Banco de Dados Efêmero e Bump para v0.2.0:**
  - Remoção de volume persistente `placar-dados` de `docker-compose.yml` e `Dockerfile`.
  - Bump de versão para `0.2.0` (`pyproject.toml`, `app/config.py`, `app/main.py`).
  - Tabela `app_meta` rastreia a versão instalada; se o servidor iniciar e detectar banco de versão anterior, ele automaticamente apaga e recria o banco limpo.
- **Frontend Renovado (`web/src/`):**
  - Criação de `HomePlacar.svelte` com abas para **Criar Placar** e **Acompanhar** (com input de 5 dígitos estilizado), além de grade das quadras ativas no momento com contagem de público `X/20`.
  - Exibição de banner com o **Código de 5 Dígitos da Sala** no topo de `SalaQuadra.svelte` com botão para copiar com um clique.
  - Exibição da tag `#12345` no topo de `PlacarManual.svelte` no modo espectador.
- **Testes Automatizados:**
  - Criação de `tests/test_sala_pin.py` e novo teste em `tests/test_main.py` validando recriação limpa de banco na troca de versão.
  - 51 testes no total 100% verdes no pytest.

## Why it matters

- Reduz a fricção de uso para praticamente zero: qualquer pessoa na quadra abre a página, cria o placar e passa o código de 5 dígitos para quem quiser assistir.
- Garante leveza e auto-manutenção do banco de dados SQLite sem necessidade de intervenção humana.
