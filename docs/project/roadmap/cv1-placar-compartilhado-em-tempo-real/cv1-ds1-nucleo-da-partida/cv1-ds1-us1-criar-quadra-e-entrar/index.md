---
code: CV1.DS1.US1
level: User Story
status: Done
status_reason: implementado e validado com Arenas, Quadras, Svelte 5 e presença WebSocket
updated: 2026-09-13
related:
  - 2026-09-13T1405Z-identidade-por-apelido-e-sessao
---

# CV1.DS1.US1 — Criar quadra e entrar por apelido

## Intent

Chegar na quadra, abrir o link e estar dentro do jogo em poucos segundos, sem cadastro.

## Scope

Tela inicial com lista de quadras ativas, criação de quadra, tela de registro por apelido, sessão persistida no navegador, lista de presentes na quadra e atribuição de admin ao primeiro participante.

## Acceptance / Done Condition

Given nenhuma quadra ativa no sistema
When um usuário cria uma quadra e informa seu apelido
Then ele entra na quadra como admin
And a quadra passa a aparecer na lista da tela inicial para os demais
And um segundo usuário que escolhe essa quadra e informa seu apelido entra como espectador
And ambos aparecem na lista de presentes
And recarregar a página devolve cada um à quadra com o mesmo apelido e o mesmo papel, sem novo registro.

## Validation Route

Dois navegadores (um deles anônimo). Criar quadra no primeiro, entrar pelo segundo, conferir lista de presentes nos dois, recarregar ambos e confirmar que os papéis se mantêm.

## Out of Scope

Encerrar ou excluir quadra, expiração de quadra inativa, unicidade global de apelido.

## Notes

Registro é obrigatório também para espectador — ninguém entra anônimo.
