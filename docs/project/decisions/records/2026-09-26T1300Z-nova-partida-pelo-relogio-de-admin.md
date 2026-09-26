---
id: nova-partida-pelo-relogio-de-admin
status: Decided
raised: 2026-09-26
decided: 2026-09-26
deciders:
  - Eli (Navigator)
  - Claude Opus 5.5 (Driver)
related:
  - CV3.DS2.US3
---

# Nova Partida pelo Relógio de um Administrador

## Question

No site, só ADMIN inicia nova partida. O participante do relógio é espectador com o controle delegado. Quem pode iniciar a nova partida pelo relógio?

## Decision

- O relógio inicia a nova partida se estiver com o controle, na versão vista, e se o dono dele for ADMIN da quadra.
- Reusa o `reiniciar` do site sem parâmetros: mesmos times, jogadores, alvo, vantagem e teto.
- Envio direto, com id idempotente por partida encerrada; não entra na fila offline.
- O evento fica em nome do relógio na linha do tempo.

## Rationale

- O relógio age pelo dono: dar a ele o que o dono já pode no site, sem promover o participante do relógio a ADMIN.
- Na fila offline, os pontos seguintes ficariam presos a uma partida que ainda não existe.

## Options Considered

- Qualquer relógio com o controle: um controlador passaria a iniciar partidas, o que o site não permite.
- Promover o participante do relógio a ADMIN: daria ao relógio poderes de gestão da sala.

## Consequences

- O botão depende de rede. A recusa não mostra aviso no relógio.

## Review Trigger

Se controladores passarem a iniciar partidas no site, ou se o relógio precisar mudar times ou regras.
