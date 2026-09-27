---
code: CV6.DS2.US1
level: User Story
status: Active
status_reason: puxada para planejamento; aguardando Checkpoint 1
updated: 2026-09-27
---

# CV6.DS2.US1 — Placar e batimentos mais legíveis no relógio

## Intent

Como jogador, quero números maiores e informações bem posicionadas no relógio, para consultar o placar rapidamente.

## Scope

- Exibir somente “Controle no telefone.” quando aplicável.
- Subir os rótulos Nós / Eles e ampliar os números.
- Ampliar um pouco o indicador de batimentos e centralizá-lo no topo.
- Avaliar uso da mesma fonte do placar principal.

## Acceptance / Done Condition

- Dado controle no telefone, então o texto exibido é exatamente “Controle no telefone.”.
- Quando consulto o relógio, então rótulos elevados, números maiores e batimentos centralizados não se sobrepõem nem cortam na borda circular.
- Quando o batimento está indisponível, então a indicação permanece honesta, sem inventar medição.

## Validation Route

Em relógio real com telefone conectado, comparar 0, 12 e 100, com e sem batimento e nos diferentes estados de controle. Aprova se a leitura melhora sem ocultar desfazer e nova partida; falha se cortar conteúdo ou apresentar medição falsa.

Aplicar também a [matriz comum](../../index.md#validação-comum). Este roteiro é para a futura implementação; não representa testes já executados.

## Out of Scope

Mudanças não descritas nesta HU, novas regras de jogo e alterações de permissões.

## Notes

Investigar compatibilidade, licença e legibilidade da fonte antes de prometer paridade. Preservar o treino no Samsung Health; não ampliar coleta de dados.

Origem: rodada de feedback do Navigator em 27/09/2026. Dependências técnicas, desenho final e versão serão definidos no checkpoint de planejamento da implementação.


## Planejamento atual

Branch: `feature/cv6-ds2-us1-leitura-no-pulso`. Ver [plano](plan.md). Implementação depende do aceite no Checkpoint 1.
