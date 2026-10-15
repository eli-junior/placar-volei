---
status: Accepted
date: 2026-10-15
related:
  - CV6.DS1.US10
---

# Barras do Android pela ponte própria e `index.html` sem cache

## Contexto

O Navigator quis o placar do espectador em tela cheia no tablet. No APK a quadra online é a página do servidor aberta no WebView (`allowNavigation`), não a interface embutida. Duas surpresas no tablet físico: (1) o plugin Capacitor `BarrasDoSistema` nunca era chamado pela página do servidor (o logcat não registrava nada; o mesmo plugin chamado pela interface embutida escondia as barras); (2) mesmo com o servidor atualizado, o WebView mostrava a versão antiga por horas, porque o `index.html` saía sem `Cache-Control` (só `Last-Modified`) e o WebView o guardava por heurística.

## Decisão (Navigator, 2026-10-15: "como você propôs")

- **Ponte própria `window.PlacarBarras`**, exposta pela `MainActivity` com `addJavascriptInterface`, só com `esconder()` e `mostrar()`. O JS usa a ponte quando ela existe e o plugin Capacitor quando não (interface embutida). Os pedidos entram numa fila e o app reaplica o último ao ganhar o foco da janela.
- **`Cache-Control: no-cache`** no `index.html` e nos arquivos soltos servidos por `serve_spa`. `/assets` (nome com hash) continua em cache.
- **Número maior só com `text-box: trim-both cap alphabetic`** (`@supports`); sem suporte vale o tamanho antigo.

## Alternativas rejeitadas

- **Dar a ponte oficial do Capacitor à página remota** (origens permitidas): não se verifica de fora (o app release não expõe DevTools nem o console) e depende da versão do Capacitor.
- **Esconder as barras pelo lado nativo ao detectar a URL:** a troca de tela no servidor é `pushState`, sem recarga de página.
- **Crescer o dígito sem aparar a caixa:** o glifo sobe dentro da caixa de linha e cobriu o nome da equipe no tablet (largura maior que a altura).

## Consequências

Qualquer página aberta no WebView enxerga `window.PlacarBarras`; hoje só o servidor passa por `allowNavigation`, e o efeito possível é mostrar ou esconder as barras (débito `ponte-das-barras-visivel-a-qualquer-pagina`). Deploys futuros chegam ao APK sem esperar o cache. Pedir uma ação nativa à página do servidor segue este padrão (ponte própria), não um plugin Capacitor.
