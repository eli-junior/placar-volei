---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-15
related:
  - CV6.DS1.US10
  - barras-do-sistema-e-cache-do-index
---

# US10: placar em tela cheia no tablet (0.56.0)

- **Pedido:** ver o placar do modo de exibição ocupar mais a tela e esconder o menu do Android (Navigator, 2026-10-15), depois de limpar o tablet de apps sem uso e instalar o APK pelo MCP `dispositivos`.
- **Entrega:** plugin `BarrasDoSistema` e ponte `window.PlacarBarras`, rodapé flutuante, cabeçalho e margens compactos, número até a altura da linha com `text-box`, `Cache-Control: no-cache` no index.
- **Achados no tablet físico (nada disso apareceria só em teste):** o servidor do APK é a página remota, sem a ponte dos plugins do Capacitor (o logcat ficou mudo até o plugin ser chamado pela interface embutida); o WebView guardava o `index.html` por horas; o número a 108cqh cobria o nome da equipe porque a largura do tablet limita a fonte, não a altura.
- **Método:** o app release não expõe DevTools nem o console; o teste de isolamento (chamar o plugin ao abrir a interface embutida, sem commitar) separou "nativo funciona" de "a página remota não chega nele".
- **Testes:** pytest 690, web 213, e2e do espectador, acessibilidade e sequência (21) e o novo `exibicao-tela-cheia` (5 formatos), `svelte-check` e `ruff` limpos. `casca.spec` falha também na master (dívida nova).
- **Dívida:** `ponte-das-barras-visivel-a-qualquer-pagina` e `casca-spec-falha-na-master` (novas).
- **Validação:** Navigator no Galaxy Tab S6 (SM-P620), com o Mini PC na branch: barras, número, toque, borda e Voltar, 2026-10-15.
