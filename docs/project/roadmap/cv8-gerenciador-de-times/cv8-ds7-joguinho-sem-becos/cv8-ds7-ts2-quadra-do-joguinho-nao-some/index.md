---
code: CV8.DS7.TS2
level: Technical Story
status: Done
status_reason: validada pelo Navigator em 2026-10-08 (0.46.3); registro em quadra-da-rodada-renovada-pelo-servidor
updated: 2026-10-08
---

# Quadra do joguinho não some no meio da rodada

## Intent

O banco das quadras é apagado a cada start (`RESET_DB_ON_STARTUP=true`, decisão de 2026-09-27) e a quadra expira após 1 h parada (`QUADRA_TTL_SECONDS=3600`). O Joguinho é durável e guarda o código da quadra. Nada reconcilia os dois lados: um deploy, um reboot ou um intervalo longo deixam o joguinho apontando para uma quadra morta (QA P2/F3). A US16 dá a saída; esta história evita o problema.

## Decisão B (Navigator, 2026-10-08): opção (a)

- **(a) Escolhida:** ao subir e ao montar o estado, reconciliar: desvincular `quadra_id` inexistente e sinalizar a chamada órfã; a quadra vinculada a uma rodada `em_andamento` não expira por TTL.
- **(b) Rejeitada:** banco das quadras em volume e sem `RESET_DB_ON_STARTUP`. Revê a decisão de 2026-09-27 e pede um registro de decisão novo; é o que mais combina com o princípio "Perder conexão não pode perder o jogo".

## Acceptance

- **Dado** uma rodada em andamento com quadra vinculada **quando** o servidor reinicia **então** o joguinho não mostra vínculo com quadra inexistente; uma partida chamada órfã aparece como "quadra indisponível" com a saída da US16 (anular).
- **Dado** uma rodada em andamento **quando** a quadra fica mais de 1 h sem atualização **então** ela não expira.

## Regressão (QA)

Cenários 1 e 7 do relatório de furos.
