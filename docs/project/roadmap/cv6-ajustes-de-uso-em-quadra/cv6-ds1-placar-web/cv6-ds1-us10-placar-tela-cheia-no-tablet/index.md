---
code: CV6.DS1.US10
level: User Story
status: Done
status_reason: validado no tablet Galaxy Tab S6 (SM-P620) pelo Navigator em 2026-10-15; entregue na 0.56.0
updated: 2026-10-15
---

# CV6.DS1.US10 — Placar em tela cheia no tablet

## Intent

Quem deixa o tablet de pé na beira da quadra vê o placar maior e sem a interface do Android por cima: o número é a razão de o aparelho estar ali.

## Scope

- No APK, quem só acompanha a partida (espectador) fica sem as barras de status e de navegação do Android. Deslizar a partir da borda as traz por instantes; elas voltam ao controlar a quadra ou sair da sala. Fora do APK nada muda.
- O placar ocupa mais a tela: cabeçalho compacto, margens menores, rodapé flutuante sobre o placar (a dica "Toque na tela para ver opções" some sozinha em 5 s) e o número até a altura toda da linha da equipe, sem cobrir o nome dela.
- A quadra online no APK é a página do servidor, onde o Capacitor não leva a ponte dos plugins; por isso a MainActivity expõe a ponte própria `window.PlacarBarras` (decisão `barras-do-sistema-e-cache-do-index`).
- O `index.html` e os arquivos soltos saem com `Cache-Control: no-cache`: o WebView do APK guardava o index por horas e seguia na versão antiga depois de um deploy.

## Acceptance / Done Condition

Given o tablet em paisagem, no APK, em uma quadra online como espectador
When o app abre a quadra
Then as barras do Android somem e o placar ocupa a tela toda, com o número maior e sem cobrir "EQUIPE A" e "EQUIPE B"
And tocar na tela mostra as opções sem mover os pontos, e depois de 3 s elas somem
And deslizar da borda mostra as barras por instantes, e Voltar à Home as traz de volta

## Validation Route

`web/tests/barras-do-sistema.test.js` (ponte, fila, ligação nativa, CSS), `web/e2e/exibicao-tela-cheia.spec.js` (a caixa do número contra o nome em 5 formatos de tela), `tests/test_review_regressions.py` (`no-cache`). No aparelho: Mini PC com a branch, `logcat` com `BarrasDoSistema esconder`, captura de tela do tablet sem barras; o Navigator validou borda, Voltar e os pontos.

## Out of Scope

Quem controla o placar (as barras continuam); relógio; temas; esconder as barras na Home e nas configurações.
