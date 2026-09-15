---
code: CV1.DS2.US2
kind: test-guide
status: Active
updated: 2026-09-15
---

# Guia de Teste e Validação — CV1.DS2.US2: Sucessão automática do admin

Este guia estabelece os testes automatizados e o roteiro de validação multi-dispositivo do Navigator para a história `CV1.DS2.US2`.

---

## 1. Verificação Automatizada

Execute na raiz do projeto:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

### Cobertura de Testes Automatizados (`tests/test_sucessao_admin.py`)

1. **`test_sucessao_promove_controlador_mais_antigo`**:
   - Criação da quadra pelo `Admin A`.
   - Ingressos sequenciais de `Controlador B` (chegou primeiro) e `Controlador C` (chegou depois).
   - Simulação de desconexão do `Admin A` há mais de 120 segundos (`ultimo_visto_em`).
   - Disparo da rotina de sucessão:
     - `Controlador B` é promovido a `ADMIN`.
     - `Admin A` é rebaixado a `CONTROLADOR`.
     - Evento `ADMIN_SUCEDIDO` registrado no log append-only.
     - Projeção na Linha do Tempo: `"Controlador B assumiu a administração por sucessão (ausência de Admin A)"`.

2. **`test_sucessao_retorno_admin_original_como_controlador`**:
   - Após a promoção de `B`, `Admin A` volta a consultar a quadra e reconecta.
   - O papel retornado para `Admin A` é estritamente `CONTROLADOR`.
   - `Admin A` não consegue revogar `B` nem alterar papéis (HTTP 403), mas consegue marcar ponto e desfazer como controlador.

3. **`test_sucessao_sem_controlador_online`**:
   - Quadra com `Admin A` e dois espectadores ou controladores desconectados.
   - Admin ausente há mais de 120s.
   - Sucessão executada: admin original rebaixado a controlador (posto de admin vago).
   - Evento `ADMIN_SUCEDIDO` gravado com `novo_admin_id=None`.
   - Projeção na Linha do Tempo: `"Administração vaga por ausência de Admin A"`.
   - Controladores continuam aptos a marcar e desfazer pontos.

4. **`test_sucessao_nao_dispara_antes_do_tempo_ou_admin_online`**:
   - Admin ativo e conectado: nenhuma sucessão deve ocorrer.
   - Admin desconectado há menos tempo que o limite (ex: 60s quando limite é 120s): nenhuma sucessão disparada.

5. **`test_sucessao_propagacao_websocket`**:
   - Clientes conectados recebem `PLACAR_ATUALIZADO` e `PRESENCA_ATUALIZADA` em tempo real sem intervenção manual quando o temporizador expira.

---

## 2. Roteiro de Validação do Navigator (Multi-dispositivo com 3 clientes)

### Contexto de Validação
Conforme o guia de desenvolvimento, histórias de presença e sucessão exigem validação com **três clientes simultâneos**:
- **Cliente A**: Navegador 1 (Admin criador da quadra).
- **Cliente B**: Navegador 2 / Janela anônima (Primeiro controlador a entrar).
- **Cliente C**: Navegador 3 / Celular (Segundo controlador a entrar).

Para facilitar a validação manual sem esperar 2 minutos inteiros, execute o backend com timeout reduzido (ex: 15 segundos):
```bash
ADMIN_TIMEOUT_SECONDS=15 uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```
*(Se estiver no PowerShell no Windows):*
```powershell
$env:ADMIN_TIMEOUT_SECONDS="15"; uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Passo a Passo

#### 1. Criar e preparar a sala
- **Cliente A**: Acesse `http://localhost:8000`, crie a quadra com o apelido `"Admin A"`. Anote o código de 5 dígitos (ex: `55432`).
- **Cliente B**: Em outro navegador ou janela anônima, acesse a quadra pelo código com o apelido `"Controlador B"`.
- **Cliente C**: Em um terceiro navegador ou celular, acesse a quadra com o apelido `"Controlador C"`.
- **Cliente A**: Na lista de participantes, promova `"Controlador B"` e `"Controlador C"` a controladores clicando em **"Tornar controlador"** em cada um.
- Confirme que tanto B quanto C veem os botões de pontuação e o badge `CONTROLADOR`.

#### 2. Desconexão do Admin A
- No **Cliente A**, feche a aba/navegador (ou ative o modo avião/desconecte a rede do aparelho).
- No **Cliente B** e **Cliente C**, observe a lista de presentes:
  - O status de `"Admin A"` muda para bolinha cinza (offline).

#### 3. Sucessão Automática
- Aguarde o tempo limite (15 segundos configurados no teste ou 2 minutos no padrão).
- **O que observar em B e C (sem recarregar a tela)**:
  - No **Cliente B**:
    - O badge de `"Controlador B"` muda automaticamente para `ADMIN`.
    - Os botões de gerenciamento de permissão (**"Revogar controlador"**) passam a ser visíveis para B na linha de C.
  - No **Cliente C**:
    - O badge de B muda para `ADMIN` e o de A passa para `CONTROLADOR`.
  - Na **Linha do Tempo** (em ambos os clientes):
    - Surge o evento: `"Controlador B assumiu a administração por sucessão (ausência de Admin A)"`.

#### 4. Operação pelo novo Admin B
- No **Cliente B**, clique em `+1 Equipe A`.
- O placar atualiza normalmente para 1 × 0 em todas as telas.

#### 5. Retorno do Admin Original A
- No **Cliente A**, reabra o navegador no link da sala `http://localhost:8000/quadra/55432`.
- **O que observar no Cliente A**:
  - Reconecta com sucesso sem precisar redigitar apelido.
  - Seu papel agora é `CONTROLADOR` (badge azul).
  - Ele NÃO possui os botões de gerenciamento de permissões (pertencem agora a B).
  - Ele consegue pontuar normalmente como controlador (`+1 Equipe B`).

---

## 3. Critérios de Sucesso

- **Condição de Passagem**:
  - Quando o admin fica offline pelo tempo configurado, o controlador mais antigo (B) é promovido a ADMIN de forma 100% automática via WebSocket.
  - O evento `ADMIN_SUCEDIDO` aparece na linha do tempo detalhando quem assumiu.
  - Ao reconectar, o admin original volta como `CONTROLADOR` e não desfaz a promoção de B.
- **Condição de Falha**:
  - O controlador mais novo (C) ser promovido em vez do mais antigo (B);
  - A sucessão exigir F5 ou reload manual para ser percebida;
  - O admin original reconectar e retomar automaticamente o posto de ADMIN;
  - A quadra travar e ninguém conseguir pontuar.
