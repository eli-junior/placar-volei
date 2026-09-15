---
code: CV2.DS1.US2
level: User Story
status: Validated
status_reason: implementada e testada, aguardando validação do Navigator
updated: 2026-09-15
related:
  - CV2.DS1.US1
  - docs/project/debt/items/2026-09-15T2210Z-toques-perdidos-e-erros-422-nao-normalizados.md
---

# CV2.DS1.US2 — Erros de validação aparecem como frase compreensível

## Intent

Substituir o `"[object Object]"` por uma frase em português que diga qual campo está errado e por quê, tanto quando o erro vem da validação automática do FastAPI quanto quando vem de uma regra de negócio.

## Scope

- `app/api.py`: `normalizar_erros_validacao()` traduz os erros do Pydantic para frases curtas em português, com rótulos amigáveis por campo, e devolve um formato estável.
- `app/main.py`: handler de `RequestValidationError` que responde 422 com `{"detail": "<frase>", "erros": [...]}` e registra a requisição inválida no log da aplicação.
- `web/src/sync.js`: `mensagemDeErro()` extrai texto legível de qualquer forma de `detail` (string, lista de objetos do FastAPI, objeto solto), com mensagem alternativa quando não há nada aproveitável.
- `web/src/App.svelte`: as três chamadas que renderizavam `data.detail` direto passam a usar `mensagemDeErro()`.
- Testes de backend sobre o formato e testes de frontend (`node --test`) sobre a extração.

## Acceptance / Done Condition

```gherkin
Given a tela inicial de criar placar
When eu envio um apelido com mais de 30 caracteres
Then a interface mostra "Apelido deve ter no máximo 30 caractere(s)."
And em nenhuma hipótese aparece o texto "[object Object]"

Given uma requisição sem o campo obrigatório de apelido para entrar na sala
When o backend recusa com HTTP 422
Then o corpo da resposta traz detail como uma única frase legível
And traz a lista erros com campo, rótulo, mensagem e tipo para quem quiser destacar o campo culpado

Given um erro de regra de negócio, como teto menor que a pontuação-alvo
When o backend recusa com HTTP 422
Then a mensagem continua sendo a frase específica da regra, sem passar pelo tradutor genérico

Given uma resposta de erro inesperada, sem detail aproveitável
When a interface precisa exibir algo
Then aparece a mensagem alternativa da ação, nunca um objeto serializado.
```

## Validation Route

1. Na tela inicial, tentar criar um placar com apelido muito longo e conferir o texto exibido.
2. Tentar criar um placar com teto menor que o alvo e conferir que a mensagem específica da regra continua aparecendo.
3. Forçar um 422 por linha de comando (`curl`) e inspecionar o corpo da resposta.
4. `uv run pytest tests/test_blindagem_e_confiabilidade.py -k 422` e `npm --prefix web test`.

## Out of Scope

- Destaque do campo culpado no formulário a partir da lista `erros`. O contrato já entrega os dados (`campo`, `rotulo`), mas o realce visual pertence ao trabalho de design da `CV2.DS3`.
- Internacionalização: as frases são em português, como todo o produto.
- Normalização de erros 5xx, que continuam com a mensagem genérica de falha de conexão.

## Notes

O código `US2` foi escolhido em vez de uma Technical Story porque o que muda é observável por quem usa: a diferença entre `"[object Object]"` e `"Apelido deve ter no máximo 30 caractere(s)."` está na tela, não na arquitetura.

A normalização acontece nas **duas** pontas de propósito. O backend passa a emitir um formato estável, e o frontend continua sabendo lidar com formatos antigos ou inesperados — um cliente em cache antigo, um proxy que devolve outro corpo ou um endpoint futuro que esqueça o handler não voltam a produzir `"[object Object]"` na tela.
