---
code: CV1.DS2.US1
kind: test-guide
status: Active
updated: 2026-09-14
---

# Guia de Teste e Validação — CV1.DS2.US1: Admin promove e revoga controladores

Este guia estabelece os testes automatizados e o roteiro de validação multi-dispositivo do Navigator para a história `CV1.DS2.US1`.

---

## 1. Verificação Automatizada

Execute na raiz do projeto:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

### Cobertura de Testes Automatizados (`tests/test_promover_revogar_controladores.py`)

1. **`test_fluxo_promover_e_revogar_controladores`**:
   - Criação da quadra pelo `Admin A`.
   - Entrada dos participantes `Espectador B` e `Espectador C`.
   - Bloqueio de pontuação, anulação e promoção vindas de `Espectador B` (HTTP 403).
   - Promoção de `Espectador B` para `CONTROLADOR` pelo `Admin A`:
     - Papel atualizado para `CONTROLADOR`.
     - Controle ativo transferido para `B`.
   - `Controlador B` pontua com sucesso (+1 ponto).
   - `Espectador C` tenta pontuar e é rejeitado com HTTP 403.
   - `Admin A` assume o controle de volta via `POST /controle/assumir` e anula o ponto via `POST /desfazer`.
   - `Admin A` revoga o papel de `B` para `ESPECTADOR`:
     - Retorno do controle ao `Admin A`.
     - `B` volta a ser rejeitado com HTTP 403 ao tentar operar o placar.

2. **`test_promover_e_revogar_via_endpoint_papel_e_websocket`**:
   - Verificação da propagação em tempo real via WebSocket de mensagens `PLACAR_ATUALIZADO` com evento `PAPEL_ALTERADO`.
   - Projeção correta na linha do tempo (`"Admin promoveu Carlos a controlador"` e `"Admin revogou controlador de Carlos"`).

---

## 2. Roteiro de Validação do Navigator (Multi-dispositivo com 3 clientes)

### Contexto de Validação
Conforme o guia de desenvolvimento, histórias envolvendo papéis e permissões exigem validação com **três clientes simultâneos**:
- **Cliente A**: Navegador comum (Admin / Dono da quadra).
- **Cliente B**: Janela anônima ou segundo navegador (Promovido a Controlador).
- **Cliente C**: Celular ou terceiro navegador (Permanece Espectador).

### Passo a Passo

#### 1. Iniciar a aplicação
No terminal:
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 2. Entrar na sala
- **Cliente A**: Acesse `http://localhost:8000`, clique em **"Criar Placar"**, informe o apelido `"Admin A"`. Observe o código de 5 dígitos (ex: `12345`).
- **Cliente B**: Em janela anônima ou outro navegador, acesse `http://localhost:8000`, clique em **"Acompanhar"**, digite o código e apelido `"Espectador B"`.
- **Cliente C**: No terceiro navegador ou celular, acesse `http://localhost:8000`, clique em **"Acompanhar"**, digite o código e apelido `"Espectador C"`.

#### 3. Observar o estado inicial
- **Cliente A (Admin)**: Vê o placar interativo com botões `+1 Equipe A`, `+1 Equipe B`, `Desfazer` e a lista de presentes contendo B e C com o botão **"Tornar controlador"**.
- **Clientes B e C**: Veem o placar retrô de espectador (`PlacarManual`), sem botões de pontuação nem de desfazer.

#### 4. Promoção de B a Controlador
- No **Cliente A**, na linha do participante `"Espectador B"`, clique no botão **"Tornar controlador"**.
- **O que observar**:
  - **Cliente B**: Instantaneamente (via WebSocket, sem recarregar a página), sua tela transiciona para o placar interativo com os botões grandes de pontuação (`+1 Equipe A`, `+1 Equipe B`). O badge de seu perfil muda para `CONTROLADOR`.
  - **Cliente C**: Permanece vendo apenas o placar do espectador sem botões. O badge de B na lista de presentes atualiza para `CONTROLADOR`.
  - **Cliente A**: Vê o botão na linha de B alternar para **"Revogar controlador"**.

#### 5. Operação pelo Controlador B
- No **Cliente B**, clique em `+1 Equipe A`.
- **O que observar**:
  - O ponto é marcado: o placar vai para 1 × 0 nos três aparelhos.
  - Na Linha do Tempo, consta: `"Admin A promoveu Espectador B a controlador"` e `"Espectador B marcou ponto para Equipe A"`.

#### 6. Tentativa de violação pelo Espectador C
- No console do desenvolvedor do **Cliente C** (ou via curl):
  ```bash
  curl -X POST http://localhost:8000/api/quadras/{CÓDIGO}/pontos -H "Content-Type: application/json" -d '{"equipe":"B"}'
  ```
- **Condição de aprovação**: A requisição é rejeitada com **HTTP 403** e nenhuma pontuação é alterada.

#### 7. Revogação de B
- No **Cliente A**, clique no botão **"Revogar controlador"** na linha de `"Espectador B"`.
- **O que observar**:
  - No **Cliente B**, os botões de pontuação desaparecem imediatamente e sua tela volta ao modo espectador.
  - O controle ativo retorna para o **Cliente A**.
  - A Linha do Tempo registra `"Admin A revogou controlador de Espectador B"`.

---

## 3. Critérios de Sucesso
- **Condição de Passagem**: B ganha botões ao ser promovido, marca ponto, perde botões ao ser revogado, e tentativas de espectador são rejeitadas no backend com HTTP 403.
- **Condição de Falha**: B não ver os botões após ser promovido sem F5; botões continuarem ativos após revogação; ou espectador conseguir pontuar diretamente pela API.
