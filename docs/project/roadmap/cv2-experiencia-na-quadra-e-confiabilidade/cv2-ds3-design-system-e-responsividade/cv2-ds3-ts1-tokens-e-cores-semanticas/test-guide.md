---
code: CV2.DS3.TS1
kind: test-guide
status: Active
updated: 2026-09-15
---

# Guia de Teste e Validação — CV2.DS3.TS1: Consolidação de Tokens e Desacoplamento Semântico de Cores

Esta é uma Technical Story: não há comportamento novo para o torcedor. O que precisa ser provado é o contrário do usual — **que nada mudou** — mais duas adições verificáveis: o anel de foco de teclado e a existência do tema Sol em tokens.

A história não altera backend nem testes automatizados de Python. `uv run pytest` continua sendo a suíte do projeto e não é afetado por ela.

---

## 1. Verificação Automatizada

Na raiz do projeto:

```bash
# reaproveita as dependências já instaladas (apenas em worktree)
ln -s /home/user/placar-volei/web/node_modules web/node_modules

cd web
npm run check     # svelte-check: 0 erros, 0 avisos
npm run build     # vite build: conclui sem erro
```

Resultado esperado:

```
COMPLETED 10 FILES 0 ERRORS 0 WARNINGS 0 FILES_WITH_PROBLEMS
✓ 129 modules transformed.
```

### 1.1 Prova de não-regressão visual (comparação do CSS gerado)

O argumento de "a aparência não mudou" não é uma opinião: é uma comparação entre o `bundle` de CSS gerado antes e depois da história.

```bash
# 1. gerar o bundle da versão anterior
git stash push -u -m ts1-verificacao -- web/src/app.css
cd web && npm run build && cd ..
cp app/static/assets/index-*.css /tmp/antes.css

# 2. restaurar a história e gerar o bundle novo
git stash list --format='%H %gs'          # localizar a entrada pela etiqueta
git stash apply <sha>                      # nunca usar pop em worktree compartilhada
cd web && npm run build && cd ..
cp app/static/assets/index-*.css /tmp/depois.css
```

Duas asserções sobre esses arquivos:

**A. Nenhuma regra de componente mudou.** Quebrando os dois `bundles` em regras de topo, o resultado é 370 regras antes e 372 depois. **360 regras são idênticas byte a byte** — ou seja, todo o CSS originado de arquivos `.svelte` está intacto. As 10 regras que saíram e as 12 que entraram são exatamente as regras escritas em `app.css`: `:root`, `body`, `input`, `.badge`, `.badge-admin`, `.badge-controlador`, `.badge-espectador`, `.status-dot`, `.status-online`, `.status-offline` — mais as duas adições da história (`:root[data-tema="sol"]` e o bloco `:focus-visible`).

**B. Toda regra reescrita resolve para o mesmo valor computado.** Expandindo os `var()` do novo `:root`:

| Alias legado | Valor antes | Resolvido agora |
|---|---|---|
| `--bg-primary` | `#0f172a` | `#0f172a` |
| `--bg-surface` | `#1e293b` | `#1e293b` |
| `--bg-card` | `#243247` | `#243247` |
| `--bg-card-hover` | `#2d3e58` | `#2d3e58` |
| `--accent-orange` | `#f97316` | `#f97316` |
| `--accent-orange-hover` | `#ea580c` | `#ea580c` |
| `--accent-cyan` | `#06b6d4` | `#06b6d4` |
| `--accent-green` | `#10b981` | `#10b981` |
| `--text-primary` | `#f8fafc` | `#f8fafc` |
| `--text-secondary` | `#94a3b8` | `#94a3b8` |
| `--text-muted` | `#64748b` | `#64748b` |
| `--border-color` | `#ffffff14` | `#ffffff14` |
| `--border-active` | `#f9731666` | `#f9731666` |
| `--radius-sm` / `-md` / `-lg` | `8px` / `14px` / `20px` | `8px` / `14px` / `20px` |
| `--font-family` / `--font-display` | Inter / Teko | Inter / Teko |

E as declarações que passaram a consumir token: `body` (`#0f172a`, `#f8fafc`, Inter), `input` (`#ffffff14`, `#1e293b`, `#f8fafc`, `14px`, `1rem`), `.badge` (`9999px`, `.75rem`), `.badge-admin` (`#f9731626`, `#fb923c`, `#f973164d`), `.badge-controlador` (`#38bdf826`, `#38bdf8`, `#38bdf84d`), `.badge-espectador` (`#94a3b81f`, `#cbd5e1`, `#94a3b840`), `.status-online` (`#10b981`, `#10b98199`), `.status-offline` (`#64748b`) — **todos idênticos aos valores anteriores**.

A única diferença sintática sem diferença de renderização é `.status-dot`, cujo `border-radius: 50%` virou `var(--raio-circular)` (`9999px`): numa caixa de 8×8 px o navegador reduz o raio proporcionalmente e desenha o mesmo círculo.

### 1.2 Contraste dos tokens

Calculado sobre `--fundo-base` de cada tema:

| Par | Modo Noite | Modo Sol |
|---|---|---|
| `--texto-forte` | 17.06:1 | **21.00:1** (preto puro sobre branco puro) |
| `--texto-suave` | 6.96:1 | 14.63:1 |
| `--foco-cor` | 12.38:1 (8.98:1 sobre `--fundo-cartao`) | 17.85:1 |
| `--time-a` | 7.35:1 | 5.36:1 |
| `--time-b` | 6.37:1 | 5.18:1 |
| `--marca` | 8.31:1 | 5.02:1 |

Todos acima de 4.5:1 (AA para texto normal); texto e foco acima de 7:1 (AAA).

---

## 2. Roteiro de Validação do Navigator

### Contexto

Um cliente basta — a história não toca estado compartilhado. Use um navegador de desktop com teclado físico.

### Passo 1 — Subir a aplicação

```bash
cd web && npm run build && cd ..
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Acesse `http://localhost:8000`.

### Passo 2 — Conferir que nada mudou

Percorra Home, criação de sala, sala e placar.

- **O que observar**: a interface está **exatamente** igual à de antes da história. Mesmas cores, mesmos tamanhos, mesmos cantos, mesmas sombras. O botão de criar placar continua ciano, o badge de admin continua laranja, o campo focado por clique continua com borda laranja.
- **Condição de aprovação**: nenhuma diferença perceptível.
- **Condição de falha**: qualquer elemento com cor, tamanho, canto ou sombra diferente do anterior.

Se houver dúvida em algum ponto, compare com uma captura de tela anterior à história ou repita a comparação de CSS da seção 1.1.

### Passo 3 — Anel de foco por teclado (a única adição visível)

Na Home, clique uma vez numa área vazia e então navegue **apenas com o teclado**: `Tab`, `Shift+Tab`, `Enter`, `Espaço`. Entre numa sala e continue navegando por todos os controles.

- **O que observar**: cada elemento alcançado — campo de PIN, botões, pílulas de pontuação, caixa de vantagem, cartões da lista, botões de ponto, desfazer — recebe um **contorno amarelo de 3 px, com 2 px de folga**, nitidamente visível sobre o fundo escuro.
- **O que observar também**: usando o **mouse**, clicar nos mesmos botões **não** desenha o contorno. O anel é de teclado, por `:focus-visible`.
- **Condição de aprovação**: nenhum elemento interativo é alcançado por `Tab` sem contorno visível, e clicar com o mouse não produz contorno.
- **Condição de falha**: qualquer elemento focável sem anel (é exatamente o buraco de acessibilidade que a história fecha), anel invisível contra o fundo, ou anel aparecendo ao clicar.

### Passo 4 — Modo Sol em tokens (inspeção, não entrega)

O Modo Sol **não tem interruptor** nesta história — quem o entrega é a `CV2.DS2.US4`. O que se valida aqui é que o CSS já está pronto para ela.

No console do navegador (F12):

```js
document.documentElement.dataset.tema = 'sol';
```

- **O que observar**: o fundo da página fica branco e o texto preto imediatamente, **sem recarregar e sem nenhuma alteração de componente**. Boa parte dos componentes continuará escura, porque eles ainda escrevem cor literal em vez de token — isso é esperado e é precisamente o trabalho listado na seção 9 do `plan.md`.
- **Condição de aprovação**: `body` e os elementos que já consomem token (fundo, texto, campos, badges, indicador de conexão) invertem para o tema claro; o anel de foco passa de amarelo para quase preto, continuando visível.
- **Condição de falha**: nada muda ao trocar o atributo, ou algum token do tema claro fica ilegível.

Para voltar:

```js
delete document.documentElement.dataset.tema;
```

### Passo 5 — Movimento reduzido

Com `prefers-reduced-motion` ativo no sistema operacional, repita o Passo 3.

- **Condição de aprovação**: o anel de foco continua aparecendo (ele não depende de animação) e nenhuma transição nova foi introduzida.

---

## 3. Critérios de Sucesso

**Condição de passagem**

- `npm run check` com 0 erros e 0 avisos; `npm run build` concluído.
- 360 das 370 regras do CSS gerado idênticas byte a byte; as demais são as de `app.css`, todas resolvendo para o mesmo valor computado.
- Aparência do produto indistinguível da anterior em todas as telas.
- Todo elemento interativo alcançado por `Tab` exibe anel de foco amarelo; o mouse não o exibe.
- `data-tema="sol"` reconfigura o tema sem tocar em componente.
- `--time-a` e `--time-b` são os únicos tokens que carregam ciano e laranja; nenhum token de ação, estado ou foco os referencia.

**Condição de falha**

- Qualquer diferença visual perceptível em relação ao estado anterior.
- Qualquer alias legado resolvendo para valor diferente do original.
- Elemento focável sem anel de foco, ou anel com contraste insuficiente.
- Token de ação, estado ou foco apontando para cor de time.
- Alteração em arquivo `.svelte`, em `app/`, em `tests/`, no `CHANGELOG.md` ou em `docs/project/debt/items/` — esta história não é proprietária desses arquivos nesta onda.
