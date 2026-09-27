# Plano — CV5.DS4.US2 Web acessível

- **Nível:** User Story · **Branch:** `feature/cv5-ds4-us2-web-acessivel` · **Versão:** patch

## Correção da revisão
Já existe `prefers-reduced-motion` em `Placar.svelte:596`, `SalaQuadra.svelte:771`, `ModalCelebracaoVitoria.svelte:114` e outros. O trabalho é auditar as animações **infinitas** que escapam desses blocos, não criar do zero.

## Scope
1. Auditar `animation: … infinite` em todos os componentes; o que faltar entra num bloco global em `app.css` (`@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-iteration-count: 1 !important; animation-duration: .01ms !important; } }`).
2. `SalaQuadra.svelte:540`: o `.controle-painel aria-live` fica sempre montado; só o conteúdo é condicional. O `aria-live` sai da `.faixa-posse` (`:478`) e vai para `.posse-texto`.
3. `LinhaDoTempo.svelte:48` migra para `<Dialogo>` (foco preso, retorno de foco, fundo inerte).
4. `ModalEntrar.svelte`: erro com `role="alert"`, input com `aria-invalid` e `aria-describedby`.
5. `Placar.svelte`: `aria-busy` só no botão que originou o envio (guardar `origem` do comando); `aria-label` do botão de próxima partida removido (o texto visível basta, WCAG 2.5.3).
6. `.btn-desfazer` com `min-height: 48px` em todas as alturas de tela.
7. Bolinha `status-dot` com `aria-hidden="true"` (o texto ao lado já informa).

## Acceptance
- Dado o NVDA/TalkBack numa sala, quando derrubo a rede, então "Sem conexão — reconectando" é anunciado.
- Dado movimento reduzido, então nenhum elemento pulsa ou gira sem parar.
- Dada a Linha do Tempo aberta, quando aperto Tab, então o foco não sai do diálogo; ao fechar, volta ao botão que abriu.
- Dado um apelido inválido no modal, então o erro é lido.

## Out of Scope
Textos e vocabulário (`CV5.DS4.US3`).

## Validation
`npm run check && npm test && npm run build` (Node do Windows); axe DevTools nas telas de sala e Home; roteiro com leitor de tela; e2e existente.
