---
code: CV1.DS1.US4
kind: plan
status: Proposed
approved_by: Navigator (Pendente)
updated: 2026-09-14
---

# Plano — CV1.DS1.US4 Encerramento automático e reinício da partida

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
     - Sob o lock da quadra (`get_quadra_lock`), valida se a partida atual já foi encerrada (idempotente: se já estiver em 0x0 de uma nova partida, retorna o snapshot).
     - Garante que a partida anterior está arquivada no banco com seu log append-only completo.
     - Cria um novo registro em `partidas` com `id = uuid()`, `status = 'EM_ANDAMENTO'`, `criado_em = <agora>`.
     - Grava o evento `PARTIDA_INICIADA` para a nova partida herdando a configuração de regras da partida anterior (`alvo`, `vantagem`, `teto`, `equipe_a`, `equipe_b`).
     - Transmite broadcast WebSocket com `PLACAR_ATUALIZADO` apontando para a nova partida em 0x0.

3. **WebSocket Contínuo entre Partidas:**
   - Em `app/main.py`, remove a desconexão equivocada de WebSocket quando `partida_id` muda (que tratava como sala expirada). A sala só é considerada expirada se a quadra foi removida (`atual is None`).
   - Todos os clientes conectados à quadra continuam ouvindo os broadcasts normalmente e recebem a transição da nova partida em tempo real.

4. **Frontend (Svelte 5):**
   - **Anúncio de Vitória Festivo e Destacado:**
     - Quando `encerrada` é verdadeira, exibe banner comemorativo com o nome da equipe vencedora, ícone de troféu e animação de celebração respeitando `prefers-reduced-motion`.
     - Desabilita os botões de marcação "+1" enquanto a partida estiver encerrada.
   - **Transição Automática e Controle:**
     - Temporizador visual regressivo: *"Próxima partida em 5s..."* (atendendo ao requisito de produto *"sem ninguém precisar mexer em nada"*).
     - Botão imediato *"Iniciar Nova Partida Agora"* para quem preferir iniciar sem aguardar a contagem.
     - O botão *"↺ Desfazer Último Ponto"* permanece ativo e visível para o admin durante a contagem. Se acionado, anula o ponto, cancela a contagem e reabre o jogo em andamento.
     - Ao zerar o contador, o cliente admin dispara automaticamente `POST /api/quadras/{quadra_id}/reiniciar`.
     - Ao receber a nova partida via WebSocket, todas as telas resetam com transição fluida para 0x0.

## Comportamento de Aceite (BDD)

```gherkin
Scenario: Vitória direta (12x10) e reinício automático
  Given uma quadra configurada para 12 pontos com vantagem de 2
  When o Time A marca ponto e o placar atinge 12x10
  Then todas as telas anunciam a vitória do Time A
  And o evento PARTIDA_ENCERRADA é gravado no log
  And a partida atual é marcada como ENCERRADA
  And o sistema inicia uma contagem regressiva de 5 segundos
  And ao final da contagem, uma nova partida inicia em 0x0 na mesma quadra com as mesmas regras

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

Scenario: Desfazer ponto da vitória durante o anúncio
  Given uma partida recém-encerrada em 12x10 com anúncio de vitória exibido
  When o admin toca em "Desfazer Último Ponto"
  Then o 12º ponto é anulado via PONTO_DESFEITO
  And o placar retorna para 11x10 em andamento
  And o anúncio de vitória e a contagem regressiva são cancelados
  And os botões de marcação são reabilitados em todas as telas
```

## Decisões de Design

### 1. Gravação Explícita de `PARTIDA_ENCERRADA` no Log
- Além da projeção em memória avaliar a condição de vitória dinamicamente, gravar um evento explícito `PARTIDA_ENCERRADA` no log garante que o término da partida seja um fato histórico imutável com carimbo UTC e autor/sistema.
- *Por que:* Cumpre o princípio *"O placar é auditável, não apenas atual"* e fecha formalmente o log de eventos daquela partida antes de arquivá-la.

### 2. Transição com Janela de Anúncio e Desfazer
- A partida não é zerada instantaneamente em 0 ms no mesmo milissegundo em que o ponto entra. Ela exibe o anúncio de vitória por 5 segundos com uma contagem regressiva visível, permitindo que todos vejam quem ganhou e que o admin corrija um toque errado antes do início da próxima partida.
- *Por que:* Atende simultaneamente ao requisito *"sem ninguém precisar mexer em nada"* e ao princípio *"Corrigir é tão barato quanto marcar"*.

### 3. Preservação da Sala (Quadra) e Participantes
- Ao reiniciar a partida, o código numérico de 5 dígitos da quadra, o nome da quadra e a lista de participantes permanecem intactos. Apenas a entidade `partida_id` é renovada.
- *Por que:* O grupo que está na pelada não precisa sair da sala, digitar PIN de novo ou escolher apelido novamente para jogar a próxima partida.

## Fora de Escopo

- Placar geral acumulado de vitórias por rodada (ex: Time A 3 x 2 Time B).
- Tela de histórico para navegar e rever partidas anteriores já encerradas.
- Configuração de regras customizadas via interface de usuário (permanece em DS3).

## Riscos e Mitigações

1. **Risco:** Desconexão indevida de espectadores durante o reinício da partida.
   - **Mitigação:** Remoção da checagem estrita de `partida_id` no loop de keepalive do WebSocket; o WebSocket só encerra se a quadra foi apagada do banco.
2. **Risco:** Dois administradores disparando `/reiniciar` simultaneamente.
   - **Mitigação:** Tratamento sob o lock da quadra com idempotência no backend.
