---
code: CV2.DS1.TS1
kind: test-guide
status: Active
updated: 2026-09-15
---

# Guia de Teste e Validação — CV2.DS1.TS1: Blindagem do snapshot do WebSocket

## 1. Verificação Automatizada

```bash
cd web && npm run build && cd ..
uv run pytest tests/test_blindagem_e_confiabilidade.py
uv run ruff check .
uv run ruff format --check .
```

### Cobertura (`tests/test_blindagem_e_confiabilidade.py`)

1. **`test_espectador_nao_recebe_codigo_mestre_em_nenhum_frame`**
   - Admin cria a sala (que ganha `codigo_mestre` no banco); o teste lê o código direto do SQLite para saber o valor real.
   - Uma segunda identidade entra como `ESPECTADOR` e abre o WebSocket.
   - O admin marca um ponto, forçando o broadcast de `PLACAR_ATUALIZADO`.
   - Todos os frames recebidos pelo espectador são serializados e o teste afirma: a string `codigo_mestre` não aparece **e** o valor do código também não.
   - A chave `quadra` de cada frame tem exatamente os campos da allowlist mais `partida_id`.

2. **`test_coluna_sensivel_futura_fica_fora_do_snapshot_por_padrao`**
   - Uma coluna `token_de_operacao` é adicionada à tabela `quadras` em tempo de execução e preenchida com um segredo.
   - `snapshot_sync()` é chamado e o teste afirma que nem a chave nem o valor aparecem.
   - É este teste que protege a *próxima* coluna sensível, não apenas a atual.

## 2. Roteiro de Validação do Navigator (2 clientes)

### Contexto
- **Cliente A**: navegador comum, admin criador da sala.
- **Cliente B**: janela anônima, espectador.

### Passo a passo

1. Subir a aplicação:
   ```bash
   uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
2. No **Cliente A**, criar um placar em `http://localhost:8000` e anotar o código de 5 dígitos.
3. No **Cliente B**, abrir o DevTools **antes** de entrar (F12 → aba Network → filtro `WS`).
4. Entrar na sala com o código e um apelido. Selecionar a conexão `/ws/<codigo>` → aba **Messages**.
5. **O que observar**: o primeiro frame (`ESTADO_INICIAL`) e, depois de o Cliente A marcar um ponto, o frame `PLACAR_ATUALIZADO`.
6. Usar a busca do DevTools (Ctrl+F dentro do painel de mensagens) por `codigo_mestre`.
7. Conferir também o log do servidor, conforme o contrato de segurança do projeto:
   ```bash
   grep -i "codigo_mestre\|$(grep OWNER_SECRET .env | cut -d= -f2)" <saída do uvicorn>
   ```

### Condição de aprovação
- A busca por `codigo_mestre` nos frames do WebSocket não encontra nenhuma ocorrência, em nenhum dos dois tipos de frame.
- A chave `quadra` traz apenas `id`, `nome`, `criado_em`, `atualizado_em`, `controle_id`, `controle_versao` e `partida_id`.
- O placar continua funcionando normalmente nos dois clientes (nenhum campo que a UI usava sumiu).

### Condição de falha
- Qualquer ocorrência de `codigo_mestre` ou do valor do código em frame recebido por espectador.
- Campos a mais na chave `quadra` além dos listados acima.
- Sala que para de atualizar, nome da quadra que some do cabeçalho ou botão de assumir controle que deixa de funcionar — sinal de que a allowlist cortou um campo que a UI consumia.
