---
code: CV5.DS5.TS1
level: Technical Story
status: Active
status_reason: Checkpoint 1 (plano) aguardando o Navigator
updated: 2026-09-27
---

# CV5.DS5.TS1 — Tipagem, módulos e testes do web

## Scope
- `jsconfig.json` com `checkJs` e typedefs JSDoc para `Snapshot`, `Quadra`, `Participante`.
- `lib/tema.js` lido antes do mount (acaba o flash de tema e a duplicação entre `SalaQuadra` e `HomePlacar`).
- Timers com limpeza (`LinhaDoTempo.svelte:32`, `SalaQuadra.svelte:191,412`, `ModalCompartilhar.svelte:54,62`).
- Extrair `lib/conexao.js` (WebSocket e fila de comandos) com testes usando WebSocket falso.
- Quebrar `SalaQuadra.svelte` (956 linhas) e trocar os nove callbacks por um objeto `acoes`.

## Acceptance
`svelte-check` com `checkJs` limpo; reconexão e fila cobertas por `node --test`; nenhuma mudança visível.

## Plano

[plan.md](plan.md) — branch `feature/cv5-ds5-ts1-tipagem-e-modulos`.
