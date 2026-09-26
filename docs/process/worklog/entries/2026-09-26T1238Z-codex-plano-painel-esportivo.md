---
date: 2026-09-26T12:38:00Z
author: Codex (Driver), sessão 01a0dd8e-b3b3-7482-a278-5f22f9738d3e
kind: milestone
related:
  - CV4
verification:
  - 59 links relativos válidos no pacote do plano
  - seis histórias Planned e duas referências com JavaScript sintaticamente válido
---

# Plano do painel esportivo preparado para retomada

## What changed

Criado o [CV4](../../../project/roadmap/cv4-painel-esportivo/index.md), com seis entregas, esforço de 1 a 10 por entrega e tarefa, diagnóstico técnico, dependências, critérios de aceite e pontos de pausa. Inclui plano detalhado, roteiro de validação, handoff, decisão visual e cópias documentais das prévias.

Branch `codex/plano-cv4-painel-esportivo`, baseada em `origin/master` em `ab2cedb`. Checkout separado para preservar a pasta que estava na história do relógio.

## Why it matters

O Navigator pediu continuidade por outro agente antes de implementar. A direção visual está aprovada: painel esportivo, pontos prioritários, Teko 600 maior e temas claro/escuro. A autorização de implementação segue pendente do Checkpoint 1.

## Verification

Validação estrutural dos arquivos: 59 links relativos resolvidos, seis índices de história e sintaxe JavaScript de duas referências conferidos. A análise leu o código atual; não executou testes da aplicação nem validação física. Nenhum arquivo de implementação foi alterado.

## Follow-up

Revisar o plano com o Navigator e autorizar E1 (Home). Conferir a correção concorrente `fix/entrar-na-quadra-pela-home` antes de modificar o fluxo de entrada. Tratar a diferença documental entre release 0.11.0 e versões web/backend 0.10.1 na coerência da próxima entrega. Manter cada US/TS em branch própria e preservar checkpoints completos.
