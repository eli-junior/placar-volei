---
id: lobby-publico-e-pin-como-identificador
status: Decided
raised: 2026-09-27
decided: 2026-09-27
deciders:
  - Eli (Navigator)
  - Claude Opus 5.5 (Driver)
related:
  - CV5.DS1.TS1
---

# Lobby Público e PIN como Identificador

## Question

A revisão de 2026-09-27 apontou que `GET /api/quadras` lista todas as salas com o código de 5 dígitos, então qualquer pessoa entra em qualquer sala. O PIN deve ser um segredo?

## Decision

- O lobby da Home continua público: é a forma de entrar com um toque na quadra (CV2/CV4).
- O PIN **identifica** a sala, não a protege. Entrar dá só o papel de Espectador; marcar pontos exige a promoção pelo Admin, e o controle continua protegido pela `controle_versao` e pelos papéis.
- O que precisa ser segredo continua sendo: `codigo_mestre`, `OWNER_SECRET`, sessões e tokens do relógio.
- Os limites de tentativa passam a usar o IP real (`CF-Connecting-IP`, com `TRUST_CLOUDFLARE`), nunca `X-Forwarded-For`.

## Consequences

- Um estranho pode assistir a uma pelada. Aceito: o placar não tem dado sensível além de apelidos.
- Salas privadas (fora do lobby) ficam como possibilidade futura, se o uso pedir.
