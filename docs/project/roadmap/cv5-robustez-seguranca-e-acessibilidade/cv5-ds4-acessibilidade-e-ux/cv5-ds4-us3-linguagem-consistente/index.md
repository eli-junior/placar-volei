---
code: CV5.DS4.US3
level: User Story
status: Active
status_reason: Checkpoint 1 (plano) aguardando o Navigator
updated: 2026-09-27
---

# CV5.DS4.US3 — Linguagem e estados consistentes

## Scope
- Um vocabulário de conexão no web, igual ao do relógio: Conectado / Reconectando… / Sem conexão (`SalaQuadra.svelte:474,533,551`).
- "Enviando o toque…" com token de cor legível no Modo Sol (`Placar.svelte` ~472).
- Texto de vitória único nos dois placares (`Placar.svelte:407`, `PlacarManual.svelte:57`).
- Selo de papel legível: "Admin", "No controle", "Espectador", ≥ 0,8rem (`SalaQuadra.svelte:486`).
- Apelido numa única chave de `localStorage` (`HomePlacar.svelte:8`, `ModalEntrar.svelte:11`).

## Acceptance
Em nenhuma tela aparecem dois estados de conexão diferentes ao mesmo tempo; o apelido digitado na Home aparece pré-preenchido ao entrar por link.

## Plano

[plan.md](plan.md) — branch `feature/cv5-ds4-us3-linguagem-consistente`.
