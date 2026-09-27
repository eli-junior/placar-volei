---
code: CV5.DS2.TS4
level: Technical Story
status: Planned
updated: 2026-09-27
---

# CV5.DS2.TS4 — Build de release

## Scope
`buildTypes.release` com R8 e `shrinkResources`, `signingConfig`, trocar o Guava inteiro por `concurrent-futures` ou `await`. Ignorar `local.properties` e `replay_pid*.log` no git.

## Acceptance
APK de release assinado, menor que o atual, com as mesmas funções.
