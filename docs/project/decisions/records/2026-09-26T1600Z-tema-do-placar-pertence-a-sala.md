---
status: Decided
raised: 2026-09-26
decided: 2026-09-26
deciders:
  - Eli (Navigator)
related:
  - CV4.DS2.US3
---

# Tema do placar pertence à sala

## Decision

O visual do placar (**Esportivo** ou **Clássico**) é uma escolha da sala, feita somente pelo administrador, persistida em `quadras.tema_placar` e entregue a todos os papéis pelo snapshot e broadcast já existentes. Continua válida em novas partidas e reconexões. O padrão é `esportivo`.

Claro/escuro permanece uma preferência local de cada dispositivo e não se mistura com o tema do placar.

## Consequences

- A coluna entra por migração aditiva (`ALTER TABLE`), sem elevar `settings.version`, que recriaria o banco.
- Troca isolada de tema não gera evento de regra nem item na linha do tempo; só atualiza a sala.
- O relógio pode iniciar nova partida como admin, mas não troca o tema.
- Clientes que não recebem o campo caem em `esportivo`.
