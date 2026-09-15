---
date: 2026-09-15T19:25:00Z
author: Antigravity (Driver)
kind: milestone
related:
  - CV1.DS2.TS1
  - CV1.DS2
verification:
  - pytest tests/test_owner_endpoint.py
  - pytest
  - npm test
  - svelte-check
  - ruff check .
  - ruff format --check .
  - validacao do navigator conforme test-guide.md
---

# Endpoint de Owner e Proteção Contra Força Bruta (CV1.DS2.TS1)

## What changed

- **Geração Segura de Código Mestre (`app/quadras.py` e `app/db.py`):**
  - Adicionada a coluna `codigo_mestre TEXT` na tabela `quadras` em `SCHEMA_SQL` com migração idempotente em `init_db_sync`.
  - Função `gerar_codigo_mestre_sync` gera códigos aleatórios de 4 dígitos (`0000`–`9999`) usando `secrets.randbelow(10000)`.
  - Códigos mestres são gerados e persistidos no banco no momento da criação de cada sala (`POST /api/quadras`).
  - Blindagem: rotas públicas da API (`/api/quadras`, `/api/quadras/{id}`, `/api/quadras/{id}/partida`) e eventos de WebSocket NUNCA expõem a coluna `codigo_mestre`.

- **Mecanismo de Rate Limiting com Janela Deslizante (`app/rate_limit.py`):**
  - Implementação da classe thread-safe `RateLimiter` com lock (`threading.Lock`).
  - Rastreamento por chave (IP/sessão) de tentativas falhas em janela deslizante de 10 minutos (600s).
  - Bloqueio progressivo de 5 minutos (300s) após 5 tentativas incorretas acumuladas na janela.
  - Retorno HTTP 429 Too Many Requests com cabeçalho padrão `Retry-After: 300` e detalhe explicativo em português.
  - Reset automático das falhas acumuladas após autenticação bem-sucedida.

- **Autenticação e Endpoint Seguro de Owner (`app/api.py` e `app/main.py`):**
  - Extração de chave de rate limit via `X-Forwarded-For` com fallback para `request.client.host`.
  - Autenticação de operador via `Authorization: Bearer <token>` ou query param `?secret=<token>` comparado contra `settings.owner_secret` de forma imune a timing attacks via `secrets.compare_digest`.
  - Camuflagem de segurança: requisições sem segredo ou com segredo inválido retornam `HTTP 404 Not Found` (em vez de 401), omitindo a própria existência da rota para scanners de rede.
  - Endpoints publicados: `GET /api/owner/quadras` e atalho de raiz `GET /owner/quadras`.
  - Listagem administrativa retorna metadados completos de todas as salas ativas com seus respectivos códigos mestres (`codigo_mestre`), PIN de acesso (`codigo_sala`), nome, times e data de criação.

- **Testes Automatizados e Qualidade:**
  - Criação da suíte `tests/test_owner_endpoint.py` com 7 novos testes automatizados cobrindo autenticação por Header Bearer e Query param, camuflagem 404, bloqueio progressivo por IP, isolamento entre IPs distintos, headers `Retry-After` e máscara nos endpoints públicos.
  - Suíte completa expandida para 96 testes automatizados no backend (100% aprovados).
  - Frontend com 100% dos testes aprovados e `svelte-check` sem erros e sem avisos.
  - Conformidade estrita de tipagem, linting e formatação com o Ruff.

## Why it matters

- Permite que o operador ou dono da infraestrutura consulte e audite os códigos mestres de todas as salas em execução com canal administrativo exclusivo e seguro.
- Protege a faixa de 4 dígitos contra ataques automatizados de força bruta via limitação rigorosa de requisições falhas.
- Garante imunidade contra enumeração e reconhecimento de rotas via retorno HTTP 404.
- Conclui as histórias ativas de `CV1.DS2 — Controle e permissões da quadra`, deixando o arco em estado validado.

## Verification

- `uv run pytest tests/test_owner_endpoint.py`: 7/7 testes aprovados.
- `uv run pytest`: 96/96 testes aprovados (100%).
- `npm --prefix web test`: 3/3 testes aprovados.
- `npm --prefix web run check`: 0 erros e 0 avisos.
- `uv run ruff check .` e `uv run ruff format --check .`: código limpo.
- Rota de validação com segredo correto, incorreto e teste de exaustão de taxa aprovada pelo Navigator.
