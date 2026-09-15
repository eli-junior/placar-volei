# Plano de Implementação — CV2.DS1.US2: Erros de validação compreensíveis

## 1. Contexto e Intenção

O FastAPI devolve `RequestValidationError` como HTTP 422 com `detail` sendo uma **lista de dicionários**:

```json
{"detail": [{"type": "string_too_long", "loc": ["body", "apelido"], "msg": "String should have at most 30 characters", "ctx": {"max_length": 30}}]}
```

`App.svelte` fazia `throw new Error(data.detail || '...')`. Com um array de objetos, o JavaScript converte para string e o usuário lê `"[object Object]"` — ou, no melhor caso, um texto em inglês com `loc` incompreensível.

## 2. Nível no Roadmap e Branch

- **Nível**: User Story (`CV2.DS1.US2`).
- **Branch**: `worktree-agent-a5cb003370b910540`.

## 3. Escopo

### 3.1 Backend — formato estável (`app/api.py` + `app/main.py`)

`normalizar_erros_validacao(erros)` devolve:

```json
{
  "detail": "Apelido deve ter no máximo 30 caractere(s). Pontuação-alvo deve ser no mínimo 1.",
  "erros": [
    {"campo": "apelido", "rotulo": "Apelido", "mensagem": "deve ter no máximo 30 caractere(s)", "tipo": "string_too_long"},
    {"campo": "alvo", "rotulo": "Pontuação-alvo", "mensagem": "deve ser no mínimo 1", "tipo": "greater_than_equal"}
  ]
}
```

- `_MENSAGENS_VALIDACAO` traduz os tipos de erro do Pydantic (`missing`, `string_too_long`, `greater_than_equal`, `int_parsing`, …) usando o `ctx` para citar o limite real.
- `_ROTULOS_CAMPOS` dá nome humano aos campos que o usuário digita (`alvo` → "Pontuação-alvo").
- Tipo desconhecido cai no `msg` original do Pydantic: degrada para inglês, nunca para objeto.
- `_nome_do_campo` descarta os prefixos `body`/`query`/`path`/`header` do `loc`.
- O handler em `app/main.py` registra a requisição inválida com `logger.info`, sem corpo — o log ganha rastro do 422 sem virar superfície de vazamento.

### 3.2 Frontend — rede de segurança (`web/src/sync.js`)

`mensagemDeErro(dados, alternativa)` é deliberadamente tolerante:

- `detail` string → devolve a string;
- `detail` lista → concatena os itens legíveis;
- `detail` objeto → tenta `rotulo`/`campo` + `mensagem`/`msg`/`detail`/`message`, ou o `loc` sem `body`;
- nada aproveitável → devolve a `alternativa` específica da ação.

Aplicada nas três chamadas de `App.svelte` (criar placar, entrar na sala, executar comando).

## 4. Decisões de Design

- **`detail` continua sendo string, sempre.** Poderia virar um objeto rico, mas `detail` é o campo que todo cliente existente já lê. Mantê-lo como frase é o que garante que nenhum consumidor volte a renderizar objeto; o detalhamento vai em `erros`, um campo novo e opcional.
- **Duas pontas normalizando.** Redundância de propósito: o backend garante a qualidade da mensagem, o frontend garante que nenhuma resposta fora do padrão quebre a tela. Uma coisa é o contrato, a outra é a defesa.
- **Sem tradução automática genérica.** As frases foram escritas à mão por tipo de erro em vez de traduzidas por biblioteca: são poucas, o vocabulário do produto é específico ("Pontuação-alvo", "Teto da vantagem") e uma tradução literal do Pydantic diria "String" e "Field" para quem só quer marcar ponto.
- **Erros de regra de negócio não passam pelo tradutor.** Os `HTTPException(422, "O teto da vantagem não pode ser menor que a pontuação-alvo.")` já eram frases boas e continuam intactos; o handler só intercepta `RequestValidationError`. Um teste fixa esse limite.

## 5. O que está Fora de Escopo

- Realce do campo culpado no formulário (o dado já está em `erros`; o visual pertence à `CV2.DS3`).
- Internacionalização.
- Normalização de 5xx.

## 6. Intenção de Versão

- **Minor** dentro da `CV2.DS1`: acrescenta o campo `erros` ao contrato de erro e muda o texto exibido ao usuário.
