---
code: CV5.DS2.TS4
level: Technical Story
status: Active
status_reason: Checkpoint 1 (plano) aguardando o Navigator
updated: 2026-09-27
---

# CV5.DS2.TS4 — Build de release

## Scope
`buildTypes.release` com R8 e `shrinkResources`, `signingConfig`, trocar o Guava inteiro por `concurrent-futures` ou `await`. Ignorar `local.properties` e `replay_pid*.log` no git.

## Acceptance
APK de release assinado, menor que o atual, com as mesmas funções.

## Plano

[plan.md](plan.md) — branch `feature/cv5-ds2-ts4-build-de-release`.
