---
code: CV5.DS3.US1
level: User Story
status: Planned
updated: 2026-09-27
---

# CV5.DS3.US1 — Placar que não congela

## Scope
- Heartbeat ou timeout de inatividade no WebSocket; reconectar em `visibilitychange` e `online` (`App.svelte:67`).
- Zerar `ultimoSnapshot` no `ESTADO_INICIAL` para aceitar `seq` menor após reinício (`sync.js:14`).
- Ler JSON só com `res.ok` ou com fallback amigável (`App.svelte:137,153,206,232`).
- Mostrar "copiado" só quando a cópia der certo (`SalaQuadra.svelte:188`, `ModalCompartilhar.svelte:51`).

## Acceptance
- Dado um espectador com o celular bloqueado por 5 min, quando desbloqueia, então o placar se atualiza sozinho ou mostra que está reconectando.
- Dado um 502 do túnel, então a mensagem é legível, não "Unexpected token <".
