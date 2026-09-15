# Sistema Visual — Tokens de Design

Referência do vocabulário visual do Placar Vôlei. A fonte da verdade é `web/src/app.css`; este documento existe para explicar **por que** cada token existe e **quando** usá-lo.

Estabelecido pela história `CV2.DS3.TS1`.

## A regra que governa tudo

**Ciano é do Time A. Laranja é do Time B. Nenhuma outra coisa no produto pode usar essas cores.**

O placar é um objeto lido de longe, de pé, com o sol batendo. A cor é o canal mais rápido de identificação de time que existe. Quando o botão de criar sala também é ciano e o badge de admin também é laranja, esse canal deixa de funcionar: a cor passa a significar "time" e "clique aqui" ao mesmo tempo, e o cérebro precisa de um segundo passo — ler — para desempatar. Um segundo passo é caro entre um rally e outro.

Ação, estado e foco do sistema vivem em neutros e no amarelo de marca. Se você está prestes a usar `--time-a` ou `--time-b` em algo que não é um time, existe um token de ação ou de estado para o seu caso.

## Como escolher um token

Pergunte **qual é o papel**, nunca **qual é o tamanho**. Os nomes foram escolhidos para que "qual eu uso aqui?" tenha resposta sem consultar valores. Se nenhum papel serve, a resposta provável não é criar um valor literal — é que o desenho está pedindo um papel que o sistema ainda não tem, e isso é uma conversa, não um `font-size: 0.83rem`.

## Tipografia

Uma família para texto (`--fonte-texto`, Inter) e uma para números de placar (`--fonte-numeros`, Teko).

A escala tem 8 degraus. Ela anda ~1.10 na faixa de interface, onde saltos grandes destroem a hierarquia densa do placar, e ~1.21 na faixa de título e display, onde o salto precisa ser óbvio a três metros da quadra.

| Token | Valor | Use para |
|---|---|---|
| `--texto-micro` | `0.75rem` | etiqueta, badge, legenda em caixa alta |
| `--texto-legenda` | `0.82rem` | metadado, horário, texto de ajuda |
| `--texto-apoio` | `0.9rem` | texto secundário, rótulo de formulário |
| `--texto-corpo` | `1rem` | leitura padrão, campo de entrada, botão |
| `--texto-destaque` | `1.2rem` | ênfase, nome de time, valor em evidência |
| `--texto-titulo` | `1.45rem` | título de seção, cabeçalho de modal |
| `--texto-titulo-forte` | `1.75rem` | título de tela, número de apoio |
| `--texto-display` | `2.5rem` | numeral grande de ação (o "+" do ponto) |

`--texto-placar` (`clamp(var(--texto-display), 16vw, 8.6rem)`) é o degrau 8 esticado, para os dígitos do placar. Não é um nono degrau: é o reconhecimento de que o número principal do produto é fluido por natureza.

Tamanhos derivados de container (`calc()` sobre a largura de um cartão) continuam legítimos, desde que piso e teto do `clamp()` sejam degraus da escala.

## Raios

| Token | Valor | Use para |
|---|---|---|
| `--raio-justo` | `8px` | detalhe interno, chip, marcador |
| `--raio-padrao` | `14px` | cartão, campo, botão — a escolha padrão |
| `--raio-amplo` | `20px` | modal, folha, painel de tela cheia |
| `--raio-circular` | `9999px` | pílula, avatar, indicador redondo |

`--raio-circular` substitui tanto `999px` quanto `50%`: em caixas pequenas o navegador reduz o raio proporcionalmente e desenha o mesmo círculo.

## Sombras

Três papéis, e o terceiro é parametrizado.

| Token | Use para |
|---|---|
| `--sombra-sutil` | repouso: cartão, chip, elemento assentado na superfície |
| `--sombra-elevada` | flutuação: modal, folha, barra fixa, cartão erguido |
| `--sombra-realce` | identidade: o brilho de um time ou da marca |

`--sombra-realce` lê `--brilho-cor`. Quem a usa declara a cor da própria identidade no mesmo bloco:

```css
.botao-ponto-time-a {
  --brilho-cor: var(--time-a-brilho);
  box-shadow: var(--sombra-realce);
}
```

É isso que evita uma sombra nova a cada time, a cada intensidade e a cada estado. E é isso que permite ao Modo Sol desligar todo o efeito neon numa linha.

## Cores

### Times — uso exclusivo

| Token | Papel |
|---|---|
| `--time-a`, `--time-a-forte` | identidade do Time A (ciano) |
| `--time-a-brilho`, `--time-a-tenue` | brilho e véu de fundo do Time A |
| `--time-b`, `--time-b-forte` | identidade do Time B (laranja) |
| `--time-b-brilho`, `--time-b-tenue` | brilho e véu de fundo do Time B |

### Marca

| Token | Papel |
|---|---|
| `--marca`, `--marca-forte`, `--marca-suave`, `--marca-tenue` | vitória, campeão, destaque institucional |

O amarelo de marca é também a cor da ação primária do sistema — justamente para que a ação não precise pedir emprestada a cor de um time.

### Ações do sistema

| Token | Papel |
|---|---|
| `--acao-primaria` / `-ativa` / `-texto` | a ação principal da tela (criar, entrar, confirmar) |
| `--acao-secundaria` / `-ativa` / `-texto` | ação de apoio, seleção, aba ativa |
| `--acao-discreta` / `-ativa` / `-texto` | ação terciária, botão fantasma |
| `--acao-destrutiva` / `-ativa` / `-texto` | encerrar, remover, revogar |

### Estados

`--estado-sucesso` (e `--estado-sucesso-brilho`), `--estado-alerta`, `--estado-erro`, `--estado-neutro`.

### Superfícies e texto

`--fundo-base`, `--fundo-superficie`, `--fundo-cartao`, `--fundo-cartao-ativo`, `--texto-forte`, `--texto-suave`, `--texto-apagado`, `--borda-sutil`, `--borda-ativa`.

### Foco

`--foco-cor`, `--foco-largura`, `--foco-deslocamento` e `--foco-anel` (variante em `box-shadow`, para quando o `outline` é cortado por um pai com `overflow: hidden`).

O anel global está em `app.css` sob `:focus-visible` e cobre todo elemento interativo. `:focus-visible` e não `:focus`: o anel aparece para teclado e navegação assistiva, não para toque nem clique.

### Gradientes

`--gradiente-fundo`, `--gradiente-time-a`, `--gradiente-time-b`, `--gradiente-marca`. São token para que o Modo Sol possa achatá-los em cor chapada sem que nenhum componente precise saber que existe um tema claro.

### Papéis de participante

`--papel-admin-*`, `--papel-controlador-*`, `--papel-espectador-*`, consumidos pelas classes `.badge-*`.

> Estes três ainda carregam as cores legadas — o badge de admin é laranja e o de controlador é ciano, ou seja, cores de time num elemento de sistema. Os tokens existem para que a correção seja de uma linha. A troca está registrada na seção 9 do `plan.md` da `CV2.DS3.TS1` e depende de aprovação de produto, porque altera a aparência.

## Temas

O produto inteiro cabe em dois blocos de variáveis.

- **Modo Noite** — padrão, definido em `:root`.
- **Modo Sol** — alto contraste para luz solar direta, definido em `:root[data-tema="sol"]`. Fundo branco, números pretos a 21:1, gradientes achatados em cor chapada e todo brilho neon desligado (`--sombra-realce: none`). Os times escurecem para manter contraste sobre fundo claro sem perder identidade.

Acionar o tema é escrever `data-tema="sol"` no `<html>`. Nenhum componente participa disso — essa é a prova de que os tokens estão corretos. A interface de acionamento pertence à história `CV2.DS2.US4`.

Contraste medido sobre `--fundo-base`:

| Par | Noite | Sol |
|---|---|---|
| `--texto-forte` | 17.06:1 | 21.00:1 |
| `--texto-suave` | 6.96:1 | 14.63:1 |
| `--foco-cor` | 12.38:1 | 17.85:1 |
| `--time-a` | 7.35:1 | 5.36:1 |
| `--time-b` | 6.37:1 | 5.18:1 |
| `--marca` | 8.31:1 | 5.02:1 |

## Aliases legados

`--accent-orange`, `--accent-cyan`, `--accent-green`, `--bg-*`, `--text-*`, `--border-*`, `--radius-*`, `--font-family`, `--font-display`.

Continuam publicados e resolvem exatamente para os valores que sempre tiveram. Existem por uma razão só: permitir que a consolidação dos tokens entrasse sem reescrever nove componentes de uma vez.

**Não use alias legado em código novo.** Eles saem quando o último componente parar de consumi-los — a migração está listada na seção 9 do `plan.md` da `CV2.DS3.TS1`.
