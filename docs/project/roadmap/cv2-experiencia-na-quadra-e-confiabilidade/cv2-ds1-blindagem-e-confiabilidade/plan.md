# Plano de Implementação — CV2.DS1: Blindagem e Confiabilidade do Placar

## 1. Contexto e Motivação
A análise técnica de frontend apontou três vulnerabilidades e fragilidades críticas:
- **C1:** O payload de WebSocket enviava `codigo_mestre` para todos os participantes (inclusive espectadores) devido ao `SELECT * FROM quadras` na função `snapshot` em `app/comandos.py`.
- **C2:** Participantes desconectados contavam indefinidamente para o teto de 20 pessoas por sala, abrindo brecha para esgotamento por fantasmas.
- **C3:** A função de envio de pontos no frontend descartava silenciosamente toques quando `operando === true` ou quando o WebSocket estava desconectado (`!conectado`), sem nenhum feedback visual nem fila, causando desconfiança no placar em redes 4G instáveis.
- **A7:** Respostas de erro 422 com array de validação do Pydantic eram renderizadas como `"[object Object]"` no frontend.

---

## 2. Escopo Concreto das Alterações

### Backend
1. **Remoção de `codigo_mestre` do Snapshot Público:**
   - Em `app/comandos.py`, na função `snapshot(conn, quadra_id)`:
     Excluir `codigo_mestre` do dicionário `sala` retornado. Apenas campos públicos (`id`, `nome`, `criado_em`, `atualizado_em`, `partida_id`, `controle_id`, `controle_versao`) devem compor o estado transmitido pelo WebSocket.
   - Rotacionar/garantir que `listar_quadras_owner` continue sendo o único local protegido para visualização do operador.
2. **Capacidade Baseada em Participantes Online / Limpeza de Inativos:**
   - Em `app/quadras.py` no endpoint de entrada (`adicionar_participante_sync`), checar se a contagem de participantes considera apenas participantes vistos recentemente ou ativos, evitando que reconexões ou abas fechadas bloqueiem novos ingressantes.
3. **Normalização de Erros de Validação 422:**
   - Em `app/main.py`, adicionar um exception handler global para `RequestValidationError` do FastAPI, formatando o retorno JSON com `{"detail": "Mensagem amigável descritiva"}` em português.

### Frontend
1. **Feedback Visual e Prevenção de Toques Perdidos no +1 (C3):**
   - No componente de placar / sala:
     - Quando uma operação de ponto ou desfazer estiver em andamento (`operando === true`), exibir indicador visual no botão (classe `enviando`, `aria-busy="true"` ou spinner sutil).
     - Se o WebSocket estiver desconectado, desabilitar visualmente os botões com tooltip/aviso \"Reconectando…\".
     - Em vez de ignorar toques subsequentes com `return` mudo, implementar uma pequena fila ou debounce seguro com feedback auditivo/tátil que informe quando uma ação está em fila de envio.
2. **Tratamento Resiliente de Mensagens de Erro (A7):**
   - No tratamento de erros de API do frontend, inspecionar se `detail` é array ou objeto antes de convertê-lo em string, exibindo a concatenação das mensagens das propriedades.

---

## 3. Critérios de Aceite (BDD)

### Cenário 1: Sigilo do Código Mestre no WebSocket
- **Given** uma quadra criada com código mestre persistido no SQLite
- **When** um espectador conecta ao WebSocket `/ws/{quadra_id}`
- **Then** a mensagem `ESTADO_INICIAL` recebida contém os dados da quadra e partida
- **And** a chave `codigo_mestre` **não** está presente em `payload.quadra` nem em nenhuma mensagem de broadcast `PLACAR_ATUALIZADO`.

### Cenário 2: Tratamento de Erros 422
- **Given** uma requisição POST com corpo inválido enviada ao backend
- **When** o servidor responde HTTP 422
- **Then** a resposta contém uma mensagem de erro compreensível em português
- **And** o frontend nunca exibe a string `"[object Object]"`.

### Cenário 3: Feedback Visual no Envio de Ponto
- **Given** o controlador tocando no botão +1
- **When** a requisição de ponto está em trânsito pela rede
- **Then** o botão exibe imediatamente o estado de envio (`aria-busy="true"`)
- **And** caso o WebSocket esteja desconectado, o botão fica visualmente desabilitado indicando reconexão.

---

## 4. O que está Fora de Escopo
- Alterações no layout em paisagem (Modo Quadra) ou temas de cor (Modo Sol) — pertencem a `CV2.DS2`.
- Redesenho da Home ou reestruturação de Design System — pertencem a `CV2.DS3`.

---

## 5. Intenção de Versão
- **Versão:** `0.5.0` (minor) — início do Capability Value 2 (CV2), introduzindo garantias de segurança no protocolo em tempo real e melhorias significativas de confiabilidade e tratamento de erros.
