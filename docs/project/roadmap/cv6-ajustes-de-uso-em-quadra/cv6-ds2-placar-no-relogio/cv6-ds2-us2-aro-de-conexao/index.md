---
code: CV6.DS2.US2
level: User Story
status: Done
status_reason: validada pelo Navigator no relógio; entregue na 0.22.1
updated: 2026-09-28
---

# CV6.DS2.US2 — Conexão indicada por aro discreto

## Intent

Como jogador, quero perceber a conexão por um aro suave na borda do relógio, para liberar espaço no centro da tela.

## Scope

- Substituir a bolinha por um aro fino ao redor de toda a tela.
- Representar o estado de conexão pelas cores do aro.
- Manter o aro discreto e sem interferir nas áreas de toque.

## Acceptance / Done Condition

- Quando o placar está visível, então o aro acompanha a borda circular completa sem disputar destaque com os números.
- Quando a conexão muda, então a cor corresponde ao estado real.
- Quando consulto o status com recurso de acessibilidade, então posso identificar o estado sem depender apenas da cor.

## Validation Route

Com telefone e relógio, desconectar por 30 segundos e reconectar; observar borda, estado e atualização do placar. Aprova se o aro é completo, discreto e verdadeiro; falha se indicar conexão saudável enquanto está desconectado.

Aplicar também a [matriz comum](../../index.md#validação-comum). Este roteiro é para a futura implementação; não representa testes já executados.

## Out of Scope

Mudanças não descritas nesta HU, novas regras de jogo e alterações de permissões.

## Notes

Conciliar com os batimentos centralizados da US1. Mapear estados e cores no planejamento.

Origem: rodada de feedback do Navigator em 27/09/2026. Dependências técnicas, desenho final e versão serão definidos no checkpoint de planejamento da implementação.


## Planejamento atual

Ver [plano](plan.md). Branch `feature/cv6-ds2-us2-aro-de-conexao`, a partir de `origin/master` `290a36c`. Checkpoint 1 aprovado. Implementação aguarda integração da US1 pelos checkpoints próprios.
