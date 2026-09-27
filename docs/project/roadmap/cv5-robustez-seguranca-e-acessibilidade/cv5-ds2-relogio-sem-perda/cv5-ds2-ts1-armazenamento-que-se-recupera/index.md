---
code: CV5.DS2.TS1
level: Technical Story
status: Active
status_reason: Checkpoint 1 (plano) aguardando o Navigator
updated: 2026-09-27
---

# CV5.DS2.TS1 — Armazenamento que se recupera

## Scope
- `CredentialStore.read()` com `runCatching`: chave inválida apaga o vínculo e pede novo pareamento (`CredentialStore.kt:20`).
- Fila corrompida vira `.corrupt` com aviso na tela, em vez de fila vazia (`CommandQueue.kt:67`).
- Token em memória no `CredentialStore`, invalidado ao salvar ou promover (`WatchModel.kt:208,414`).
- WebSocket não abre com `Bearer null` (`WatchModel.kt:381`).

## Acceptance
- Dado um arquivo de fila corrompido, quando o app abre, então avisa que há lances ilegíveis e não finge fila vazia.
- Dada uma chave do Keystore invalidada, então o app abre na tela de pareamento, sem crash.

## Plano

[plan.md](plan.md) — branch `feature/cv5-ds2-ts1-armazenamento-que-se-recupera`.
