---
date: 2026-09-15T17:15:00Z
author: Antigravity (Driver)
kind: milestone
related:
  - CV1.DS3.US1
  - CV1.DS3
verification:
  - pytest tests/test_configurar_regras.py
  - pytest
  - npm test
  - svelte-check
  - validacao do navigator conforme test-guide.md
---

# Configuração de Pontuação-Alvo, Vantagem e Teto na Criação da Sala (CV1.DS3.US1)

## What changed

- **Regras Configuráveis na Criação da Sala (`HomePlacar.svelte`):**
  - Adicionada a seção **"Regras da Partida"** no formulário de criação de sala da tela inicial.
  - Seleção ágil de pontuação-alvo via botões de 1 toque (presets de `12`, `15`, `21`, `25` pontos) e suporte a pontuação personalizada (`1` a `100`).
  - Interruptor intuitivo para exigência de vantagem de 2 pontos (marcado por padrão).
  - Campo numérico para teto máximo da pontuação (exibido condicionalmente apenas quando a vantagem está ativa).
  - Validação inline no frontend: se o usuário informar um teto menor que a pontuação-alvo, um alerta visual vermelho é exibido e a submissão é bloqueada.

- **Validação e Persistência no Backend (`app/api.py` e `app/quadras.py`):**
  - Schema `CriarQuadraBody` expandido com `alvo: int = 12`, `vantagem: bool = True` e `teto: int | None = None`.
  - Validação estrita: requisições com `teto < alvo` são rejeitadas preventivamente com HTTP 422 e detalhe descritivo em português.
  - Funções `criar_quadra_sync` e `criar_quadra` recebem os parâmetros e registram no payload do evento `PARTIDA_INICIADA` no SQLite.
  - Eliminação do hardcode anterior (`alvo: 12, vantagem: True, teto: None`).

- **Projeção e Transparência das Regras (`app/projecao.py` e `SalaQuadra.svelte`):**
  - Linha do Tempo detalha as regras na narrativa cronológica inicial, incluindo o teto quando configurado (ex: `"Partida iniciada até 15 pts com vantagem de 2 (teto 18)"`).
  - Cabeçalho da quadra em `SalaQuadra.svelte` exibe um badge destacado com as regras vigentes (`🎯 Até {alvo} pts • {Vantagem / Sem vantagem} • Teto {teto}`) para administradores, controladores e espectadores.
  - Encerramento sem vantagem avalia vitória imediatamente ao atingir o alvo exato (ex: 15 × 14).
  - Encerramento com teto encerra imediatamente ao atingir o teto mesmo com apenas 1 ponto de vantagem.
  - Reinício de partida (`POST /reiniciar`) preserva automaticamente as regras configuradas na sala anterior.

- **Testes Automatizados e Qualidade:**
  - Criação de `tests/test_configurar_regras.py` com 7 novos testes automatizados cobrindo todo o ciclo de vida das regras.
  - Suíte completa expandida para 89 testes automatizados no backend (100% aprovados).
  - 3 testes no frontend aprovados e `svelte-check` com 0 erros e 0 avisos.
  - Formatação e linting 100% em conformidade com o Ruff.

## Why it matters

- Permite que cada pelada jogue com as regras combinadas antes da partida (12, 15, 21 ou 25 pontos, com ou sem vantagem, com ou sem teto), sem exigir suporte a múltiplos sets.
- A decisão de definir as regras no momento de criação da sala manteve o log de eventos limpo e eliminou complexidade concorrente durante o jogo.
- Entrega formal e conclusão da Delivery Story `CV1.DS3 — Regras da partida configuráveis pela quadra`.

## Verification

- `uv run pytest tests/test_configurar_regras.py` e `uv run pytest`: 89/89 testes aprovados.
- `npm --prefix web test`: 3/3 testes aprovados.
- `npm --prefix web run check`: 0 erros e 0 avisos.
- `npm --prefix web run build`: bundle de produção gerado com sucesso.
- Rota de validação no navegador com 3 cenários confirmada pelo Navigator no Checkpoint 2.
