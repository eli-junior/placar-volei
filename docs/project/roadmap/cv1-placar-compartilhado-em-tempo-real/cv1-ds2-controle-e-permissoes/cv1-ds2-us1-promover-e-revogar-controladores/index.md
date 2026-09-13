---
code: CV1.DS2.US1
level: User Story
status: Planned
status_reason:
updated: 2026-09-13
related:
  - 2026-09-13T1405Z-identidade-por-apelido-e-sessao
---

# CV1.DS2.US1 — Admin promove e revoga controladores

## Intent

O dono da quadra escolhe quem mais pode mexer no placar, e desfaz essa escolha quando quiser.

## Scope

Painel de participantes visível ao admin, ação de promover espectador a controlador e de revogar, evento `PAPEL_ALTERADO`, aplicação da permissão no backend e reflexo imediato na tela de quem foi promovido ou rebaixado.

## Acceptance / Done Condition

Given uma quadra com um admin e dois espectadores
When o admin promove um dos espectadores a controlador
Then aquele participante passa a ver os botões de ponto e desfazer, sem recarregar a página
And o outro espectador continua sem eles
And uma tentativa de pontuar vinda de espectador é rejeitada pelo backend, mesmo se forjada fora da UI
And ao revogar, os botões desaparecem imediatamente para o ex-controlador.

## Validation Route

Três navegadores. Promover, conferir a UI dos três, tentar chamar a rota de ponto direto pelo cliente do espectador e confirmar rejeição. Revogar e conferir de novo.

## Out of Scope

Sucessão automática (US2), takeover (US3).

## Notes

Permissão é validada no servidor. Esconder botão é conveniência de UI, nunca o controle de acesso.
