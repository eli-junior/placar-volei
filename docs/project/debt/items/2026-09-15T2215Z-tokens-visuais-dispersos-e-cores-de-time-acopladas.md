---
id: debt-tokens-e-cores-acopladas
status: Paying
kind: design-system
severity: medium
source: CV1.DS1.US5
revisit_trigger: Nova tela ou componente que precise escolher tipografia, raio, sombra ou cor de ação
closure_condition: Escala tipográfica de 8 degraus, 4 raios e 3 sombras tokenizados, com ciano e laranja de uso exclusivo dos Times A e B
---

# Tokens Visuais Dispersos e Cores de Time Reutilizadas em Ações do Sistema

## Description

O CSS acumulou valores ad-hoc ao longo de toda a `CV1`: cerca de 40 tamanhos de fonte distintos, 17 raios de borda e 20 sombras, definidos direto nos componentes em vez de tokens em `web/src/app.css`.

Além do volume, existe um acoplamento semântico: as cores Ciano e Laranja identificam os Times A e B no placar, mas também são usadas em botões genéricos, foco e ações do sistema. O resultado é ambíguo à beira da quadra — um botão ciano de "confirmar" parece pertencer ao Time A.

Não há anel de foco global `:focus-visible`, o que também bloqueia a navegação por teclado.

## Carrying Reason

A `CV1` priorizou provar o fluxo de partida em tempo real. Cada story resolveu seu visual localmente, o que era o custo certo a pagar enquanto o produto ainda estava se definindo.

## Revisit Trigger

Qualquer nova tela, tema alternativo (como o Modo Sol) ou trabalho de acessibilidade.

## Closure Condition

Tokens consolidados em `app/app.css` (tipografia, raios, sombras, cores semânticas neutras e de marca), cores de time restritas ao placar e anel `:focus-visible` global.

## Notes

Pago por `CV2.DS3.TS1`. É pré-requisito do tema "Modo Sol" (`CV2.DS2.US4`).
