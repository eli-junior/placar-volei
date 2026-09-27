---
code: CV5.DS5.TS1
level: Technical Story
status: Validated
status_reason: automode aprovado pelo Navigator em 2026-09-27; testes automatizados verdes
human_validation: pending
updated: 2026-09-27
---

# CV5.DS5.TS1 — Tipagem, módulos e testes do web

## Scope
- `jsconfig.json` com `checkJs` e typedefs JSDoc para `Snapshot`, `Quadra`, `Participante`.
- `lib/tema.js` lido antes do mount (acaba o flash de tema e a duplicação entre `SalaQuadra` e `HomePlacar`).
- Timers com limpeza (`LinhaDoTempo.svelte:32`, `SalaQuadra.svelte:191,412`, `ModalCompartilhar.svelte:54,62`).
- Extrair `lib/conexao.js` (WebSocket e fila de comandos) com testes usando WebSocket falso.
- Quebrar `SalaQuadra.svelte` (956 linhas) e trocar os nove callbacks por um objeto `acoes`.

## Acceptance
`svelte-check` com `checkJs` limpo; reconexão e fila cobertas por `node --test`; nenhuma mudança visível.

## Plano

[plan.md](plan.md) — branch `feature/cv5-ds5-ts1-tipagem-e-modulos`.

## Revisão (Passo 5)

- **Feito:**
  - `jsconfig.json` com `// @ts-check` em `sync.js` e `lib/*.js`, e typedefs em `lib/tipos.js`.
  - `lib/tema.js`, aplicado em `main.js` antes do mount.
  - Limpeza de timers em `LinhaDoTempo`, `SalaQuadra` e `ModalCompartilhar`.
  - `lib/conexao.js`, com 7 testes de socket e relógio falsos. O `App.svelte` só trata as mensagens.
- **Bug achado e corrigido:** o QR de `ModalCompartilhar` chamava `gerarQrCode(url, 'M')` e usava `.length` do objeto retornado. O QR não aparecia.
- **Ajuste ao plano:** o `checkJs` global para `.svelte` gera 20 erros de callbacks tipados como `Function`, então ficou só nos módulos de lógica. A divisão da `SalaQuadra` e o objeto `acoes` também ficaram de fora. Os dois estão no débito `debt-sala-quadra-grande-e-props-sem-tipo`.
- **Base:** a branch contém a `integracao/cv5`, porque mexe nos mesmos arquivos da DS3.US1 e da DS4.US3.
- **Testes:** `svelte-check` sem erros nem avisos, testes `node --test` (10 novos, 1 ajustado) e build verdes.
- **Validação humana pendente:** abrir o placar com o Modo Sol salvo e ver que não pisca escuro. Abrir "Compartilhar" e ver o QR aparecer e ser lido pela câmera. A reconexão deve se comportar como na DS3.US1.
