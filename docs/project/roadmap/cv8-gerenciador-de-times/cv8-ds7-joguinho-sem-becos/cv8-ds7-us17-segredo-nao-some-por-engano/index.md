---
code: CV8.DS7.US17
level: User Story
status: Done
status_reason: validada pelo Navigator em 2026-10-08 (0.46.4); registro em recusa-do-segredo-e-bloqueio-sem-apagar
updated: 2026-10-08
---

# Segredo do dono não some por engano

## Intent

**Como** dono, **quero** que o aparelho só esqueça o segredo quando ele foi mesmo recusado, **para** não ter que redigitá-lo depois de um erro qualquer.

## Causa confirmada no código

O relatório do QA (P5) atribuiu a perda ao 429; no código, o 429 não apaga nada. O que apaga é **qualquer 404**: `Sessao.svelte` e `Jogadores.svelte` chamam `sair()` em todo 404, e o servidor usa 404 tanto para "segredo errado" (`api.py::validar_segredo_owner`, mascarado) quanto para erros de domínio ("jogador não encontrado").

## Acceptance

- **Dado** o segredo certo salvo **quando** uma ação recebe um 404 de domínio (com `erros[].campo`) **então** o segredo continua salvo e o erro aparece no lugar.
- **Dado** um bloqueio por tentativas (429) **então** o segredo continua salvo e a tela diz quanto falta (`Retry-After`).
- **Dado** uma requisição **sem** o cabeçalho de segredo **então** ela não conta como tentativa errada no bloqueio por IP.
- **Dado** o segredo errado **então** o aparelho o esquece, como hoje.

## Design a decidir no plano

Distinguir a recusa do segredo pelo corpo (404 sem `erros`), ou por um sinal próprio sem revelar o endpoint a quem não tem segredo.
