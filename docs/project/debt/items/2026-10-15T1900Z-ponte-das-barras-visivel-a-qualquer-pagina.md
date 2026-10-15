---
id: debt-ponte-das-barras-visivel-a-qualquer-pagina
status: Carried
kind: architecture
severity: low
source: CV6.DS1.US10
revisit_trigger: O WebView passar a abrir outro host além do servidor, ou a ponte ganhar uma ação além de esconder e mostrar as barras
closure_condition: Ponte restrita à origem do servidor (por exemplo, `WebViewCompat.addWebMessageListener` com a origem permitida) ou validação do host antes de agir
---

# Ponte das Barras Visível a Qualquer Página

## Description

`window.PlacarBarras` (`addJavascriptInterface`) é exposta a toda página que o WebView carregar, não só à do servidor. Quem a chamar só consegue esconder ou mostrar as barras do Android.

## Carrying Reason

Só o host do servidor passa por `allowNavigation` (os demais links abrem no navegador do sistema) e o pior efeito é estético. Restringir por origem exigiria o listener de mensagens do WebView, sem como verificar de fora neste release.

## Notes

Decisão: `docs/project/decisions/records/2026-10-15T1900Z-barras-do-sistema-e-cache-do-index.md`.
