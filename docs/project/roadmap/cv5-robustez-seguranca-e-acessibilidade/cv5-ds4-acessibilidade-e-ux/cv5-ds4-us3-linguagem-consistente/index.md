---
code: CV5.DS4.US3
level: User Story
status: Validated
status_reason: automode aprovado pelo Navigator em 2026-09-27; testes automatizados verdes
human_validation: pending
updated: 2026-09-27
---

# CV5.DS4.US3 — Linguagem e estados consistentes

## Scope
- Um vocabulário de conexão no web, igual ao do relógio: Conectado / Reconectando… / Sem conexão (`SalaQuadra.svelte:474,533,551`).
- "Enviando o toque…" com token de cor legível no Modo Sol (`Placar.svelte` ~472).
- Texto de vitória único nos dois placares (`Placar.svelte:407`, `PlacarManual.svelte:57`).
- Selo de papel legível: "Admin", "No controle", "Espectador", ≥ 0,8rem (`SalaQuadra.svelte:486`).
- Apelido numa única chave de `localStorage` (`HomePlacar.svelte:8`, `ModalEntrar.svelte:11`).

## Acceptance
Em nenhuma tela aparecem dois estados de conexão diferentes ao mesmo tempo; o apelido digitado na Home aparece pré-preenchido ao entrar por link.

## Plano

[plan.md](plan.md) — branch `feature/cv5-ds4-us3-linguagem-consistente`.

## Revisão (Passo 5)

- **Feito:** `lib/preferencias.js` (`lerApelido` com migração, `guardarApelido`, `nomeDoPapel`); chip "Reconectando…" e banner "Reconectando… Os controles do placar voltam sozinhos."; "{nome} venceu!" nos dois placares e no anúncio; selo legível em 0,8rem; `.aviso-envio` com `var(--acento-info)`.
- **Textos aprovados pelo Navigator:** "{nome} venceu!" e "Controlador".
- **Testes:** `svelte-check` sem erros nem avisos, testes `node --test` (5 novos em `preferencias.test.js`, 1 ajustado em `controle.test.js`) e build verdes. O e2e `superficies.spec.js` foi ajustado para "Equipe A venceu", mas não rodou nesta sessão.
- **Débito novo:** nenhum.
- **Validação humana pendente:** derrubar a rede e ver o chip e o banner com "Reconectando…"; ver "Enviando o toque…" no Modo Sol sob luz forte; digitar o apelido na Home, abrir um link de sala em aba nova e ver o apelido preenchido; conferir o selo "Controlador".
