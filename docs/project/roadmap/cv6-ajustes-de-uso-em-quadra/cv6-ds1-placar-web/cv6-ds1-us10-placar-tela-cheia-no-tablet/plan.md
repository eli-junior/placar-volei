# Plano — CV6.DS1.US10

- **Branch:** `feature/placar-tela-cheia-tablet` (versão 0.56.0, `versionCode` 44).
- **Escopo:** plugin nativo `BarrasDoSistema`, rodapé flutuante com a dica que some, cabeçalho e margens compactos, número até 100cqh só com `text-box`.
- **Descoberto no caminho:** a quadra online é a página do servidor e o Capacitor não leva a ponte dos plugins até ela (o plugin nunca era chamado) ➜ ponte própria `window.PlacarBarras`; o WebView guardava o `index.html` por horas ➜ `no-cache`; o número crescia e cobria o nome da equipe (o glifo sobe na caixa de linha) ➜ `text-box: trim-both cap alphabetic` só onde há suporte, medido por e2e.
- **Alternativas rejeitadas:** ampliar o `allowNavigation` do Capacitor para dar a ponte oficial à página remota (não verificável de fora); reduzir o cartão em vez de crescer o dígito.
