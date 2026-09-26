---
id: debt-erro-de-entrada-pela-home-fora-da-vista
status: Paid
kind: usability
severity: medium
source: relato do Navigator em 2026-09-26
revisit_trigger: próxima mexida na Home, ou novo relato de "Entrar não funciona"
closure_condition: a recusa ao entrar pelo card da quadra ativa aparece junto do campo de apelido, na aba Acompanhar, com o código preenchido
---

# Erro de Entrada pela Home Fora da Vista

## Description

O card da quadra ativa na Home entra com o apelido salvo no aparelho. Se esse apelido já está em uso na quadra, o servidor responde 409 (`apelido_em_uso`). A mensagem aparece no topo da Home, longe do card, e parece que o botão **Entrar** não faz nada.

## Carrying Reason

O Navigator pediu para anotar e priorizar a `CV3.DS2.US3`. O contorno é trocar o apelido na aba **Acompanhar**.

## Proposed Fix

Na recusa pelo card: abrir a aba **Acompanhar** com o código preenchido, colocar o foco no apelido e mostrar o erro ao lado do campo. Patch, com teste de componente. A branch `fix/entrar-na-quadra-pela-home` existe só com o registro no changelog.

## Closure Evidence

Pago por `CV4.DS1.US1` na branch `codex/cv4-ds1-us1-home`. Selecionar uma quadra abre a aba **Acompanhar** e preenche o código antes da chamada de entrada. Se a API recusa a entrada, a mensagem permanece junto ao formulário e o foco volta ao campo de apelido. O teste `home-placar.test.js` cobre ordem, visibilidade local e recuperação do foco; o Navigator aprovou a Home em 2026-09-26.
