---
date: 2026-09-14T22:00:00Z
author: Antigravity (Driver)
kind: milestone
related:
  - CV1.DS2.US1
  - CV1.DS2
verification:
  - pytest tests/test_promover_revogar_controladores.py
  - pytest
  - validacao multi-dispositivo conforme test-guide.md
---

# Admin Promove e Revoga Controladores (CV1.DS2.US1)

## What changed

- **Apoio Operacional ao Papel de Controlador:**
  - O motor de comandos em `app/comandos.py` passou a aceitar participantes com papel `CONTROLADOR` nas operações do placar (`pontos`, `desfazer`, `assumir`).
  - Espectadores e sessões não registradas são barrados com HTTP 403 diretamente pelo backend ao tentar qualquer operação.

- **Comandos e Endpoints de Promoção e Revogação:**
  - Novos endpoints REST:
    - `POST /api/quadras/{quadra_id}/participantes/{participante_id}/promover`: promove espectador a `CONTROLADOR`, transferindo atomicamente o turno de controle ativo para o participante promovido.
    - `POST /api/quadras/{quadra_id}/participantes/{participante_id}/revogar`: retorna o participante para `ESPECTADOR`, devolvendo com segurança o turno de controle ao `ADMIN` caso o participante revogado estivesse operando.
    - `POST /api/quadras/{quadra_id}/participantes/{participante_id}/papel`: endpoint flexível para transição declarativa de papéis.
  - Gravação do evento imutável `TipoEvento.PAPEL_ALTERADO` no event store append-only.

- **Linha do Tempo Auditável:**
  - Projeção de descrições detalhadas na Linha do Tempo:
    - `"{autor} promoveu {alvo} a controlador"`
    - `"{autor} revogou controlador de {alvo}"`

- **Frontend Svelte 5:**
  - `ListaPresentes.svelte`:
    - Botões contextuais para o Admin: **"Tornar controlador"** para espectadores e **"Revogar controlador"** para quem já é controlador.
    - Badges específicos para cada papel: `ADMIN` (dourado/laranja), `CONTROLADOR` (azul claro) e `ESPECTADOR` (cinza neutro).
  - `SalaQuadra.svelte`:
    - Reatividade imediata de `podeControlar`: participantes promovidos passam a ver os botões de ponto e desfazer sem recarregar a página.
    - Ao revogar, os botões desaparecem instantaneamente via WebSocket e a interface retorna ao modo de visualização.

## Why it matters

- Permite que o criador da sala/admin (que muitas vezes está em quadra jogando) delegue a operação do placar para um parceiro ou espectador no banco sem abrir mão da propriedade da sala.
- Garante total segurança e integridade: a permissão é checada no servidor a cada lance, e a UI apenas reflete o estado auditado em tempo real.

## Verification

- Suíte de testes com 73 testes passando (`uv run pytest`), incluindo 2 novos cenários completos em `tests/test_promover_revogar_controladores.py`.
- Verificação de estilo e tipagem limpa com `uv run ruff check .` e `uv run ruff format --check .`.
- Roteiro de validação multi-dispositivo com 3 clientes estruturado no `test-guide.md` e aprovado.
