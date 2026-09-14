---
code: CV1.DS1.US4
kind: plan
status: Proposed
approved_by: Navigator (Ajustado)
updated: 2026-09-14
---

# Plano — CV1.DS1.US4 Encerramento da partida e reinício sob demanda

## Nível e Versão

- **Nível:** User Story (`CV1.DS1.US4`)
- **Versão alvo:** `0.3.0` (fechamento do arco de entrega `CV1.DS1 - Núcleo da Partida`)
- **Branch:** `feature/cv1-ds1-us4-encerramento-e-reinicio`

## Escopo

1. **Gravação do evento explícito `PARTIDA_ENCERRADA`:**
   - Quando um ponto marcado atinge a condição de vitória (`avaliar_vitoria` retorna `True`), o backend grava atomicamente o evento append-only `PARTIDA_ENCERRADA` no log da partida, com `vencedor` ("A" ou "B"), placar final e regras vigentes.
   - Atualiza a tabela `partidas` para `status = 'ENCERRADA'` e `encerrado_em = <timestamp>`.
   - Se o ponto da vitória for desfeito com `PONTO_DESFEITO` logo em seguida, a projeção reabre a partida (`encerrada = False`, `vencedor = None`) e o registro no banco volta para `status = 'EM_ANDAMENTO'`, `encerrado_em = NULL`.

2. **Endpoint REST para Reinício / Nova Partida na Quadra:**
   - `POST /api/quadras/{quadra_id}/reiniciar`:
     - Autenticação e autorização via sessão (Admin/Controlador).
     - Sob o lock da quadra (`get_quadra_lock`), valida se a partida atual já foi encerrada.
     - Garante que a partida anterior está arquivada no banco com seu log append-only completo.
     - Cria um novo registro em `partidas` com `id = uuid()`, `status = 'EM_ANDAMENTO'`, `criado_em = <agora>`.
     - Grava o evento `PARTIDA_INICIADA` para a nova partida herdando a configuração de regras da partida anterior (`alvo`, `vantagem`, `teto`, `equipe_a`, `equipe_b`).
     - Transmite broadcast WebSocket com `PLACAR_ATUALIZADO` apontando para a nova partida em 0x0.

3. **WebSocket Contínuo entre Partidas:**
   - Em `app/main.py`, remove a desconexão equivocada de WebSocket quando `partida_id` muda. A sala só é considerada expirada se a quadra foi removida (`atual is None`).
   - Todos os clientes conectados à quadra continuam ouvindo os broadcasts normalmente e recebem a transição da nova partida em tempo real.

4. **Frontend (Svelte 5):**
   - **Anúncio de Vitória Festivo e Destacado:**
     - Quando `encerrada` é verdadeira, exibe banner comemorativo com o nome da equipe vencedora, ícone de troféu e celebração visual respeitando `prefers-reduced-motion`.
     - Desabilita os botões de marcação "+1" enquanto a partida estiver encerrada.
   - **Controle Sob Demanda (Sem Reinício Automático):**
     - Exibe o botão de destaque **"Iniciar Nova Partida"** para o administrador / controlador.
     - Para espectadores, exibe indicação de que o jogo acabou e aguarda o início da próxima partida.
     - O botão *"↺ Desfazer Último Ponto"* permanece ativo e visível para o admin; se acionado, anula o ponto da vitória, cancela o encerramento e reabre o jogo em andamento (ex: de 12x10 volta para 11x10).
     - Quando o admin clica no botão "Iniciar Nova Partida", chama `POST /api/quadras/{quadra_id}/reiniciar`.
     - Ao receber a nova partida via WebSocket, todas as telas transitam com fluidez para 0x0.

## Comportamento de Aceite (BDD)

```gherkin
Scenario: Vitória direta (12x10) e reinício sob demanda
  Given uma quadra configurada para 12 pontos com vantagem de 2
  When o Time A marca ponto e o placar atinge 12x10
  Then todas as telas anunciam a vitória do Time A
  And o evento PARTIDA_ENCERRADA é gravado no log
  And a partida atual é marcada como ENCERRADA
  And o placar permanece na tela com o resultado final
  And um botão "Iniciar Nova Partida" é exibido para o controlador
  When o controlador clica em "Iniciar Nova Partida"
  Then uma nova partida inicia em 0x0 na mesma quadra com as mesmas regras em todas as telas

Scenario: Vantagem após empate (14x12)
  Given uma quadra com partida empatada em 11x11 (alvo 12 com vantagem)
  When o Time A marca ponto chegando a 12x11
  Then a partida NÃO é encerrada e segue em andamento
  When o Time B empata em 12x12 e depois Time A faz 13x12
  Then a partida permanece em andamento
  When o Time A marca o 14º ponto (14x12)
  Then a partida encerra com anúncio de vitória do Time A

Scenario: Encerramento com teto atingido (15x14)
  Given uma quadra com alvo 12, vantagem de 2 e teto em 15
  When o placar chega a 14x14 e o Time A marca ponto (15x14)
  Then a partida encerra imediatamente com vitória do Time A pelo teto configurado

Scenario: Desfazer ponto da vitória
  Given uma partida recém-encerrada em 12x10 com anúncio de vitória exibido
  When o admin toca em "Desfazer Último Ponto"
  Then o 12º ponto é anulado via PONTO_DESFEITO
  And o placar retorna para 11x10 em andamento
  And o anúncio de vitória é removido e o botão "Iniciar Nova Partida" desaparece
  And os botões de marcação "+1" são reabilitados em todas as telas
```

## Decisões de Design

### 1. Reinício Sob Demanda por Botão Explícito
- A partida finalizada permanece em exibição na tela com o placar final e o vencedor anunciado até que o responsável decida iniciar o próximo jogo clicando no botão "Iniciar Nova Partida".
- *Decisão do Navigator:* Não utilizar reinício automático por timer. A quadra tem o seu tempo de descanso, conversa ou troca de jogadores entre partidas.

### 2. Gravação Explícita de `PARTIDA_ENCERRADA` no Log
- Gravar um evento explícito `PARTIDA_ENCERRADA` no log garante que o término da partida seja um fato histórico imutável com carimbo UTC e autor/sistema.

### 3. Preservação da Sala (Quadra) e Participantes
- Ao reiniciar a partida, o código numérico de 5 dígitos da quadra, o nome da quadra e a lista de participantes permanecem intactos. Apenas a entidade `partida_id` é renovada.

## Fora de Escopo

- Placar geral acumulado de vitórias por rodada (ex: Time A 3 x 2 Time B).
- Tela de histórico para navegar e rever partidas anteriores já encerradas.
- Configuração de regras customizadas via interface de usuário (permanece em DS3).

## Riscos e Mitigações

1. **Risco:** Desconexão indevida de espectadores durante o reinício da partida.
   - **Mitigação:** Remoção da checagem estrita de `partida_id` no loop de keepalive do WebSocket; o WebSocket só encerra se a quadra foi apagada do banco.
2. **Risco:** Dois administradores disparando `/reiniciar` simultaneamente.
   - **Mitigação:** Tratamento sob o lock da quadra com idempotência no backend.
