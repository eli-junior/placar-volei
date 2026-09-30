---
id: debt-sala-quadra-grande-e-props-sem-tipo
status: Carried
kind: maintainability
severity: low
source: CV5.DS5.TS1
revisit_trigger: Próxima história que mexa em giro, imersão ou tela cheia da sala, ou quando um erro de prop só aparecer em uso
closure_condition: SalaQuadra.svelte abaixo de ~600 linhas (preferências e imersão extraídas), callbacks do App num objeto `acoes` e props tipadas por JSDoc com `checkJs` ligado também para `.svelte`
---

# SalaQuadra Grande e Props sem Tipo

## Description

`SalaQuadra.svelte` tem cerca de 950 linhas: acumula tema, giro, inversão, wake lock, tela cheia, imersão e seis modais. O `App.svelte` repassa nove callbacks por props. Com `checkJs` ligado para `.svelte`, o svelte2tsx tipa cada callback como `Function`, o que gera 20 erros até as props serem tipadas por JSDoc.

## Carrying Reason

A `CV5.DS5.TS1` ligou o `@ts-check` só nos módulos de lógica (`sync.js`, `lib/*.js`) e extraiu tema e conexão. Dividir a sala e tipar as props mexe em quase todos os componentes, sem mudança visível. Fica para quando uma história já for mexer nesses pontos.

## Updates

- 2026-09-30 (CV6.DS1.US9): `SalaQuadra.svelte` ganhou a derivação `sequencia`, repassada a `Placar` e `PlacarManual` como mais uma prop sem tipo. Crescimento pequeno; revisit trigger inalterado.
