---
id: debt-fluxos-da-interface-sem-teste-de-ponta-a-ponta
status: Carried
kind: validation
severity: medium
source: CV3.DS1.US2
revisit_trigger: Escolha de um runner de navegador (o mesmo que a dívida de contraste do Modo Sol pede), ou mais um defeito de interface achado só no teste físico
closure_condition: Um teste que percorra, num navegador, criar sala → vincular relógio → tornar controlador → passar controle, rodando junto com os demais; e, no relógio, testes de tela (Compose) ou do WatchModel com servidor falso cobrindo abertura, troca e cancelamento
---

# Fluxos da Interface sem Teste de Ponta a Ponta

## Description

O site tem `node --test` para lógica pura e `svelte-check`, mas nenhum teste que renderize e clique nas telas. Os testes do backend chamam as rotas direto.

## Carrying Reason

Montar um runner de navegador é trabalho próprio, fora do escopo da US2. Os dois defeitos achados foram corrigidos com testes de lógica.

## Impact

Na US2, dois defeitos de interface só apareceram no teste físico do Navigator:

- a engrenagem das configurações aparecia vazia desde a CV2 (ícone `engrenagem` inexistente);
- não havia botão para passar o controle, embora a rota existisse desde a CV2.DS2.US5.

Cada um custou um ciclo de deploy no Mini PC, e cada deploy apaga as salas (`debt-banco-de-producao-sem-volume-persistente`).

Na US5 (CV3.DS1.US5), o mesmo padrão no relógio: três ajustes de tela (elementos fora do centro no mostrador redondo, "Retornar" piscando antes da verificação, faixa "Ingressar numa quadra" aparecendo por um instante) só apareceram no teste físico, em três deploys. O fluxo de troca no aparelho (adotar o vínculo novo, cancelamento refeito ao reconectar, corrida entre aprovar e cancelar) tem teste só no servidor; no Android, só a lógica pura (`LinkChoice.kt`) é testada.

## Revisit Trigger

Ver frontmatter.

## Closure Condition

Ver frontmatter.

## Notes

`web/tests/icones-usados.test.js` cobre só a classe de defeito do ícone.

Atualizado na US5 (2026-09-23): o `WatchModel` tem 517 linhas; separar vínculo de placar/fila, previsto para o início da US4, facilita testar cada parte com um servidor falso.
