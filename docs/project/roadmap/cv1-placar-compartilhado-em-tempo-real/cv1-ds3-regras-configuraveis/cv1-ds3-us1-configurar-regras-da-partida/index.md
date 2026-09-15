---
code: CV1.DS3.US1
level: User Story
status: Done
status_reason: implementada, testada e validada pelo Navigator
updated: 2026-09-15
related:
  - CV1.DS1.US4
---

# CV1.DS3.US1 — Configurar pontuação-alvo, vantagem e teto

## Intent

Definir as regras da pelada (pontuação-alvo, vantagem e teto) no momento de criação da sala, de forma rápida e intuitiva.

## Scope

Formulário de criação de placar na tela inicial com seleção de pontuação-alvo (padrão 12, com atalhos 12, 15, 21, 25 e campo livre), interruptor de vantagem de 2 pontos (liga/desliga) e teto opcional da vantagem; validação de valores (`alvo >= 1`, `teto >= alvo`); persistência no evento `PARTIDA_INICIADA`; exibição das regras ativas no cabeçalho do placar e preservação automática das regras ao reiniciar partidas na mesma sala.

## Acceptance / Done Condition

Given a tela inicial "Criar Placar"
When o criador define a pontuação-alvo para 15 com vantagem de 2 e teto 18
Then a sala é criada com as regras configuradas e exibidas com destaque no cabeçalho
And a partida encerra no momento em que a condição configurada for atingida (15 com 2 de vantagem ou teto 18)
And quando a vantagem for desmarcada, a partida encerra no momento em que qualquer equipe atingir o alvo
And uma tentativa de criar sala com teto menor que a pontuação-alvo é rejeitada com mensagem clara no cliente e no servidor
And ao iniciar nova partida na mesma sala, as regras configuradas são preservadas.

## Validation Route

1. Criar sala com alvo 15 e sem vantagem: marcar 15 × 14 e conferir encerramento imediato.
2. Criar sala com alvo 12, vantagem ligada e teto 15: testar 11 × 11 -> 12 × 11 (não encerra) -> 13 × 11 (encerra por vantagem) e 15 × 14 (encerra por teto).
3. Tentar criar sala com alvo 12 e teto 10: conferir rejeição de formulário e na API.
4. Reiniciar a partida e conferir que as regras originais continuam vigentes.

## Out of Scope

Alteração dinâmica de regras com a partida em andamento (para novas regras, cria-se uma nova sala).

## Notes

Decisão de produto do Navigator em 2026-09-15 (ADR `2026-09-15T1525Z-regras-da-partida-definidas-na-criacao-da-sala.md`): as regras pertencem à sala e são imutáveis durante a sua vida, evitando distrações e disputas à beira da quadra durante o jogo.

