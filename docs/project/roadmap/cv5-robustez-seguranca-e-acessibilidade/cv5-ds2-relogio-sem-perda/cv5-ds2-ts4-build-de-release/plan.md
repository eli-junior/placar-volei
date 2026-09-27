# Plano — CV5.DS2.TS4 Build de release

- **Nível:** Technical Story · **Branch:** `feature/cv5-ds2-ts4-build-de-release` · **Versão:** patch (APK)

## Scope
1. `buildTypes.release` com `isMinifyEnabled = true`, `isShrinkResources = true` e `proguard-rules.pro` (regras de OkHttp, org.json e Health Services).
2. `signingConfigs.release` lendo keystore e senhas de `~/.gradle/gradle.properties` (fora do repo). Sem keystore configurado, o build de release falha com mensagem clara.
3. Trocar `guava` por `androidx.concurrent:concurrent-futures-ktx` (`await()` no `unregisterMeasureCallbackAsync`).
4. Subir `compileSdk`/`targetSdk` para 36 e pedir a permissão por versão: `READ_HEART_RATE` em API ≥ 36, `BODY_SENSORS` antes (`HeartRate.kt:36,76`).
5. `development-guide.md`: comando de build de release e onde fica a keystore.

## Correção da revisão
`local.properties` e `*.log` já estão no `.gitignore`: nada a fazer.

## Acceptance
- Então `./gradlew assembleRelease` gera um APK assinado menor que o de debug atual (anotar os tamanhos).
- Dado o Galaxy Watch 8 (Wear OS 6), quando abro o placar pela primeira vez, então o pedido de permissão é o de frequência cardíaca e o batimento aparece.
- E pareamento, pontos, desfazer e batimento funcionam no APK de release (R8 não removeu nada usado por reflexão).

## Risks / Navigator
- **Precisa do Navigator:** criar a keystore de release e guardar as senhas fora do repo.
- Subir para targetSdk 36 pode trazer mudanças de comportamento (edge-to-edge, predictive back). Roteiro físico completo obrigatório.

## Validation
Build de debug e release, 44 testes JVM, lint; roteiro físico completo no relógio com o APK de release.
