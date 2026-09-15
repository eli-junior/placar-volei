---
code: CV2.DS1.US2
kind: test-guide
status: Active
updated: 2026-09-15
---

# Guia de Teste e Validação — CV2.DS1.US2: Erros de validação compreensíveis

## 1. Verificação Automatizada

```bash
cd web && npm run check && npm test && npm run build && cd ..
uv run pytest tests/test_blindagem_e_confiabilidade.py -k 422
uv run ruff check . && uv run ruff format --check .
```

### Cobertura de backend (`tests/test_blindagem_e_confiabilidade.py`)

1. **`test_422_de_campo_obrigatorio_tem_detalhe_legivel`** — `POST /entrar` sem corpo devolve `detail == "Apelido é obrigatório."` e a lista `erros` com `campo`, `rotulo`, `mensagem` e `tipo` exatos.
2. **`test_422_de_limites_descreve_cada_campo`** — apelido, nome e alvo inválidos na mesma requisição produzem uma frase citando os três limites reais e `erros` com os três campos.
3. **`test_422_de_regra_de_negocio_continua_string_simples`** — teto menor que o alvo continua com a frase específica da regra, provando que o handler genérico não sequestrou os 422 lançados à mão.

### Cobertura de frontend (`web/tests/sync.test.js`, `node --test`)

4. **`erro normalizado do backend chega como frase legível`**.
5. **`422 cru do FastAPI nunca vira "[object Object]"`** — alimenta `mensagemDeErro()` com o formato antigo (lista de dicionários com `loc`/`msg`) e afirma que a saída é texto útil.
6. **`corpo sem descrição cai na mensagem alternativa`** — `{}`, `null` e `{detail: {}}` devolvem a alternativa da ação.

## 2. Roteiro de Validação do Navigator

### Preparação

```bash
cd web && npm run build && cd ..
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Passo 1 — Formato da resposta pela linha de comando

```bash
# cria uma sala e guarda o código
CODIGO=$(curl -s -X POST localhost:8000/api/quadras \
  -H 'Content-Type: application/json' -d '{"apelido":"Admin"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')

# campo obrigatório ausente
curl -s -X POST localhost:8000/api/quadras/$CODIGO/entrar \
  -H 'Content-Type: application/json' -d '{}'

# vários limites errados de uma vez
curl -s -X POST localhost:8000/api/quadras \
  -H 'Content-Type: application/json' \
  -d '{"apelido":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","alvo":0}'

# regra de negócio (não passa pelo tradutor genérico)
curl -s -X POST localhost:8000/api/quadras \
  -H 'Content-Type: application/json' -d '{"alvo":15,"teto":10}'
```

**O que observar** — as respostas precisam ser, respectivamente:

```json
{"detail": "Apelido é obrigatório.", "erros": [{"campo": "apelido", "rotulo": "Apelido", "mensagem": "é obrigatório", "tipo": "missing"}]}
{"detail": "Apelido deve ter no máximo 30 caractere(s). Pontuação-alvo deve ser no mínimo 1.", "erros": [ ... dois itens ... ]}
{"detail": "O teto da vantagem não pode ser menor que a pontuação-alvo."}
```

### Passo 2 — Mensagem na tela

O formulário da tela inicial já limita o apelido com `maxlength="30"`, então é preciso burlar o limite do navegador para ver o erro do servidor:

1. Abrir `http://localhost:8000` e o DevTools (F12) na aba **Console**.
2. Colar:
   ```js
   await fetch('/api/quadras', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({ apelido: 'a'.repeat(40) })
   }).then(r => r.json())
   ```
   e conferir que o `detail` que aparece no console é a frase em português.
3. Alternativa pela interface: na aba **Elements**, selecionar o campo de apelido, remover o atributo `maxlength`, digitar 40 caracteres e enviar o formulário.
   - **O que observar**: a mensagem de erro exibida acima do formulário é `Apelido deve ter no máximo 30 caractere(s).`

### Passo 3 — Regra de negócio pela interface

1. No formulário de criação, escolher pontuação-alvo `15`, ligar a vantagem e digitar teto `10`.
2. **O que observar**: a validação preventiva do formulário já bloqueia. Se for enviado mesmo assim (removendo a trava pelo DevTools), a mensagem do servidor aparece completa e específica.

## 3. Critérios de Sucesso

### Condição de aprovação
- Nenhuma tela do produto exibe `"[object Object]"` em nenhum caminho de erro.
- Todo 422 de validação traz `detail` como frase única em português nomeando o campo e o limite real.
- O campo `erros` traz o detalhamento estruturado (`campo`, `rotulo`, `mensagem`, `tipo`).
- Os 422 de regra de negócio continuam com o texto específico da regra, sem tradução genérica.
- Um erro sem descrição aproveitável cai na mensagem alternativa da ação, não em texto vazio.

### Condição de falha
- `"[object Object]"`, `"undefined"` ou mensagem vazia em qualquer erro.
- `detail` voltando como lista ou objeto.
- Mensagem em inglês para os tipos de erro cobertos (`missing`, limites de texto, limites numéricos, tipo inteiro).
- Texto genérico ("Não foi possível criar o placar") substituindo uma mensagem específica que o servidor forneceu.
