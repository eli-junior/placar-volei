---
code: CV6.DS1.US1
level: User Story
status: Planned
status_reason: feedback do Navigator em 2026-09-27; desenvolvimento posterior
updated: 2026-09-27
---

# CV6.DS1.US1 — Cabeçalho compacto e navegação visível

## Intent

Como participante, quero identificar a quadra e acessar as ações do topo rapidamente, para operar o placar sem ocupar espaço excessivo.

## Scope

- Reunir voltar, nome/número da quadra, configurações, inverter lados e status em uma linha.
- Tornar a seta de voltar visível e centralizada.
- Trocar a legenda “Ao vivo” por uma bolinha verde, amarela ou vermelha, mantendo descrição acessível do estado.

## Acceptance / Done Condition

- Dado tablet, Fold aberto ou fechado, quando abro a quadra, então o topo cabe sem sobreposição e a seta fica centralizada.
- Quando aciono inverter lados, então colunas e controles continuam associados à equipe correta.
- Quando muda a conexão, então o indicador representa o estado real e pode ser identificado por tecnologia assistiva.

## Validation Route

Comparar os três formatos nos dois temas; acionar voltar, ajustes e inversão; interromper a rede por 30 segundos e restaurar. Aprova se topo e comandos permanecem legíveis e o status acompanha a conexão; falha se houver cortes ou estado enganoso.

Aplicar também a [matriz comum](../../index.md#validação-comum). Este roteiro é para a futura implementação; não representa testes já executados.

## Out of Scope

Mudanças não descritas nesta HU, novas regras de jogo e alterações de permissões.

## Notes

Definir no planejamento a correspondência exata das três cores com os estados existentes; não reduzir alvos de toque para caber.

Origem: rodada de feedback do Navigator em 27/09/2026. Dependências técnicas, desenho final e versão serão definidos no checkpoint de planejamento da implementação.

