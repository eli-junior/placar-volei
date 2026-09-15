---
date: 2026-09-15T14:15:00Z
author: Antigravity (Driver)
kind: milestone
related:
  - CV1.DS2.US2
  - CV1.DS2
verification:
  - pytest tests/test_sucessao_admin.py
  - pytest
  - validacao multi-dispositivo conforme test-guide.md
---

# Sucessão Automática do Admin (CV1.DS2.US2)

## What changed

- **Rastreio Ativo de Ausência e Tolerância de Admin:**
  - `app/quadras.py`: funções `atualizar_ultimo_visto_sync` e `atualizar_ultimo_visto` atualizam `ultimo_visto_em` de participantes no SQLite a cada conexão e desconexão de WebSocket.
  - `app/main.py`: no `lifespan` do FastAPI, nova tarefa periódica em background `rotina_sucessao()` inspeciona a cada 2 segundos as quadras com conexões ativas no `ConnectionHub`.
  - Tolerância configurável via `settings.admin_timeout_seconds` (padrão de 120s em produção).

- **Eleição Determinística e Transição de Autoridade:**
  - `app/sucessao.py`: módulo dedicado contendo `verificar_sucessao_quadra_sync` e `verificar_sucessao_quadra`.
  - Quando o admin fica ausente além do timeout de 2 minutos:
    - O controlador online há mais tempo (`criado_em ASC`) é promovido automaticamente a `ADMIN`.
    - O admin ausente é rebaixado no banco de dados para `CONTROLADOR`.
    - O controle ativo é transferido para o novo admin caso estivesse com o anterior.
    - Se nenhum controlador estiver online, o posto de admin fica vago e os controladores existentes mantêm total permissão para marcar e desfazer pontos.
  - Gravação do evento auditável `ADMIN_SUCEDIDO` com `antigo_admin_id`, `antigo_admin_apelido`, `novo_admin_id`, `novo_admin_apelido` e `motivo`.

- **Projeção e Comunicação em Tempo Real:**
  - `app/projecao.py`: narrativa cronológica na Linha do Tempo detalha a sucessão:
    - `"{novo_admin} assumiu a administração por sucessão (ausência de {antigo_admin})"` ou `"Administração vaga por ausência de {antigo_admin}"`.
  - Broadcast via WebSocket de `PLACAR_ATUALIZADO` e `PRESENCA_ATUALIZADA`: o novo admin ganha os botões de administração instantaneamente sem recarregar a tela; o admin anterior, caso reconecte, volta estritamente com o papel de `CONTROLADOR`.

- **Garantia de Qualidade e Cobertura:**
  - Criação de `tests/test_sucessao_admin.py` com 5 testes cobrindo ordem de chegada, reconexão do ex-admin, tolerância de ausência, caso sem controlador online e WebSocket. Total da suíte expandido para 82 testes 100% verdes.

## Why it matters

- Evita o travamento da partida por falta de bateria, fechamento acidental de janela ou queda de conectividade do criador da sala.
- Garante autoridade contínua e auditável sem necessidade de intervenção física ou recriação da sala.

## Verification

- 82 testes automatizados passando no pytest (`uv run pytest`).
- `svelte-check` no frontend com 0 erros e 0 avisos.
- `uv run ruff check .` e `uv run ruff format --check .` 100% limpos.
- Roteiro de validação multi-dispositivo com 3 clientes aprovado pelo Navigator.
