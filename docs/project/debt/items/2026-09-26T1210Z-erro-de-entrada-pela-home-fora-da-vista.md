---
id: debt-erro-de-entrada-pela-home-fora-da-vista
status: Carried
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
