---
code: CV7.TS1
level: Technical Story
status: In Progress
status_reason: implementada; aguardando build e validação do Navigator no aparelho
updated: 2026-10-01
---

# CV7.TS1 — Casca Capacitor do APK

## Intent

Gerar o APK Android `br.com.placarvolei` a partir da web atual e abrir com ele a quadra online do servidor, sem comportamento novo de placar.

## Scope

- Capacitor 8 em `web/` (`capacitor.config.ts`), projeto Android em `android/`; os estáticos embarcados saem de `app/static` e não são versionados.
- Interface embarcada (`https://localhost`) abre a tela inicial do app (`InicioApp.svelte`): servidor lembrado no aparelho, padrão vindo de `PLACAR_SERVIDOR` no build; HTTP só para rede local.
- "Abrir quadras online" navega o WebView para o servidor (host em `allowNavigation`); lá roda o app de sempre, com cookies e WebSocket na mesma origem.
- `scripts/build-apk.sh [debug|release]`.

## Acceptance / Done Condition

Given o APK instalado e o servidor no ar
When abro o app e toco em Abrir quadras online
Then a home das quadras abre dentro do app (não no navegador do sistema)
And crio uma quadra, marco pontos e outro celular no navegador vê o mesmo placar
And o relógio vinculado a essa quadra continua funcionando como hoje

## Validation Route

`web/tests/casca.test.js`, `web/e2e/casca.spec.js` (Capacitor simulado, axe nos dois temas); build e uso no aparelho pelo Navigator.

## Out of Scope

Quadra local (CV7.US1); ponte com o relógio (CV7.TS3); ícone e splash próprios; keystore de release.
