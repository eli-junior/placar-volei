# Guia de Teste e Validação — CV1.DS1.TS3

## Verificação Automatizada

Executar suite completa de testes:
```bash
uv run pytest
```
Resultado esperado: 45 testes passando com sucesso.

Executar linter e formatador:
```bash
uv run ruff check . ; uv run ruff format --check .
```
Resultado esperado: 0 erros, tudo formatado.

## Rota de Validação do Navigator

### Rota 1 — Preservação de Arenas após Reset do Banco

1. Verifique o conteúdo atual de `defaultArenas.json`:
   - Esperado: Contém "T9 Beach Club" com "Quadra 01" e "Tio Cleo", e "Tio Cleo" com "So tem uma".
2. Pare qualquer servidor em execução e apague o arquivo de banco de teste/desenvolvimento:
   ```powershell
   Remove-Item data/placar.db -ErrorAction SilentlyContinue
   ```
3. Inicie o servidor:
   ```powershell
   uv run uvicorn app.main:app --reload --port 8000
   ```
4. Abra o navegador em `http://localhost:8000`:
   - **O que observar:** A lista de arenas carrega imediatamente com "T9 Beach Club" e "Tio Cleo".
   - Ao clicar em "T9 Beach Club", as quadras "Quadra 01" e "Tio Cleo" estão disponíveis para jogo.
   - **Condição de aprovação:** Arenas e quadras presentes e funcionais mesmo após deletar o `.db`.
   - **Condição de falha:** Tela vazia pedindo para criar a primeira arena.

### Rota 2 — Atualização Contínua ao Criar Nova Arena e Quadra

1. Na tela inicial (`http://localhost:8000`), clique em **+ Nova Arena**.
2. Crie uma arena com nome *"CT Litoral"* e depois crie uma quadra *"Quadra Praia"*.
3. Abra o arquivo `defaultArenas.json` no editor ou terminal:
   - **O que observar:** A nova arena *"CT Litoral"* e sua quadra *"Quadra Praia"* foram adicionadas ao JSON automaticamente.
   - **Condição de aprovação:** `git status` mostra `defaultArenas.json` modificado e pronto para commit/push no Git.
   - **Condição de falha:** O arquivo JSON não reflete a nova arena ou quadra.
