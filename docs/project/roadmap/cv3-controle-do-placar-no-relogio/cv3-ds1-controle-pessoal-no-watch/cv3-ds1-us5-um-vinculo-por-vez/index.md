---
code: CV3.DS1.US5
level: User Story
status: Planned
status_reason: Pedido do Navigator no Checkpoint 1 da US3 (2026-09-23); vem depois da US3, antes ou junto da US4
updated: 2026-09-23
related:
  - CV3.DS1.US3
  - CV3.DS1.US4
---

# CV3.DS1.US5 — Um vínculo por vez: retomar ou trocar de quadra

## Intent
Como Eli, quero reabrir o app do relógio e escolher entre voltar à quadra em que estou vinculado ou gerar um novo código, sem que o relógio continue preso a uma quadra antiga.

## Scope
- Ao abrir o app com vínculo válido: "Retornar à quadra XXXXX" ou "Gerar novo código". Sem vínculo válido (sala expirada, revogação): só "Gerar código".
- O relógio fica vinculado a uma quadra por vez. O pedido de código novo informa o vínculo que substitui; **ao aprovar** o código novo, o servidor revoga o antigo: o "Eli (Relógio)" sai da sala anterior e o controle volta ao dono (mesmo caminho da revogação pelo telefone).
- Gerar um código e desistir mantém o vínculo atual.

## Acceptance / Done Condition
- Dado o relógio vinculado à quadra A com a sala ativa, quando reabrir o app, então vê "Retornar à quadra A" e "Gerar novo código".
- Quando aprovar um código novo na quadra B, então a quadra A deixa de listar "Eli (Relógio)", o controle de A volta ao dono, e o token antigo recebe 401.
- Dado um código novo gerado e não aprovado, então o vínculo com A continua valendo.
- Com lances pendentes da quadra A, "Gerar novo código" avisa quantos lances serão abandonados e pede confirmação; nada é descartado em silêncio.

## Validation Route
Watch real, dois telefones em duas salas. Vincular em A, passar o controle, gerar e aprovar código em B; conferir A (sem relógio, controle com o dono) e B (relógio presente). Repetir desistindo do código: continua em A.

## Out of Scope
Vários relógios por pessoa, relógio para outras pessoas, configuração de servidor no aparelho (removida na US3).

## Notes
- A remoção do campo de servidor da tela de vínculo foi feita na [US3](../cv3-ds1-us3-desfazer/plan.md).
- Hoje (0.8.0), a exclusividade é só por dono na mesma sala; um código aprovado em outra sala deixa o vínculo antigo ativo.
