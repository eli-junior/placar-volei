---
status: Decided
raised: 2026-09-13
decided: 2026-09-13
deciders:
  - Navigator
supersedes:
related:
  - CV1.DS2
---

# Owner takeover por código mestre de 4 dígitos

## Question

Como o operador da instância recupera a administração de uma quadra quando fica preso atrás de um admin que não coopera?

## Decision

Cada quadra recebe, na criação, um **código aleatório de 4 dígitos**.

- O operador consulta os códigos num **endpoint de owner** (`/owner/quadras`), autenticado por um segredo longo guardado no `.env`. O endpoint nunca é referenciado na UI.
- Numa rota de takeover, informando o código da quadra, o operador **assume como admin**; o admin corrente é rebaixado a controlador.
- O takeover gera evento `ADMIN_ASSUMIDO`, **visível na linha do tempo** para todos.
- Proteção contra força bruta: máximo 5 tentativas por sessão/IP, seguidas de bloqueio progressivo. Tentativas falhas também são registradas.

## Rationale

4 dígitos são 10.000 combinações — trivialmente quebráveis sem limite de tentativas, e adequados com limite. O Navigator quis um código curto por ser digitável em celular; o rate limit é o que torna a escolha defensável.

O takeover é auditável por decisão de produto: o princípio "todos veem a mesma partida" não abre exceção para o operador. Poder assumir silenciosamente transformaria o placar compartilhado num objeto com dono oculto.

## Options Considered

- **Código derivado de segredo no `.env`** (determinístico por quadra) — rejeitado: vazar um código expõe o esquema de derivação de todos.
- **Código apenas no log do servidor** — rejeitado: exige SSH no Mini PC no meio de uma pelada.
- **Senha mestra global única** — rejeitado: um vazamento vale para todas as quadras, para sempre.
- **Takeover silencioso** — rejeitado por violar princípio de produto.

## Consequences

- O segredo de owner nunca aparece em resposta de API pública, na UI ou em log de aplicação.
- O endpoint de owner exige teste de segurança explícito na rota de validação da story.
- O rate limit precisa de estado persistente ou de janela em memória com comportamento definido após restart.
- O código de 4 dígitos é gerado por fonte criptograficamente segura, não por `random` comum.

## Review Trigger

Se a instância deixar de ser de uso doméstico ou for exposta a um público mais amplo, substituir os 4 dígitos por credencial de owner adequada.
