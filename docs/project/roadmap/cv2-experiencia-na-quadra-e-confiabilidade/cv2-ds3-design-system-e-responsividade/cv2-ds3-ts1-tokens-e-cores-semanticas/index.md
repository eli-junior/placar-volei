---
code: CV2.DS3.TS1
level: Technical Story
status: Active
status_reason: tokens implementados e verificados; aguarda validação do Navigator
updated: 2026-09-15
related:
  - CV2.DS2.US4
  - CV2.DS3.US1
  - CV2.DS3.US2
  - CV2.DS3.US4
  - CV2.DS3.US5
  - docs/product/design-tokens.md
---

# CV2.DS3.TS1 — Consolidação de Tokens e Desacoplamento Semântico de Cores

## Intent

Dar ao produto um vocabulário visual único e nomeado por papel, para que uma decisão de aparência seja tomada uma vez no sistema e não quarenta vezes espalhadas pelos componentes.

Dois problemas concretos motivam a história. O primeiro é dispersão: cada componente escolheu seu próprio tamanho de fonte, seu próprio raio e sua própria sombra, e o resultado é uma hierarquia que não se sustenta entre telas. O segundo é ambiguidade semântica: ciano e laranja identificam os Times A e B no placar e, ao mesmo tempo, pintam botões de criar sala, pílulas selecionadas, caixas de seleção e o anel de foco dos campos. Quem está na beira da quadra não consegue usar a cor como sinal de time, porque a mesma cor também quer dizer "clique aqui".

## Scope

- **Inventário auditável** dos valores visuais em uso hoje em `web/src/App.svelte`, `web/src/components/*.svelte` e `web/src/app.css`, com contagem real registrada no `plan.md`.
- **Escala tipográfica de 8 degraus**, nomeada por papel (`--texto-micro` a `--texto-display`), mais um degrau derivado fluido (`--texto-placar`) para os dígitos do placar.
- **4 raios** (`--raio-justo`, `--raio-padrao`, `--raio-amplo`, `--raio-circular`).
- **3 sombras** (`--sombra-sutil`, `--sombra-elevada`, `--sombra-realce`), sendo a terceira parametrizada por `--brilho-cor` para que o brilho de identidade deixe de existir como catorze valores literais distintos.
- **Desacoplamento semântico de cores**: ciano e laranja passam a ser propriedade exclusiva de `--time-a` e `--time-b`. Ação, estado e foco do sistema ganham tokens próprios em neutros e no amarelo de marca (`--acao-primaria`, `--acao-secundaria`, `--acao-destrutiva`, `--estado-*`, `--foco-*`).
- **Anel de foco global** em `:focus-visible`, cobrindo todo elemento interativo, com contraste medido sobre o fundo escuro.
- **Aliases legados** (`--accent-orange`, `--accent-cyan`, `--radius-md`, ...) preservados apontando para os tokens novos, resolvendo exatamente para os mesmos valores.
- **Tema "Modo Sol"** definido em tokens no seletor `:root[data-tema="sol"]`, pronto para ser acionado pela `CV2.DS2.US4`.

## Acceptance / Done Condition

Given a folha `web/src/app.css` consolidada
When o frontend é construído com `npm run build`
Then todo alias legado resolve exatamente para o valor que tinha antes desta história
And nenhuma regra de componente do CSS gerado muda em relação ao build anterior
And `npm run check` termina com 0 erros e 0 avisos
And existe exatamente uma escala tipográfica de 8 degraus, 4 raios e 3 sombras publicados como token
And ciano e laranja aparecem apenas sob `--time-a` e `--time-b`, nunca sob token de ação, estado ou foco
And a navegação por teclado revela um anel de foco visível em todo elemento interativo
And trocar o atributo `data-tema` para `sol` no `<html>` reconfigura fundo, texto, times, marca, gradientes e sombras sem tocar em nenhum componente.

## Validation Route

Detalhada em `test-guide.md`. Em resumo:

1. `cd web && npm run check && npm run build` — 0 erros, build concluído.
2. Comparação regra a regra do CSS gerado antes e depois: apenas as regras originárias de `app.css` mudam de forma, e todas resolvem para o mesmo valor computado.
3. Navegação da Home até a sala usando apenas `Tab` / `Shift+Tab` / `Enter` / `Espaço`, confirmando o anel de foco amarelo em todo elemento alcançável.
4. Acionamento manual do Modo Sol via console (`document.documentElement.dataset.tema = 'sol'`) para inspecionar os tokens do tema claro, sem que isso faça parte do produto entregue.

## Out of Scope

- **Aplicação dos tokens nos componentes `.svelte`.** Nenhum arquivo `.svelte` é alterado nesta história. A lista completa dos ajustes necessários está na seção 7 do `plan.md` e pertence à onda seguinte (`CV2.DS3.US1`, `US2`, `US4` e `US5`).
- **Acionamento do Modo Sol pela interface** (interruptor, persistência da preferência, `prefers-color-scheme`): pertence à `CV2.DS2.US4`.
- **Remoção dos aliases legados.** Eles só saem quando o último componente parar de consumi-los.
- **Correção de overflow, container queries e alvos de toque** (`CV2.DS3.US1`, `US4`, `US5`).

## Notes

- A história é uma Technical Story: não há comportamento novo para o torcedor. O que ela entrega é a condição para que `CV2.DS2.US4`, `CV2.DS3.US1`, `US2`, `US4` e `US5` sejam baratas em vez de caras.
- A restrição dura desta onda foi **não alterar a aparência**. Por isso alguns tokens nascem com o valor legado mesmo quando o valor legado é justamente o problema — é o caso de `--papel-admin-*`, que ainda carrega o laranja do Time B num badge de sistema. O token existe para que a troca da onda seguinte seja de uma linha; a troca em si está registrada no `plan.md`.
- Pelo mesmo motivo, `color-scheme: dark` **não** foi declarado no `:root`: ele mudaria o desenho nativo de barra de rolagem e de caixa de seleção.
- O item de débito citado no escopo original da DS3 (`docs/project/debt/items/2026-09-15T2215Z-tokens-visuais-dispersos-e-cores-de-time-acopladas.md`) **não existe no repositório** — o único item presente em `docs/project/debt/items/` é o de endpoints legados de arenas. A criação ou atualização do item de débito correspondente fica para o Navigator, já que arquivos do Ledger não são de propriedade desta história nesta onda de trabalho paralelo.
