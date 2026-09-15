---
code: CV1.DS2.US3
level: User Story
status: Deferred
status_reason: Despriorizada pelo Navigator em 2026-09-15; criar uma nova sala resolve conflitos de admin sem necessidade de takeover
updated: 2026-09-15
related:
  - 2026-09-13T1415Z-owner-takeover-por-codigo-mestre
---

# CV1.DS2.US3 — Owner assume a administração por código mestre

## Intent

O operador da instância recupera o controle de qualquer quadra, sem depender da boa vontade de quem está com o posto.

## Scope

Rota de takeover, validação do código de 4 dígitos da quadra, promoção do operador a admin, rebaixamento do admin corrente a controlador e evento `ADMIN_ASSUMIDO` visível a todos.

## Acceptance / Done Condition

Given uma quadra com admin ativo e um código mestre conhecido pelo operador
When o operador informa o código correto na rota de takeover
Then ele passa a admin da quadra
And o admin anterior passa a controlador, com a mudança refletida na tela dele imediatamente
And todos os participantes veem o registro da assunção
And um código incorreto não altera papel algum e conta para o limite de tentativas.

## Validation Route

Dois navegadores. Consultar o código no endpoint de owner, executar o takeover pelo segundo navegador e conferir a troca de papéis nas duas telas e o registro do evento. Repetir com código errado.

## Out of Scope

Takeover silencioso — rejeitado por decisão de produto.

## Notes

A visibilidade do takeover é intencional: o princípio "todos veem a mesma partida" não abre exceção para o operador.
