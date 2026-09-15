---
code: CV1.DS3.US1
kind: test-guide
status: Active
updated: 2026-09-15
---

# Guia de Teste e Validação — CV1.DS3.US1: Configurar pontuação-alvo, vantagem e teto

Este guia estabelece os testes automatizados e o roteiro de validação multi-dispositivo do Navigator para a história `CV1.DS3.US1`.

---

## 1. Verificação Automatizada

Execute na raiz do projeto:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
npm --prefix web test
npm --prefix web run check
```

### Cobertura de Testes Automatizados (`tests/test_configurar_regras.py`)

1. **`test_configurar_regras_admin`**:
   - Criação da quadra com regras padrão (12 pts, vantagem=True, teto=None).
   - Admin altera regras para alvo 15, vantagem=True, teto 18 via `POST /api/quadras/{id}/regras`.
   - Verifica persistência do evento `REGRA_ALTERADA` no log e atualização de `estado_partida`.
   - Linha do tempo exibe: `"Regra alterada por Admin: alvo 15 pts, com vantagem de 2, teto 18 pts"`.

2. **`test_alteracao_regra_encerra_partida_no_proximo_ponto`**:
   - Partida chega a 11 × 11 com alvo 12 e vantagem ligada.
   - Admin desliga a vantagem (`vantagem=False`).
   - Um ponto é marcado para a Equipe A (12 × 11).
   - Partida encerra formalmente com vitória da Equipe A e evento `PARTIDA_ENCERRADA`.

3. **`test_alteracao_regra_com_posto_vago_permite_controlador`**:
   - Quadra sem admin ativo (posto vago após sucessão).
   - Controlador conectado altera as regras da partida com sucesso.
   - A alteração fica registrada com o apelido do controlador.

4. **`test_bloqueio_de_espectador_e_controlador_com_admin_presente`**:
   - Espectador tenta alterar regra e recebe HTTP 403.
   - Controlador tenta alterar regra enquanto o Admin está presente e recebe HTTP 403.

5. **`test_rejeicao_teto_menor_que_alvo`**:
   - Tentativa de configurar alvo 15 com teto 12.
   - O servidor rejeita com HTTP 422 e mensagem descritiva: `"O teto da vantagem não pode ser menor que a pontuação-alvo."`.

6. **`test_propagacao_regras_websocket`**:
   - Todos os clientes conectados na sala recebem `PLACAR_ATUALIZADO` com as novas regras e a nova linha do tempo em tempo real.

---

## 2. Roteiro de Validação do Navigator (Multi-dispositivo com 2 clientes)

### Contexto de Validação
- **Cliente A**: Navegador comum (Admin criador da sala).
- **Cliente B**: Janela anônima ou celular (Espectador acompanhando o placar).

### Passo a Passo

#### 1. Iniciar a aplicação
No terminal:
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 2. Entrar na sala
- **Cliente A (Admin)**: Crie uma nova quadra com o apelido `"Admin A"`. Observe o código de 5 dígitos gerado.
- **Cliente B (Espectador)**: Em janela anônima ou celular, acesse a sala informando o código e o apelido `"Espectador B"`.
- Observe que no topo de ambos os clientes as regras padrão são exibidas: `Até 12 pts • Vantagem de 2`.

#### 3. Simular empate em 11 × 11
- No **Cliente A**, marque 11 pontos para a Equipe A e 11 pontos para a Equipe B (placar 11 × 11).
- Com a regra de vantagem ligada, um ponto para qualquer lado levaria a 12 × 11 sem encerrar a partida (necessário abrir 2 de vantagem ou atingir o teto).

#### 4. Ajustar regras da partida (Desligar vantagem)
- No **Cliente A**, clique no botão **"⚙️ Regras"**.
- Desmarque a opção **"Exigir vantagem de 2 pontos"**.
- Clique em **"Salvar Regras"**.
- **O que observar**:
  - Em ambos os clientes (sem recarregar a tela), o resumo de regras muda para `Até 12 pts • Sem vantagem`.
  - Na **Linha do Tempo**, surge o registro: `"Regra alterada por Admin A: alvo 12 pts, sem vantagem"`.

#### 5. Marcar o ponto decisivo
- No **Cliente A**, clique em `+1` na Equipe A (placar vai para 12 × 11).
- **O que observar**:
  - A partida encerra imediatamente com vitória da Equipe A!
  - Banner de vitória aparece em ambas as telas e os botões de pontuação são bloqueados.

#### 6. Validação de rejeição de teto menor que alvo
- Inicie uma nova partida no **Cliente A** clicando em **"▶ Iniciar Nova Partida"**.
- Abra novamente **"⚙️ Regras"**.
- Mantenha a vantagem ligada, defina o alvo para `15` e o teto para `10`.
- Clique em **"Salvar Regras"**.
- **Condição de aprovação**: A operação é bloqueada com mensagem clara de erro alertando que o teto não pode ser menor que o alvo.

#### 7. Tentativa de alteração por espectador
- No console do desenvolvedor do **Cliente B** (Espectador):
  ```bash
  curl -X POST http://localhost:8000/api/quadras/{CÓDIGO}/regras -H "Content-Type: application/json" -d '{"alvo":15,"vantagem":false}'
  ```
- **Condição de aprovação**: Requisição rejeitada com **HTTP 403**.

---

## 3. Critérios de Sucesso

- **Condição de Passagem**:
  - As regras são editadas na UI e propagam em tempo real para todos os clientes conectados.
  - O motor de vitória reage imediatamente às regras configuradas (ex: 12x11 encerra sem vantagem).
  - Tentativas com teto < alvo são rejeitadas com erro claro.
  - Espectadores não conseguem alterar as regras (HTTP 403).
- **Condição de Falha**:
  - Alteração de regra exigir F5 para refletir no placar;
  - Desligar a vantagem não permitir encerramento com 1 ponto de diferença ao atingir o alvo;
  - Permitir salvar teto menor que a pontuação-alvo;
  - Espectador conseguir alterar as regras via API.
