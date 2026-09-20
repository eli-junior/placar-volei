---
id: cores-de-tema-como-token-e-veu-como-canal-de-cor
status: Decided
date: 2026-09-20
source: fix/modo-sol-placar
supersedes: none
---

# Cor de Tema Vive em Token, e o Véu É um Canal de Cor

## Context

O Modo Sol foi entregue na `0.5.0` trocando apenas o bloco de variáveis de `:root[data-tema="sol"]`. Isso pressupõe que todo componente consome cor por token. A premissa não era verdadeira: os componentes ainda continham cerca de 130 cores literais. O resultado visível é que ativar o Modo Sol clareava o fundo enquanto o placar permanecia preto.

Duas famílias de literais causavam a maior parte do problema:

1. Cores de objeto — os cartões do placar, com gradiente escuro fixo e numeral claro.
2. Sobreposições — 44 ocorrências de `rgba(255, 255, 255, x)` usadas como fundo de botão, borda e realce, com 17 opacidades diferentes.

## Decision

**Nenhum componente declara cor literal.** Toda cor de superfície, texto, borda, sombra ou realce vem de token definido em `web/src/app.css`. A exceção é a cor que pertence ao objeto representado, não ao tema: o brilho do anel metálico do cartão e o fundo branco obrigatório do QR code. Essas exceções levam comentário explicando o motivo.

**O véu é publicado como canal de cor, não como escala de opacidade.** `--veu` guarda apenas os três componentes RGB (`255, 255, 255` no tema escuro; `15, 23, 42` no Modo Sol) e cada componente escreve a própria opacidade:

```css
background: rgba(var(--veu), 0.08);
```

## Rationale

A alternativa considerada foi publicar uma escala fechada de véus (`--veu-fraco`, `--veu-medio`, `--veu-forte`). Ela é mais canônica em sistemas de design e força consistência, mas exigiria reclassificar 17 opacidades distintas em 3 ou 4 degraus. Isso mudaria a aparência do tema escuro atual, que é a tela em produção e que esta correção não podia alterar.

O canal de cor preserva cada opacidade existente exatamente, então o tema escuro ficou intacto: das 388 regras de cor do CSS construído, 381 saíram idênticas após resolver as variáveis, e as 7 restantes são consolidações deliberadas de tons quase iguais.

A escala fechada continua sendo o destino desejável. Ela pode ser construída em cima de `--veu` depois, quando houver espaço para ajustar a aparência do tema escuro.

## Consequences

- Um tema novo passa a ser de fato um bloco de variáveis. Nenhum componente precisa saber que ele existe.
- A verificação de paridade de tema fica mecânica: construir o CSS antes e depois, resolver as variáveis e comparar as regras de cor. Essa checagem deve ser repetida por qualquer trabalho que mexa em tokens.
- Cor de objeto físico permanece literal por decisão, não por esquecimento. Quem encontrar uma dessas encontrará também o comentário.
- `--veu` não impede que alguém escolha uma opacidade arbitrária. A consistência aqui depende de revisão, não do token. É o custo aceito para manter o tema escuro intacto.
