---
code: CV5.DS4.US2
level: User Story
status: Active
status_reason: Checkpoint 1 (plano) aguardando o Navigator
updated: 2026-09-27
---

# CV5.DS4.US2 — Web acessível

## Scope
- `@media (prefers-reduced-motion)` global em `app.css` para pulsos e giro.
- Regiões `aria-live` sempre montadas; o live da posse só em `.posse-texto` (`SalaQuadra.svelte:478,540`).
- Linha do Tempo migra para `Dialogo` (`LinhaDoTempo.svelte:48`).
- Erro do modal de apelido com `role="alert"` e `aria-describedby` (`ModalEntrar.svelte:71`).
- `aria-busy` só no botão que enviou; `aria-label` da próxima partida igual ao texto visível (`Placar.svelte:245,419`).
- Desfazer com pelo menos 48px em telas baixas (`Placar.svelte:692`).

## Acceptance
Com leitor de tela, a queda de conexão é anunciada; com movimento reduzido, nada pulsa; o foco não escapa da Linha do Tempo.

## Plano

[plan.md](plan.md) — branch `feature/cv5-ds4-us2-web-acessivel`.
