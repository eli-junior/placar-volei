---
id: debt-acessibilidade-e-overflow
status: Paying
kind: accessibility
severity: medium
source: CV1.DS1.US1
revisit_trigger: Qualquer ajuste de layout responsivo ou auditoria de acessibilidade
closure_condition: Zero rolagem horizontal de 360px a 1440px, zoom habilitado, alvos de toque de 44x44px e semântica ARIA nos controles compostos
---

# Acessibilidade WCAG 2.2 Pendente e Overflow Horizontal em Mobile e Tablet

## Description

A interface não passa em critérios básicos de WCAG 2.2 e vaza layout em telas pequenas:

- `.equipes-grid` e o cabeçalho da sala produzem rolagem horizontal indesejada em viewports de celular e tablet (`scrollWidth > innerWidth`).
- O zoom está desabilitado via `user-scalable`, o que é falha direta de acessibilidade.
- Alvos de toque abaixo do mínimo de 44×44px.
- Abas e seletores de opção sem semântica ARIA (`role="tab"`, `role="radio"`), e o placar não é anunciado por leitor de tela com o nome dos times.

## Carrying Reason

A `CV1` validou o produto em um conjunto restrito de aparelhos do Navigator. O relatório de Frontend, UX e Design Visual de 2026-09-15 foi a primeira auditoria sistemática de viewports e acessibilidade.

## Revisit Trigger

Qualquer mudança estrutural de layout ou inclusão de novo controle interativo.

## Closure Condition

Auditoria axe-core limpa nas rotas principais, inspeção sem overflow em 360×740, 375×812, 768×1024, 1024×768 e 1440×900, e navegação completa por teclado com foco visível.

## Notes

Pago por `CV2.DS3` (US1 e US5).
