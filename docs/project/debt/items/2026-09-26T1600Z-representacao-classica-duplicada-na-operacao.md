---
id: debt-representacao-classica-duplicada-na-operacao
status: Carried
kind: maintainability
severity: low
source: CV4.DS2.US3, revisão do Checkpoint 3 em 2026-09-26
revisit_trigger: próxima mudança visual no tema Clássico, ou divergência percebida entre operação e acompanhamento
closure_condition: operação e espectador usam a mesma representação clássica, com os toques de ponto injetados pela composição de operação
---

# Representação Clássica Duplicada na Operação

## Description

No tema **Clássico**, o espectador usa `PlacarClassico.svelte`, enquanto `Placar.svelte` (administrador e controlador) mantém sua própria grade de `CartaoDobravel`. Proporções dos cartões, faixa de nome e cores das equipes estão em dois lugares; um ajuste visual pode chegar a um papel e não ao outro.

## Carrying Reason

Na operação os cartões são alvos de toque, com fila, `aria-busy` e feedback. Mover esse comportamento para a representação pura depois da validação aumentaria o risco da `CV4.DS2.US3` sem ganho visível ao Navigator.

## Proposed Fix

Dar a `PlacarClassico.svelte` um slot ou callbacks opcionais para o toque em cada lado e fazer `Placar.svelte` compor comandos em volta dele, como já faz com `PlacarResultado` no tema Esportivo.
