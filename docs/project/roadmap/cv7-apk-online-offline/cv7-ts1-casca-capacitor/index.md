---
code: CV7.TS1
level: Technical Story
status: Validated
status_reason: APK de debug validado pelo Navigator no Galaxy Z Fold (SM-F956B) em 2026-10-01
updated: 2026-10-01
---

# CV7.TS1 — Casca Capacitor do APK

## Intent

Gerar o APK Android `br.com.placarvolei` a partir da web atual e abrir com ele a quadra online do servidor, sem comportamento novo de placar.

## Scope

- Capacitor 8 em `web/` (`capacitor.config.ts`), projeto Android em `android/`; os estáticos embarcados saem de `app/static` e não são versionados.
- Interface embarcada (`https://localhost`) abre a tela inicial do app (`InicioApp.svelte`): o servidor é fixo, vem de `PLACAR_SERVIDOR` no build e não é editável; HTTP só para rede local.
- A tela testa `GET /health` (5 s, `no-cors`) e só libera "Abrir quadras online" se a rede chegar ao servidor; senão mostra "Servidor indisponível" e "Testar de novo".
- "Abrir quadras online" navega o WebView para o servidor (host em `allowNavigation`); lá roda o app de sempre, com cookies e WebSocket na mesma origem.
- Ícone do launcher (quadrado, redondo e adaptativo) gerado da bola do `favicon.svg` sobre `#0f172a`.
- `scripts/build-apk.sh [debug|release]`; instalar com `adb install -r --user 0` (sem `--user 0`, o Samsung duplica o app no perfil Dual App).

## Acceptance / Done Condition

Given o APK instalado e o servidor no ar
When abro o app e toco em Abrir quadras online
Then a home das quadras abre dentro do app (não no navegador do sistema)
And crio uma quadra, marco pontos e outro celular no navegador vê o mesmo placar
And o relógio vinculado a essa quadra continua funcionando como hoje

## Validation Route

`web/tests/casca.test.js`, `web/e2e/casca.spec.js` (Capacitor simulado, axe nos dois temas, servidor fixo, servidor fora do ar); o e2e compila a web com `--mode e2e` (`web/.env.e2e`). Build e uso no aparelho validados pelo Navigator.

## Out of Scope

Quadra local (CV7.US1); ponte com o relógio (CV7.TS3); splash próprio; keystore e assinatura de release.

## Known Limits

O teste de conexão só prova que a rede chegou ao servidor: qualquer resposta HTTP (inclusive 502 do túnel) conta como disponível. Ver `debt-apk-teste-de-conexao-so-detecta-rede`.
