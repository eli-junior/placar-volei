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

Na CV4.DS2.US2, a estabilidade do placar ao revelar controles, o descarte do toque de revelação e a recusa de tela cheia foram verificados com scripts Playwright temporários, fora do repositório. Esses cenários devem entrar na suíte da `CV4.DS3.TS1`.

Na CV4.DS3.US1, operação sem rolagem (390 e 1066 px), inversão dos +1, posse com dois clientes, `Assumir` e chamada forjada sem controle (403) foram verificados com scripts Playwright temporários. Entram na suíte da `CV4.DS3.TS1`.

Na CV4.DS3.US2, retorno de foco após diálogos, menu ⋯ por papel, campo visível em tela baixa (teclado) e vitória em dois clientes foram verificados da mesma forma. Entram na suíte da `CV4.DS3.TS1`.

**Atualização (CV4.DS3.TS1, 2026-09-26):** a parte web está coberta. `npm run test:e2e` (Playwright) percorre criar sala → tornar controlador → assumir/passar controle → pontuar em dois clientes, junto com os demais testes e no CI. Falta a metade do relógio (testes de tela Compose ou do `WatchModel` com servidor falso), prevista na `CV3.DS1.TS1`.

## Revisit Trigger

Ver frontmatter.

## Closure Condition

Ver frontmatter.

## Notes

`web/tests/icones-usados.test.js` cobre só a classe de defeito do ícone.

Atualizado na US5 (2026-09-23): o `WatchModel` tem 517 linhas; separar vínculo de placar/fila, previsto para o início da US4, facilita testar cada parte com um servidor falso.

## Progresso

- 2026-09-26 (CV3.DS1.TS1, 0.19.0): fila, placar confirmado e envio do relógio saíram para a `ScoreSync`, testada com servidor falso (`ScoreSyncTest`). Continuam sem teste: abertura, troca de quadra e cancelamento no `WatchModel`.
- 2026-09-27 (CV6.DS2.US1): a leitura foi conferida no Galaxy Watch real com APK release, incluindo 0, 12 e 100, batimento, controle no telefone, fim de partida e Nova. A dívida continua Carried porque essa validação manual não substitui testes Compose ou do `WatchModel` para os fluxos de tela.
