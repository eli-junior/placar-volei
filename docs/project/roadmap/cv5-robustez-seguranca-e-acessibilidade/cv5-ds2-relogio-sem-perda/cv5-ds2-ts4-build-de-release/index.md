---
code: CV5.DS2.TS4
level: Technical Story
status: Done
status_reason: aceito pelo Navigator em 2026-09-27 (teste conjunto da integracao/cv5)
human_validation: accepted
updated: 2026-09-27
---

# CV5.DS2.TS4 — Build de release

## Scope
`buildTypes.release` com R8 e `shrinkResources`, `signingConfig`, trocar o Guava inteiro por `concurrent-futures` ou `await`. Ignorar `local.properties` e `replay_pid*.log` no git.

## Acceptance
APK de release assinado, menor que o atual, com as mesmas funções.

## Plano

[plan.md](plan.md) — branch `feature/cv5-ds2-ts4-build-de-release`.

## Revisão (Passo 5)

- **Feito:** `buildTypes.release` com R8 e `shrinkResources` (26,6 MB → 3,4 MB), `proguard-rules.pro`, `signingConfigs.release` lido de `~/.gradle/gradle.properties`, `compileSdk`/`targetSdk` 36, permissão de batimento por versão (`heartPermission`, com teste) e `BODY_SENSORS` com `maxSdkVersion="35"`.
- **Não feito, com motivo:** trocar o Guava. O Health Services depende dele em runtime (`listenablefuture` resolve para a versão vazia), então a troca não encolhia o APK.
- **Testes:** testes JVM (1 novo), `assembleDebug`, `assembleRelease` e lint verdes (12 avisos, sem erros).
- **Precisa do Navigator:** criar a keystore (comando no `wear/README.md`). Sem ela, o release sai sem assinatura.
- **Risco:** o R8 pode remover algo usado por reflexão. O APK de release precisa do roteiro físico completo: pareamento, pontos, desfazer, batimento e fila offline.
- **Validação humana pendente:** o roteiro acima com o APK de release no Galaxy Watch 8. O primeiro pedido de permissão deve ser o de frequência cardíaca.
