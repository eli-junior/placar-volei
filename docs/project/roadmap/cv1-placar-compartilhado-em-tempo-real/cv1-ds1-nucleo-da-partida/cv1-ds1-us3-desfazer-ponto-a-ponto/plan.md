---
code: CV1.DS1.US3
kind: plan
status: Implemented
approved_by: Navigator
updated: 2026-09-13
---

# Plano — CV1.DS1.US3 Desfazer ponto a ponto até zerar

## Nível e Versão

- **Nível:** User Story (`CV1.DS1.US3`)
- **Versão alvo:** `0.1.0` (terceira entrega de `CV1.DS1 - Núcleo da Partida`)

## Escopo

1. **Backend (FastAPI + Event Store):**
   - Novo endpoint REST para anulação de ponto:
     - `POST /api/quadras/{quadra_id}/desfazer`:
       - Valida a existência da quadra e partida ativa.
       - Valida autenticação da sessão do participante (`session_id`).
       - Carrega eventos existentes da partida e obtém a projeção atual (`projetar_estado`).
       - Verifica se há pontos a desfazer: se `len(estado_atual.eventos_ativos_seq) == 0` (placar em 0 × 0), retorna HTTP 400 ("Nenhum ponto para desfazer").
       - Seleciona o sequence number do último ponto marcado ativo: `ref_seq = estado_atual.eventos_ativos_seq[-1]`.
       - Grava atomicamente o evento append-only `PONTO_DESFEITO` no banco com `payload={"ref_seq": ref_seq}` e `autor_id` do participante.
       - Recalcula a projeção determinística (`projetar_estado`), que automaticamente anula o ponto referenciado e reavalia a condição de vitória (reabrindo a partida caso tenha anulado o ponto do match point).
       - Dispara broadcast WebSocket para todos os conectados da quadra com `PLACAR_ATUALIZADO`.
       - Retorna o evento gravado e o novo `estado_partida`.

2. **Frontend (Svelte 5):**
   - **Botão de Desfazer em [`Placar.svelte`](file:///D:/projetos/placar_volei/web/src/components/Placar.svelte):**
     - Botão ergonômico "↺ Desfazer Último Ponto", posicionado logo abaixo dos botões de marcação.
     - Visibilidade clara e acessível a um toque (sem diálogos de confirmação invasivos, respeitando o princípio *"Corrigir é tão barato quanto marcar"*).
     - Estado habilitado/desabilitado reativo: fica desabilitado quando `pontosA + pontosB === 0` ou durante o envio da requisição.
     - Se o último ponto da vitória for desfeito, o placar reverte os números, o banner de vitória desaparece e os botões de marcação "+1" são reabilitados automaticamente em tempo real.
     - Feedback háptico leve (`navigator.vibrate?.(30)`) e proteção contra clique duplo acidental.
   - **Comunicação e Sincronização:**
     - Função `handleDesfazerPonto` em `App.svelte` chamando `POST /api/quadras/{id}/desfazer`.
     - Atualização instantânea de `estadoPartida` local e via broadcast WebSocket `PLACAR_ATUALIZADO`.

## Comportamento de Aceite (BDD)

```gherkin
Given uma partida em andamento com placar em 5x3
When o participante toca no botão "Desfazer" três vezes seguidas
Then o placar atualiza para 3x2 em todas as telas em tempo real
And o log no banco contém 3 eventos PONTO_DESFEITO adicionais, com o histórico original 100% preservado
And o botão Desfazer permanece habilitado enquanto houver pontos no placar
And ao desfazer todos os pontos até 0x0, o botão Desfazer torna-se inativo (disabled)
And se o placar estava em 12x0 (encerrada com vitória) e o 12º ponto for desfeito, a partida volta a ficar em andamento (11x0) e os botões de marcação são reativados.
```

## Decisões de Design

### 1. Desfazer por Sequência Inversa do Log Ativo (`eventos_ativos_seq`)
- O modelo de projeção em `app/projecao.py` já calcula a tupla ordenada `eventos_ativos_seq` (todos os pontos marcados cujo `seq` ainda não foi referenciado por nenhum `PONTO_DESFEITO`). O último ponto ativo é simplesmente `eventos_ativos_seq[-1]`.
- *Por que:* É determinístico, imutável e à prova de condições de corrida: se 10 pontos foram marcados, desfazer 10 vezes reverte exatamente ponto a ponto em ordem LIFO (Last-In, First-Out), sem apagar nada do banco.

### 2. Reversão Automática do Fim de Partida
- Como `projetar_estado` reavalia `avaliar_vitoria` a cada novo estado gerado, desfazendo o ponto final da partida faz com que `encerrada` volte a ser `False` e `vencedor` volte a ser `None`.
- *Por que:* Atende perfeitamente ao princípio *"Corrigir é tão barato quanto marcar"*. Um ponto acidental que encerrou o jogo pode ser corrigido imediatamente com um toque.

### 3. Sem Modal de Confirmação
- Nenhum modal de confirmação do tipo "Tem certeza que deseja desfazer?".
- *Por que:* O princípio de produto estabelece explicitamente: *"desfazer é ponto a ponto, sem limite, até zerar, e está a um toque de distância — nunca atrás de menu, confirmação modal ou tela de histórico"*.

## Fora de Escopo

- Desfazer eventos que não sejam ponto (ex: mudança de regra, troca de papel).
- Refazer (Redo).
- Restrição de papel para quem pode desfazer (entra em `CV1.DS2`).

## Riscos e Mitigações

1. **Risco:** Múltiplos cliques rápidos no botão de desfazer enquanto a requisição viaja.
   - **Mitigação:** Desabilitar o botão durante a submissão com debounce e validação no backend de `eventos_ativos_seq`.
