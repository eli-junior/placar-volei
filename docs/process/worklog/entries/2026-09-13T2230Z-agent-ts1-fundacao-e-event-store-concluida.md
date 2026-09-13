---
date: 2026-09-13T22:30:00Z
author: Antigravity (Driver)
kind: milestone
related:
  - CV1.DS1.TS1
verification:
  - uv run pytest (14 testes verdes)
  - uv run python scripts/validar_fundacao.py
  - validação manual pelo Navigator no PowerShell local
---

# Fundação do backend e event store concluída (CV1.DS1.TS1)

## What changed

Implementada a fundação da aplicação FastAPI com SQLite:
- `app/db.py`: conexão SQLite nativa em thread pool, modo WAL, foreign keys e schema com as 4 tabelas centrais (`quadras`, `partidas`, `participantes`, `eventos`) com unicidade `UNIQUE(partida_id, seq)`.
- `app/eventos.py`: envelope de eventos e append serializado por `asyncio.Lock` por quadra, garantindo sequência monotônica e persistência dos dados em disco.
- `app/projecao.py`: função pura `projetar_estado` determinística, com anulação idempotente por referência de `PONTO_DESFEITO` e avaliação da regra vigente (alvo, vantagem de 2 e teto).
- `app/hub.py`: `ConnectionHub` particionado por quadra para propagação via WebSockets.
- `app/main.py`: aplicação FastAPI, lifespan assíncrono e endpoint `/health`.
- `pyproject.toml` e `.env.example`: gerenciamento com `uv` e configurações via `pydantic-settings`.
- Suíte automatizada com 14 testes (`tests/test_projecao.py`, `tests/test_eventos.py`, `tests/test_main.py`) e script de inspeção direta `scripts/validar_fundacao.py`.

## Why it matters

O coração do sistema é o log de eventos append-only. O placar ser uma projeção desse log garante:
1. Desfazer ponto a ponto sem limite até zerar, sem perda de auditoria;
2. Desfazer o ponto da vitória reabre a partida automaticamente sem tratamento especial;
3. Resiliência completa a reinício do processo ou do Mini PC — o estado reconstrói-se diretamente a partir dos eventos no SQLite.

## Verification

- `uv run pytest`: 14 testes passando em 0.38s.
- `uv run ruff check .` e `uv run ruff format --check .`: código limpo e formatado.
- `uv run python scripts/validar_fundacao.py`: inspecionou diretamente o SQLite confirmando que pontos desfeitos continuam no log e que a projeção é determinística.
- Validado e aceito pelo Navigator no Checkpoint 2.

## Follow-up

- Iniciar a próxima story do roadmap: `CV1.DS1.US1` (criar quadra e entrar).
- Definir estratégia mínima de versionamento/migração de schema em `CV1.DS1.TS2`.
