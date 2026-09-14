---
code: CV1.DS1.US2
kind: test-guide
status: Active
updated: 2026-09-13
---

# Guia de Teste e Validação — CV1.DS1.US2 Marcar ponto em tempo real

Este guia estabelece os testes automatizados e o roteiro de validação multi-dispositivo para a história `CV1.DS1.US2`.

## 1. Verificação Automatizada

### Testes de Backend (`pytest`)
- `tests/test_pontos.py`:
  - `test_marcar_ponto_equipe_a`: chama `POST /api/quadras/{id}/pontos` com `{"equipe": "A"}` e verifica:
    - Status HTTP 201 ou 200.
    - Evento `PONTO_MARCADO` gravado no banco de dados com autor e payload correspondentes.
    - `estado_partida.pontos_a` igual a 1 e `pontos_b` igual a 0.
  - `test_marcar_ponto_equipe_b`: incrementa pontos da equipe B e confere projeção.
  - `test_marcar_ponto_sem_participante`: requisição sem cookie de sessão/participante válido retorna 401 ou 403.
  - `test_marcar_ponto_partida_encerrada`: quando uma partida atinge o alvo com vitória, novos pontos são rejeitados com 400 ("Partida encerrada").
  - `test_websocket_broadcast_ponto`: cliente WebSocket conectado na quadra recebe mensagem `PLACAR_ATUALIZADO` imediatamente após o ponto ser marcado via REST.

### Testes de Frontend (`svelte-check` e build)
- `npm run check` em `web/`: zero erros de tipagem/runes.
- `npm run build` em `web/`: gera artefatos estáticos em `app/static/` sem avisos impeditivos.

---

## 2. Roteiro de Validação do Navigator (Multi-dispositivo)

Conforme os princípios do projeto, estado compartilhado requer validação em pelo menos dois clientes simultâneos.

### Preparação
1. Suba a aplicação localmente:
   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
2. Abra dois navegadores diferentes ou um celular e um navegador no computador:
   - **Cliente 1 (Controlador/Admin):** Navegador principal ou Celular A (`http://localhost:8000`).
   - **Cliente 2 (Espectador):** Navegador anônimo ou Celular B (`http://<seu-ip-local>:8000`).
3. Ambos entram na mesma arena (ex: "T9 Beach Club") e na mesma quadra (ex: "Quadra 1").
   - Cliente 1 entra com apelido "Eli".
   - Cliente 2 entra com apelido "Visitante".
4. Verifique que ambos os clientes mostram a tela do placar com o indicador verde **"Ao vivo"** e o placar em `0 × 0`.

### Passos de Teste

#### Passo 1: Marcação de Ponto e Propagação Simultânea
- **Ação:** No Cliente 1, toque no botão **"+1"** da **Equipe A**.
- **Observação esperada:**
  - O placar da Equipe A no Cliente 1 transiciona com animação fluida para **1**.
  - No Cliente 2 (sem nenhum clique), o placar da Equipe A atualiza para **1** quase instantaneamente (menos de 500ms).
- **Condição de Aprovação:** Ambas as telas exibem `1 × 0` e o dígito realizou transição visual.
- **Condição de Falha:** O número mudar seco sem transição, ou uma das telas demorar mais de 2 segundos ou exigir recarregamento manual.

#### Passo 2: Marcação Alternada
- **Ação:** No Cliente 2, toque no botão **"+1"** da **Equipe B**.
- **Observação esperada:** Ambas as telas atualizam sincronizadas para `1 × 1`.
- **Condição de Aprovação:** Ambas as telas mostram `1 × 1`.
- **Condição de Falha:** Divergência de placar entre as telas.

#### Passo 3: Ergonomia com Uma Mão
- **Ação:** Teste o botão de ponto em um celular real usando apenas o polegar com a mão que segura o aparelho.
- **Observação esperada:** A área de toque é grande e confortável, sem risco de toque falso em elementos vizinhos.
- **Condição de Aprovação:** Toque confortável e imediato.

#### Passo 4: Resiliência de Conexão e Reconciliação (Modo Avião)
- **Ação:**
  1. No Cliente 2 (celular), ative o **Modo Avião** (ou desligue o Wi-Fi).
  2. No Cliente 1, marque mais 2 pontos para a Equipe A (placar vai para `3 × 1`).
  3. Aguarde 20 a 30 segundos.
  4. No Cliente 2, desative o Modo Avião (reconecte a rede).
- **Observação esperada:**
  - Assim que a conexão for restabelecida, o indicador volta a **"Ao vivo"**.
  - O placar no Cliente 2 reconcilia automaticamente para `3 × 1` **sem** que o usuário precise recarregar ou tocar na tela.
- **Condição de Aprovação:** Placar reconciliado em `3 × 1` de forma transparente.
- **Condição de Falha:** Tela do Cliente 2 ficar travada em `1 × 1` até um recarregamento manual da página.
