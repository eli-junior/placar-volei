# Plano de Implementação — CV1.DS2.US1: Admin promove e revoga controladores

## 1. Contexto e Intenção

O objetivo desta história é permitir que o dono da quadra (`ADMIN`) delegue o poder de marcação e correção de pontos para outros participantes presentes (`CONTROLADOR`), podendo também revogar essa permissão a qualquer momento.

## 2. Nível no Roadmap e Branch

- **Nível**: User Story (`CV1.DS2.US1` dentro da Delivery Story `CV1.DS2 — Controle e permissões da quadra`).
- **Branch**: `feature/cv1-ds2-us1-promover-e-revogar-controladores` criada a partir de `master`.

## 3. Escopo

1. **Backend**:
   - Manutenção e refinamento do comando `papel` / `alterar_papel` em `app/comandos.py` e endpoint REST correspondente em `app/api.py`.
   - Suporte aos papéis: `ADMIN`, `CONTROLADOR`, `ESPECTADOR`.
   - Validação de autorização: apenas `ADMIN` pode promover espectador a controlador ou revogar controlador para espectador.
   - Não permitir que o admin rebaixe a si mesmo sem sucessão (fora do escopo desta story).
   - Gravação do evento auditável `PAPEL_ALTERADO` no event store append-only.
   - Aplicação de permissão rígida nas ações de pontuação (`pontos`, `desfazer`): permitidas para `ADMIN` e `CONTROLADOR`. Qualquer tentativa de um `ESPECTADOR` é rejeitada com HTTP 403.
   - Ajuste na projeção da linha do tempo (`app/projecao.py`) para exibir mensagens claras:
     - Promoção: `"{autor} promoveu {alvo} a controlador"`
     - Revogação: `"{autor} revogou o papel de controlador de {alvo}"`
2. **Frontend**:
   - `ListaPresentes.svelte`:
     - Exibição de badge para cada papel: `ADMIN` (dourado/destaque), `CONTROLADOR` (azul/destaque), `ESPECTADOR` (neutro).
     - Se o participante atual for `ADMIN`:
       - Botão "Promover a controlador" para espectadores.
       - Botão "Revogar controlador" para quem é controlador.
   - `SalaQuadra.svelte`:
     - Reatividade imediata de `podeControlar`: ativa quando `eu.papel in ('ADMIN', 'CONTROLADOR')`.
     - Ao ser promovido ou revogado, o participante tem seu estado refletido instantaneamente via WebSocket sem reload de página.
3. **Testes Automatizados**:
   - Suíte `tests/test_promover_revogar_controladores.py` validando promoção, revogação, bloqueio HTTP 403 para espectadores e evento WebSocket.

## 4. Comportamento de Aceite (BDD)

```gherkin
Given uma quadra com um admin e dois espectadores
When o admin promove um dos espectadores a controlador
Then aquele participante passa a ver os botões de ponto e desfazer, sem recarregar a página
And o outro espectador continua sem eles
And uma tentativa de pontuar vinda de espectador é rejeitada pelo backend com HTTP 403, mesmo se forjada diretamente via API
And ao revogar o papel de controlador, os botões desaparecem imediatamente para o ex-controlador
And a linha do tempo registra os eventos de promoção e revogação.
```

## 5. Decisões de Design

- **Segurança no servidor**: a UI esconde os botões para espectadores por conveniência e clareza, mas o backend valida rigorosamente o papel do participante na sessão ativa antes de executar qualquer ponto ou anulação.
- **REST + WebSocket**: a ação de alterar papel dispara uma requisição REST autenticada por sessão (`POST /api/quadras/{id}/participantes/{alvo_id}/papel`), persiste o evento e notifica todos os clientes conectados via broadcast WebSocket com o snapshot atualizado da sala.

## 6. Fora de Escopo

- Sucessão automática de admin por timeout de presença (`US2`).
- Owner takeover por código mestre (`US3`).
- Múltiplos admins ou transferência voluntária de admin.

## 7. Intenção de Versão

- **Minor**: parte integrante da Delivery Story `CV1.DS2`.
