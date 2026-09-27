# Plano — CV5.DS5.TS1 Tipagem, módulos e testes do web

- **Nível:** Technical Story · **Branch:** `feature/cv5-ds5-ts1-tipagem-e-modulos` · **Versão:** sem versão (sem mudança visível)

## Scope
1. `web/jsconfig.json` com `checkJs: true`; typedefs JSDoc para `Snapshot`, `Quadra`, `Participante`, `EstadoPartida` em `lib/tipos.js`. Corrigir o que o `svelte-check` apontar.
2. `lib/tema.js` (`lerTema`, `aplicarTema`) chamado em `main.js` antes do mount: acaba o flash e a duplicação entre `SalaQuadra.svelte:49-87` e `HomePlacar.svelte:9,34-49`.
3. `$effect` com timers devolvem `clearTimeout` (`LinhaDoTempo.svelte:32`, `SalaQuadra.svelte:191,412`, `ModalCompartilhar.svelte:54,62`).
4. `lib/conexao.js`: `conectarWebSocket` e a fila de comandos saem do `App.svelte`, com testes `node --test` usando WebSocket falso (reconexão, socket antigo, vigia da DS3).
5. `SalaQuadra.svelte` (956 linhas): extrair preferências (giro, inversão, wake lock, tela cheia) para `lib/preferencias.js` e a imersão para um componente; os nove callbacks do `App` viram um objeto `acoes`.

## Acceptance
- `svelte-check` com `checkJs` sem erros nem avisos.
- Testes de `lib/conexao.js` cobrindo reconexão e descarte de mensagens de socket antigo.
- Nenhuma mudança visível: e2e existente passa igual.

## Ordem de execução
Depois da `CV5.DS3.US1` e da `CV5.DS4.US3`, que mexem nos mesmos arquivos (evita conflito). Pode ser dividida em duas branches (1–3 e 4–5) se ficar grande.

## Out of Scope
Migrar para TypeScript (`lang="ts"`).

## Validation
`npm run check && npm test && npm run build` e e2e (Node do Windows).
