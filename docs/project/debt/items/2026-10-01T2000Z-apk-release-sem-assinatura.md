---
id: debt-apk-release-sem-assinatura
status: Carried
kind: operation
severity: low
source: CV7.TS1
revisit_trigger: Antes de distribuir um APK de release ou de instalar o app fora da máquina do Navigator
closure_condition: `signingConfigs` lendo a keystore do Navigator por variáveis do Gradle, R8/minify ligado e etapa de APK no CI, com o roteiro físico completo rodado no release
---

# APK de Release sem Assinatura e sem Minify

## Description

`android/app/build.gradle` não tem `signingConfigs` e o tipo `release` está com `minifyEnabled false`. `scripts/build-apk.sh release` produz um APK não assinado. O CI não gera APK. O projeto também carrega recursos e testes de exemplo do template do Capacitor (`com.getcapacitor.myapp`, `drawable-v24`, `splash.png`).

## Carrying Reason

Só o APK de debug foi usado, instalado pelo Navigator via `adb`. A keystore fica só com o Navigator e a TS1 a deixou fora do escopo.

## Notes

O relógio passará a usar o mesmo `applicationId` e a mesma assinatura (CV7.TS3), então a assinatura precisa existir antes disso.
