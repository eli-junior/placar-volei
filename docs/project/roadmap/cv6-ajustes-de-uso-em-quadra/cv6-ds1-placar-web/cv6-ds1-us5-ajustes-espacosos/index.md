---
code: CV6.DS1.US5
level: User Story
status: Planned
status_reason: feedback do Navigator em 2026-09-27; desenvolvimento posterior
updated: 2026-09-27
---

# CV6.DS1.US5 — Configurações legíveis com pontuação primeiro

## Intent

Como administrador, quero ajustes bem distribuídos e pontuação no topo, para encontrar primeiro as regras mais importantes.

## Scope

- Colocar Pontuação e vantagem como primeira seção após o título.
- Reajustar largura, altura, margens internas e espaçamento do modal.
- Adaptar campos, botões e rolagem ao espaço disponível, incluindo teclado aberto.

## Acceptance / Done Condition

- Quando abro configurações, então Pontuação e vantagem aparece antes de visual e equipes.
- Dado tablet, Fold aberto ou fechado, então campos e textos têm respiro e não ficam colados às bordas.
- Quando uso teclado, zoom ou rolagem, então consigo editar e alcançar Salvar e Cancelar.
- Quando salvo ou cancelo, então permanece o comportamento funcional existente.

## Validation Route

Nos três formatos, abrir ajustes, editar alvo, vantagem, teto e jogadores; testar teclado aberto, zoom de 200%, salvar e cancelar. Aprova se nenhum campo ou ação fica inacessível; falha se houver corte, sobreposição ou mudança indevida das regras.

Aplicar também a [matriz comum](../../index.md#validação-comum). Este roteiro é para a futura implementação; não representa testes já executados.

## Out of Scope

Mudanças não descritas nesta HU, novas regras de jogo e alterações de permissões.

## Notes

O ajuste do tamanho dos números integra esta superfície pela US3. A prioridade de pontuação refere-se à ordem das configurações.

Origem: rodada de feedback do Navigator em 27/09/2026. Dependências técnicas, desenho final e versão serão definidos no checkpoint de planejamento da implementação.

