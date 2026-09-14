---
code: CV1.DS1.US2
kind: plan
status: Implemented
approved_by: Navigator
updated: 2026-09-13
---

# Plano — CV1.DS1.US2 Marcar ponto e ver o placar sincronizado

## Nível e Versão

- **Nível:** User Story (`CV1.DS1.US2`)
- **Versão alvo:** `0.1.0` (segunda User Story de `CV1.DS1 - Núcleo da Partida`)

## Escopo

1. **Backend (FastAPI + Event Store):**
   - Rota REST para marcar ponto:
     - `POST /api/quadras/{quadra_id}/pontos`:
       - Recebe payload `{"equipe": "A" | "B"}`.
       - Valida que a quadra existe e possui partida ativa em andamento.
       - Identifica o autor a partir do cookie de sessão `session_id` associado à quadra (`participante_id`).
       - Valida se a partida não está encerrada (se já atingiu o alvo com vitória, rejeita novos pontos com HTTP 400).
       - Registra atomicamente o evento `PONTO_MARCADO` no event store SQLite (`append_evento`).
       - Carrega eventos da partida e recalcula a projeção determinística (`projetar_estado`).
       - Emite broadcast via WebSocket (`ConnectionHub`) para todos os clientes conectados na quadra com a mensagem `PLACAR_ATUALIZADO` contendo o evento gravado e o `estado_partida` projetado.
       - Retorna o evento gerado e o novo `estado_partida`.
   - Rota REST de consulta de estado da partida:
     - `GET /api/quadras/{quadra_id}/partida`: retorna o estado projetado atual da partida ativa da quadra.

2. **Frontend (Svelte 5):**
   - Componente de Placar Interativo (`Placar.svelte` integrado a `SalaQuadra.svelte`):
     - Exibição de Time A e Time B com pontuação em tamanho display (visível a metros de distância).
     - Botões de ponto por equipe com área de toque ampla, dimensionados para uso com uma só mão / polegar na beira da quadra (mínimo de altura e largura ergonômica).
     - Feedback de toque imediato com vibração tátil leve (`navigator.vibrate?.(40)` quando suportado) e estado ativo visual.
     - Proteção contra clique duplo acidental (debounce/submissão concorrente).
     - Transição animada do número do placar usando transições/motion nativo do Svelte (animação deslizante/flip visual ou `spring`/`tween`, com duração de 150–250ms), sem troca seca de dígito.
     - Suporte completo a `prefers-reduced-motion` (desativa movimento físico para usuários com sensibilidade).
   - WebSocket e Sincronização em Tempo Real (`App.svelte` / `SalaQuadra.svelte`):
     - Tratamento da mensagem `PLACAR_ATUALIZADO` para atualizar reativamente `estadoPartida`.
     - Reconciliação transparente na reconexão: ao restabelecer a conexão WebSocket (ou após queda de rede/modo avião), a mensagem `ESTADO_INICIAL` já entrega o estado projetado atualizado do servidor sem exigir recarga manual de página.
     - Indicação visual caso a partida atinja a condição de vitória/encerramento.

## Comportamento de Aceite (BDD)

```gherkin
Given dois participantes conectados na mesma quadra (Cliente 1 e Cliente 2)
When Cliente 1 toca no botão "+1" da Equipe A
Then o evento PONTO_MARCADO é gravado no banco com tipo, equipe "A", autor_id e criado_em
And o placar da Equipe A incrementa de 0 para 1 em ambas as telas em até 2 segundos
And o número transiciona visualmente com animação suave em vez de trocar seco
And quando o Cliente 2 desativa sua rede por 30 segundos enquanto pontos adicionais são marcados
When o Cliente 2 reconecta à rede
Then seu placar reconcilia automaticamente para o estado vigente sem necessidade de recarregar a página manualmente.
```

## Decisões de Design

### 1. Marcação de Ponto via REST + Broadcast via WebSocket
- A gravação do ponto é feita via `POST /api/quadras/{quadra_id}/pontos`. O backend grava o evento, projeta o estado e dispara broadcast WebSocket para todas as conexões ativas da quadra.
- *Por que:* Garante semântica HTTP clara (status code 201/200, mensagens de erro em caso de validação falha, cookies HttpOnly de sessão enviados nativamente pelo navegador). O broadcast WebSocket replica a atualização a todos os celulares simultaneamente em menos de 100ms.
- *Alternativa rejeitada:* Comandos de mutação enviados diretamente como texto cru dentro do canal WebSocket — mais difícil de testar de forma isolada, complica tratamento de autenticação de sessão e erros de validação HTTP.

### 2. Projeção Determinística Reutilizada
- O backend já possui a função determinística `projetar_estado(eventos)` implementada e testada em `app/projecao.py`. Cada ponto gravado passa por essa projeção, mantendo integridade absoluta entre o log append-only e o estado retornado.
- *Por que:* Alinha-se diretamente ao princípio fundamental do produto: *"O placar é auditável, não apenas atual. Todo estado visível deriva de um log de eventos append-only."*

### 3. Transição Visual Nativa do Svelte 5
- Usaremos as transições nativas do Svelte (`fly`/`scale` chaveados pelo valor da pontuação com `@media (prefers-reduced-motion)`). Quando o número muda, o dígito anterior transiciona e o novo entra com movimento vertical fluido (180ms), dando clareza imediata sobre quem pontuou.
- *Por que:* Atende ao princípio de produto *"O movimento conta o que mudou"* e respeita o critério de aceite de US2 sem adicionar dependências pesadas de terceiros.

### 4. Ergonomia para Uso com Uma Mão
- No celular, os botões de pontuar ocupam a metade inferior da tela do placar com alvos de toque grandes (botões "+1" com pelo menos 80px de altura e largura cheia por coluna).
- *Por que:* Em pé na beira da quadra, o controlador segura o celular com uma mão e marca com o polegar.

## Fora de Escopo

- Restrição de quem pode marcar ponto por papel (isso pertence a `CV1.DS2 - Controle e Permissões`; nesta US2, qualquer participante registrado na quadra pode pontuar para viabilizar teste end-to-end do núcleo).
- Botão "Desfazer Ponto" (pertence a `CV1.DS1.US3`).
- Visualização de linha do tempo histórica de pontos (pertence a `CV1.DS4.US1`).
- Customização dinâmica de regras da quadra em tempo de execução (pertence a `CV1.DS3.US1`).
- Encerramento formal e botão de reiniciar nova partida (pertence a `CV1.DS1.US4`).

## Riscos e Mitigações

1. **Risco:** Toque duplo rápido acidental por trepidação do dedo do usuário marcar dois pontos.
   - **Mitigação:** Desabilitar temporariamente o botão no frontend durante o voo da requisição (`submetendoPonto = true`) e debounce visual.
2. **Risco:** Latência ou queda de conexão no momento do toque.
   - **Mitigação:** Tratamento de erro na requisição REST com feedback visual em caso de falha; a reconexão automática do WebSocket restaura a verdade do log assim que a rede restabelecer.
