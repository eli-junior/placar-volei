# Plano de Implementação — CV2.DS3.TS1: Consolidação de Tokens e Desacoplamento Semântico de Cores

## 1. Contexto e Intenção

O produto cresceu por componente. Cada tela decidiu sozinha quanto vale "texto pequeno", quanto vale "canto arredondado" e quanto vale "elevação". O resultado é um sistema visual que existe de fato, mas não existe escrito em lugar nenhum: ele está espalhado em literais dentro de nove arquivos `.svelte`.

Isso cobra dois preços. O primeiro é de manutenção: qualquer decisão de hierarquia tipográfica precisa ser repetida dezenas de vezes e sempre sobra um lugar esquecido. O segundo é de produto, e é o mais caro: **ciano e laranja são, ao mesmo tempo, a identidade dos Times A e B no placar e a cor de ação genérica do sistema**. O botão "Criar Placar" é ciano. A pílula de pontuação selecionada é ciano. A caixa de seleção de vantagem é ciano. O anel de foco do campo de texto é laranja. O badge de admin é laranja. Na beira da quadra, sob sol, a cor deixa de ser sinal de time e vira ruído.

Esta história escreve o sistema visual em um lugar só e devolve ciano e laranja aos times.

## 2. Nível no Roadmap e Branch

- **Nível**: Technical Story (`CV2.DS3.TS1`, dentro da Delivery Story `CV2.DS3 — Sistema Visual, Layouts Fluidos e Acessibilidade WCAG`).
- **Branch**: `worktree-agent-a9ae3437bf57c255d` (worktree dedicada, trabalho paralelo a outro agente na mesma onda).
- **Propriedade de arquivos nesta onda**: esta história altera **apenas** `web/src/app.css` e cria documentação. Nenhum `.svelte`, nenhum arquivo em `app/`, `tests/`, `CHANGELOG.md` ou `docs/project/debt/items/` é tocado — outro agente está editando `Placar.svelte`, `SalaQuadra.svelte`, `App.svelte` e o backend simultaneamente.

## 3. Inventário Real

Extração automatizada sobre `web/src/**/*.svelte` e `web/src/app.css`, contando declarações CSS distintas (`font-size`, `border-radius`, `box-shadow`, `text-shadow`).

| Propriedade | Valores distintos antes | Ocorrências antes | Tokens depois |
|---|---|---|---|
| `font-size` | **41** | 126 | **8 degraus** (+1 derivado fluido) |
| `border-radius` | **17** | 72 | **4** |
| `box-shadow` | **32** | 33 | **3** |
| `text-shadow` | 2 | 2 | reaproveitam `--time-a-brilho` / `--time-b-brilho` |
| `filter: drop-shadow()` | 1 | 1 | `--sombra-sutil` |

Confirmação em relação ao relatório de origem da DS3:

- **Fontes**: o relatório citava ~40; a contagem real é **41**. Confere.
- **Raios**: o relatório citava 17; a contagem real é **17**. Confere exatamente.
- **Sombras**: o relatório citava ~20; a contagem real é **32** valores de `box-shadow` distintos (mais 2 `text-shadow` e 1 `drop-shadow`). **A dispersão de sombra é maior do que o relatório supunha** — a diferença vem dos brilhos coloridos, que são catorze variações do mesmo efeito com cor e raio ligeiramente diferentes. É exatamente esse conjunto que `--sombra-realce` parametrizada elimina.

Distribuição de `font-size` por arquivo: `HomePlacar` 34, `Placar` 19, `PlacarManual` 16, `SalaQuadra` 15, `LinhaDoTempo` 14, `ModalEntrar` 9, `ListaPresentes` 7, `ModalCriarQuadra` 6, `CartaoDobravel` 4, `app.css` 2. `App.svelte` não declara nenhum.

## 4. De-Para — Escala Tipográfica

Escala de 8 degraus. Os degraus andam ~1.10 na faixa de texto de interface, onde saltos grandes destroem a hierarquia densa do placar, e ~1.21 na faixa de título e display, onde o salto precisa ser óbvio a três metros da quadra. Os degraus 1 (`0.75rem`) e 4 (`1rem`) coincidem de propósito com os dois únicos tamanhos escritos em `app.css` hoje, para que esta história não mova um pixel sequer.

| # | Token | Valor | Papel | Valores legados absorvidos |
|---|---|---|---|---|
| 1 | `--texto-micro` | `0.75rem` | etiquetas, badges, legendas em caixa alta | `0.6rem`, `0.65rem`, `0.7rem`, `0.72rem`, `0.74rem`, `0.75rem`, `0.76rem`, `0.78rem` |
| 2 | `--texto-legenda` | `0.82rem` | metadados, horários, texto de ajuda | `0.8rem`, `0.82rem`, `0.83rem`, `0.85rem` |
| 3 | `--texto-apoio` | `0.9rem` | texto secundário, rótulo de formulário | `0.875rem`, `0.88rem`, `0.9rem`, `0.92rem`, `0.95rem` |
| 4 | `--texto-corpo` | `1rem` | leitura padrão, campo de entrada, botão | `1rem`, `1.05rem` |
| 5 | `--texto-destaque` | `1.2rem` | ênfase, nome de time, valor em evidência | `1.1rem`, `1.15rem`, `1.2rem`, `1.25rem` |
| 6 | `--texto-titulo` | `1.45rem` | título de seção, cabeçalho de modal | `1.35rem`, `1.4rem`, `1.5rem`, `1.5rem !important` |
| 7 | `--texto-titulo-forte` | `1.75rem` | título de tela, número de apoio | `1.6rem`, `1.7rem`, `1.75rem`, `1.8rem`, `2rem` |
| 8 | `--texto-display` | `2.5rem` | numeral grande de ação (o "+" do ponto) | `2.2rem`, `2.5rem`, `2.75rem` |
| — | `--texto-placar` (derivado) | `clamp(var(--texto-display), 16vw, 8.6rem)` | dígitos do placar | `5rem`, `7.2rem`, `8.6rem`, `var(--cartao-num, 7.2rem)` |

Dois tamanhos permanecem calculados a partir do container, porque é essa a natureza deles. Eles não somem da escala — passam a ancorar piso e teto em degraus:

| Valor legado | Onde | Forma alvo |
|---|---|---|
| `clamp(0.72rem, calc(var(--cartao-w) * 0.075), 1.25rem)` | `PlacarManual.svelte` | `clamp(var(--texto-micro), calc(var(--cartao-w) * 0.075), var(--texto-destaque))` |
| `calc(var(--divisor-w) * 0.55)` | `PlacarManual.svelte` | permanece (dimensão do divisor, não da tipografia) |

Total conferido: 8 + 4 + 5 + 2 + 4 + 4 + 5 + 3 + 4 + 2 = **41 valores legados**, todos endereçados.

## 5. De-Para — Raios

| Token | Valor | Papel | Valores legados absorvidos |
|---|---|---|---|
| `--raio-justo` | `8px` | detalhes internos, chips, marcadores | `2px`, `4px`, `6px`, `8px`, `var(--radius-sm)` |
| `--raio-padrao` | `14px` | cartões, campos e botões (escolha padrão) | `10px`, `12px`, `14px`, `16px`, `var(--radius-md)` |
| `--raio-amplo` | `20px` | modais, folhas e painéis de tela cheia | `18px`, `var(--radius-lg)`, `var(--radius-lg) var(--radius-lg) 0 0` |
| `--raio-circular` | `9999px` | pílulas, avatares, indicadores redondos | `50%`, `999px`, `9999px` |

Um raio permanece fluido, com piso e teto ancorados:

| Valor legado | Onde | Forma alvo |
|---|---|---|
| `clamp(10px, calc(var(--cartao-w, 148px) * 0.08), 24px)` | `CartaoDobravel.svelte` | `clamp(var(--raio-justo), calc(var(--cartao-w, 148px) * 0.08), var(--raio-amplo))` |

Total conferido: 5 + 5 + 3 + 3 + 1 = **17 valores legados**, todos endereçados.

Os valores `8px`, `14px` e `20px` foram escolhidos deliberadamente iguais aos legados `--radius-sm`, `--radius-md` e `--radius-lg`. Assim os aliases resolvem para o mesmo valor e nenhum componente muda de forma nesta onda. A consequência aceita é que raios de `2px` e `4px` vão engordar para `8px` quando migrados — mudança pequena, visível, e que pertence à onda seguinte.

## 6. De-Para — Sombras

Três papéis. O terceiro é parametrizado: quem o usa declara `--brilho-cor` com a cor da própria identidade (`var(--time-a-brilho)`, `var(--time-b-brilho)`, `var(--marca-tenue)`). É isso que colapsa catorze brilhos literais em um.

| Token | Valor (Modo Noite) | Papel |
|---|---|---|
| `--sombra-sutil` | `0 2px 8px rgba(2, 6, 23, 0.45)` | repouso: cartão, chip, elemento assentado na superfície |
| `--sombra-elevada` | `0 16px 40px rgba(2, 6, 23, 0.6)` | flutuação: modal, folha, barra fixa, cartão erguido |
| `--sombra-realce` | `0 4px 16px var(--brilho-cor)` | identidade: brilho de time ou de marca, desligado no Modo Sol |

| Papel alvo | Valores legados absorvidos |
|---|---|
| `--sombra-sutil` | `0 4px 20px rgba(0,0,0,.25)`; `0 1px 1px rgba(0,0,0,.7)`; `0 2px 6px rgba(0,0,0,.4)`; `0 2px 8px rgba(0,0,0,.4)`; `drop-shadow(0 2px 4px rgba(0,0,0,.3))` |
| `--sombra-elevada` | `0 10px 40px rgba(0,0,0,.5)`; `0 16px 28px rgba(0,0,0,.6)`; `0 8px 24px rgba(0,0,0,.6)`; `0 -8px 36px rgba(0,0,0,.6)`; `0 16px 40px rgba(0,0,0,.7)`; `0 4px 28px rgba(0,0,0,.35)`; `0 16px 40px rgba(0,0,0,.6), inset …`; `0 8px 24px rgba(0,0,0,.6), inset …` |
| `--sombra-realce` com `--brilho-cor: var(--time-a-brilho)` | `0 0 16px rgba(6,182,212,.3)`; `0 4px 14px rgba(6,182,212,.3)`; `0 6px 20px rgba(6,182,212,.45)`; `0 2px 8px rgba(2,132,199,.35)`; `0 2px 8px rgba(2,132,199,.3)`; `0 4px 14px rgba(2,132,199,.4)`; `0 4px 14px rgba(2,132,199,.25)` |
| `--sombra-realce` com `--brilho-cor: var(--time-b-brilho)` | `0 0 16px rgba(249,115,22,.3)`; `0 4px 14px rgba(249,115,22,.3)`; `0 6px 20px rgba(249,115,22,.45)`; `0 4px 20px rgba(249,115,22,.35)`; `0 4px 14px rgba(234,88,12,.45)` |
| `--sombra-realce` com `--brilho-cor: var(--marca-tenue)` | `0 4px 20px rgba(245,158,11,.2)` |
| `--sombra-realce` com `--brilho-cor: var(--estado-sucesso-brilho)` | `0 0 8px rgba(16,185,129,.6)` |
| `--foco-anel` | `0 0 0 2px rgba(56,189,248,.2)`; `0 0 0 2px rgba(249,115,22,.2)` |
| `none` | `0 0 0 rgba(0,0,0,0)` (estado "sem sombra" escrito à mão) |
| Relevo local do componente (não é elevação; permanece no `CartaoDobravel`/`PlacarManual`, mas passa a compor com `--sombra-sutil`) | `0 2px 5px rgba(0,0,0,.6), inset 0 1px 2px rgba(255,255,255,.9), inset 0 -1px 2px rgba(0,0,0,.6)`; `inset 0 2px 4px rgba(0,0,0,.9), 0 1px 1px rgba(255,255,255,.2)`; `inset 0 1px 1px rgba(0,0,0,.7)` |

Total conferido: 4 + 8 + 7 + 5 + 1 + 1 + 2 + 1 + 3 = **32 valores de `box-shadow`**, mais 1 `drop-shadow` e 2 `text-shadow` (os neons do cartão dobrável, que passam a ler `--time-a-brilho` / `--time-b-brilho` para que o Modo Sol os zere).

## 7. De-Para — Cores Semânticas

### 7.1 A regra

**Ciano e laranja pertencem aos times. Ponto.** Qualquer outro uso está errado por construção.

| Token | Modo Noite | Modo Sol | Dono |
|---|---|---|---|
| `--time-a`, `--time-a-forte`, `--time-a-brilho`, `--time-a-tenue` | `#06b6d4`, `#0891b2` | `#0e7490`, `#155e75`, brilho `transparent` | Time A |
| `--time-b`, `--time-b-forte`, `--time-b-brilho`, `--time-b-tenue` | `#f97316`, `#ea580c` | `#c2410c`, `#9a3412`, brilho `transparent` | Time B |
| `--marca`, `--marca-forte`, `--marca-suave`, `--marca-tenue` | `#f59e0b`, `#d97706`, `#fcd34d` | `#b45309`, `#92400e`, `#78350f` | produto (vitória, campeão) |
| `--acao-primaria` / `-ativa` / `-texto` | marca sobre texto quase preto | `#0f172a` sobre branco | sistema |
| `--acao-secundaria` / `-ativa` / `-texto` | `#334155` / `#475569` | `#e2e8f0` / `#cbd5e1` | sistema |
| `--acao-discreta` / `-ativa` / `-texto` | transparente / véu branco 6% | transparente / véu escuro 8% | sistema |
| `--acao-destrutiva` / `-ativa` / `-texto` | `#ef4444` / `#dc2626` | `#b91c1c` / `#991b1b` | sistema |
| `--estado-sucesso`, `--estado-alerta`, `--estado-erro`, `--estado-neutro` | `#10b981`, marca, `#f87171`, texto suave | `#047857`, marca, `#b91c1c` | sistema |
| `--foco-cor`, `--foco-largura`, `--foco-deslocamento`, `--foco-anel` | `#fcd34d`, `3px`, `2px` | `#0f172a` | sistema |

Contraste medido (WCAG, sobre `--fundo-base`):

| Par | Noite | Sol |
|---|---|---|
| `--texto-forte` | 17.06:1 | **21.00:1** |
| `--texto-suave` | 6.96:1 | 14.63:1 |
| `--foco-cor` | 12.38:1 (8.98:1 sobre `--fundo-cartao`) | 17.85:1 |
| `--time-a` | 7.35:1 | 5.36:1 |
| `--time-b` | 6.37:1 | 5.18:1 |
| `--marca` | 8.31:1 | 5.02:1 |

### 7.2 Usos legados a corrigir (onda seguinte)

Cada linha abaixo é uma cor de time sendo usada para dizer algo que não é time.

| Uso legado | Arquivo | Token alvo |
|---|---|---|
| Botão "Criar Placar" e botões primários (`#0284c7`, `#0369a1`) | `HomePlacar.svelte`, `SalaQuadra.svelte`, `PlacarManual.svelte` | `--acao-primaria` |
| Pílula de pontuação selecionada, aba ativa (`#0284c7` / `#38bdf8`) | `HomePlacar.svelte` | `--acao-primaria` / `--acao-secundaria-ativa` |
| `accent-color: #0284c7` da caixa de vantagem | `HomePlacar.svelte` | `--acao-primaria` |
| Anel de foco do campo (`0 0 0 2px rgba(56,189,248,.2)` e `rgba(249,115,22,.2)`) | `HomePlacar.svelte`, `app.css` | `--foco-anel` |
| Borda de item ativo na lista de presentes (`#38bdf8`) | `ListaPresentes.svelte` | `--acao-secundaria-ativa` |
| Destaque de evento na linha do tempo (`#22d3ee`) | `LinhaDoTempo.svelte` | `--estado-neutro` ou `--marca-suave` |
| Botão "Assumir controle" (`#0369a1`) | `SalaQuadra.svelte` | `--acao-primaria` |
| Badge de admin em laranja (`rgba(249,115,22,…)`, `#fb923c`) | `app.css` (`--papel-admin-*`) | `--marca` / `--marca-suave` |
| Badge de controlador em ciano (`#38bdf8`) | `app.css` (`--papel-controlador-*`) | `--acao-secundaria-texto` ou neutro claro |
| `input:focus` com borda laranja | `app.css` | `--foco-cor` via `:focus-visible` |
| `--borda-ativa` em laranja (`rgba(249,115,22,.4)`), usada como borda de elemento selecionado | `app.css`, consumida por `Placar.svelte` e `SalaQuadra.svelte` via `--border-active` | `--acao-secundaria-ativa` ou `--marca-tenue` |
| Botão de marcar ponto do Time A/B (gradiente ciano/laranja) | `Placar.svelte`, `PlacarManual.svelte` | **correto como está** — vira `--gradiente-time-a` / `--gradiente-time-b` |

## 8. Decisões de Design

- **Nomear por papel, não por valor.** `--texto-legenda` sobrevive a uma mudança de escala; `--font-size-13` não. O mesmo vale para `--time-a` contra `--accent-cyan`: o segundo nome é justamente o que autorizou o vazamento da cor do time para o resto do produto.

- **Aliases legados em vez de migração em massa.** Migrar os nove componentes na mesma onda seria uma alteração de milhares de linhas, impossível de revisar e em rota de colisão com o outro agente que edita `Placar.svelte`, `SalaQuadra.svelte` e `App.svelte` agora. Os aliases custam dezoito linhas e tornam a história verificável: se todo alias resolve para o valor antigo, a aparência não pode ter mudado.

- **`--sombra-realce` parametrizada em vez de uma sombra por time.** Um token por time significaria dois; um token por time e por intensidade significaria seis. Parametrizar por `--brilho-cor` mantém três sombras e ainda deixa o Modo Sol desligar o efeito inteiro num único lugar (`--sombra-realce: none`).

- **O foco é do sistema, não do time.** Usar laranja no anel de foco confundia "este campo está ativo" com "isto é do Time B". O anel passa para `#fcd34d`, o amarelo de marca, a 12.38:1 sobre o fundo escuro.

- **`:focus-visible` e não `:focus`.** `app.css` zera o `outline` de todo botão. Sem anel, quem navega por teclado fica cego. Com `:focus` o anel apareceria também no toque e no clique, alterando a aparência atual do produto. `:focus-visible` entrega acessibilidade sem cobrar regressão.

- **Modo Sol como bloco de variáveis e nada mais.** O tema inteiro cabe num seletor. Nenhum componente precisa saber que existe tema claro — inclusive porque os gradientes viraram token e, no Sol, simplesmente resolvem para cor chapada.

- **Alternativa rejeitada: escala geométrica pura.** Uma razão única (por exemplo 1.125 em todos os degraus) daria uma tabela mais bonita e uma hierarquia pior: o produto precisa de degraus curtos entre `0.75rem` e `1rem`, onde mora quase toda a interface, e de degraus largos acima de `1.45rem`, onde mora o placar. A razão é dupla de propósito, e isso está escrito no `app.css`.

- **Alternativa rejeitada: `--font-size-xs/sm/md/lg`.** Nomes de camiseta descrevem tamanho relativo, não papel, e por isso não resolvem a pergunta "qual eu uso aqui?". Seis meses depois existem `lg`, `xl` e `2xl` e a dispersão volta com outro nome.

## 9. Ajustes de Componente Adiados para a Onda Seguinte

Nenhum arquivo `.svelte` foi tocado. A lista abaixo é o trabalho que consome o que esta história publicou, para ser distribuído entre `CV2.DS3.US1`, `US2`, `US4`, `US5` e `CV2.DS2.US4`.

**Tipografia (126 declarações em 9 arquivos)**

1. `HomePlacar.svelte` — 34 `font-size` literais para degraus da escala. Maior concentração do produto; deve ir junto com o redesenho da Home (`CV2.DS3.US2`).
2. `Placar.svelte` — 19 literais; o `.btn-plus` de `2.2rem` vira `--texto-display` (`2.5rem`, aumento visível e intencional).
3. `PlacarManual.svelte` — 16 literais, incluindo os dois tamanhos fluidos que passam a ancorar piso e teto em degraus.
4. `SalaQuadra.svelte` — 15 literais.
5. `LinhaDoTempo.svelte` — 14 literais.
6. `ModalEntrar.svelte` — 9; `ListaPresentes.svelte` — 7; `ModalCriarQuadra.svelte` — 6; `CartaoDobravel.svelte` — 4 (estes últimos passam a usar `--texto-placar`).

**Raios**

7. Substituir `2px`, `4px`, `6px`, `8px` por `--raio-justo` (`HomePlacar`, `LinhaDoTempo`, `PlacarManual`, `SalaQuadra`, `ListaPresentes`). Detalhes de `2px` e `4px` ficam visivelmente mais arredondados — é a mudança aceita da consolidação.
8. Substituir `10px`, `12px`, `14px`, `16px` por `--raio-padrao` (`HomePlacar`, `CartaoDobravel`, `SalaQuadra`).
9. Substituir `18px` por `--raio-amplo` (`PlacarManual`).
10. Substituir `999px` e `50%` por `--raio-circular` (`CartaoDobravel`, `LinhaDoTempo`, `ListaPresentes`, `Placar`, `PlacarManual`, `SalaQuadra`).
11. Ancorar o `clamp()` de raio do `CartaoDobravel.svelte` nos degraus.

**Sombras**

12. Trocar as 8 sombras pretas de flutuação por `--sombra-elevada` (`ModalCriarQuadra`, `ModalEntrar`, `LinhaDoTempo`, `PlacarManual`, `CartaoDobravel`, `Placar`).
13. Trocar as 4 sombras pretas de repouso por `--sombra-sutil`, e o `drop-shadow` do `PlacarManual`.
14. Trocar os 14 brilhos coloridos por `--sombra-realce` + `--brilho-cor` local (`Placar`, `PlacarManual`, `HomePlacar`, `SalaQuadra`).
15. Trocar os 2 anéis de foco em `box-shadow` por `--foco-anel`.
16. Fazer os 2 `text-shadow` neon do `CartaoDobravel.svelte` lerem `--time-a-brilho` / `--time-b-brilho`, para que o Modo Sol os apague.

**Cores semânticas**

17. Aplicar a tabela da seção 7.2: todo `#0284c7`, `#0369a1`, `#38bdf8`, `#0891b2` e `#22d3ee` fora de contexto de time vira token de ação ou de estado.
18. Trocar os gradientes literais por `--gradiente-time-a`, `--gradiente-time-b`, `--gradiente-marca` e `--gradiente-fundo` (`Placar`, `PlacarManual`, `CartaoDobravel`), condição necessária para o Modo Sol achatá-los.
19. Repontar `--papel-admin-*` para `--marca` e `--papel-controlador-*` para um neutro claro, em `app.css`. É uma mudança de aparência deliberada e por isso não cabia nesta onda.
20. Migrar `input:focus` de `--accent-orange` para `--foco-cor`, em `app.css`, quando a mudança de aparência estiver aprovada.
21. Declarar `color-scheme: dark` no `:root` (e manter `light` no Modo Sol), para que barra de rolagem e controles nativos acompanhem o tema. Deixado de fora porque altera o desenho nativo de caixa de seleção e barra de rolagem.
22. Remover os dezoito aliases legados do `app.css` quando o último componente parar de consumi-los.

**Acionamento do Modo Sol** (`CV2.DS2.US4`, outro agente)

23. Interruptor de tema, persistência da preferência e leitura de `prefers-color-scheme`. Do lado do CSS não falta nada: basta `document.documentElement.dataset.tema = 'sol'`.

## 10. O que está Fora de Escopo

- Alteração de qualquer arquivo `.svelte`, de `app/`, de `tests/`, do `CHANGELOG.md` ou de `docs/project/debt/items/` — propriedade de outro agente nesta onda.
- Correção de overflow horizontal, container queries do placar, alvos de toque de 44×44 e semântica ARIA (`CV2.DS3.US1`, `US4`, `US5`).
- Auditoria automatizada com axe-core (pertence à rota de validação da DS3 como um todo).
- Criação do item de débito no Ledger. O arquivo citado no escopo da DS3 não existe no repositório e o Ledger não é de propriedade desta história.

## 11. Intenção de Versão

**Patch.** A história não muda comportamento nem aparência: publica vocabulário. A versão minor pertence à primeira User Story da DS3 que consumir os tokens e produzir efeito visível.

## 12. Riscos e Ambiguidades

- **Risco de colisão de merge em `app.css`.** Baixo: o outro agente trabalha em `.svelte` e no backend. Se ele tiver adicionado tokens à folha, o merge precisa preservar ambos os blocos.
- **Ambiguidade de produto para o Navigator:** a cor de ação primária do sistema passa a ser o amarelo de marca. Isso resolve o desacoplamento, mas troca a cor do botão mais clicado do produto (hoje ciano) por amarelo. A troca **não acontece nesta história** — acontece quando o item 17 da seção 9 for executado. É uma decisão de produto e está registrada aqui para o Navigator confirmar antes daquela onda.
- **Aceito conscientemente:** ao migrar, raios de `2px`/`4px` engordam para `8px` e o `+` do botão de ponto cresce de `2.2rem` para `2.5rem`. São os dois únicos pontos onde a consolidação cobra um preço visual.
