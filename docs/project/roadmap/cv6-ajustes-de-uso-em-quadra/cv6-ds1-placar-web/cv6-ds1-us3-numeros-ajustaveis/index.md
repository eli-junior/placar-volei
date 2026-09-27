---
code: CV6.DS1.US3
level: User Story
status: Planned
status_reason: feedback do Navigator em 2026-09-27; desenvolvimento posterior
updated: 2026-09-27
---

# CV6.DS1.US3 — Números proporcionais e tamanho configurável

## Intent

Como participante, quero um placar proporcional à minha tela e poder ajustar o tamanho dos números, para ler confortavelmente na distância de uso.

## Scope

- Rever a escala automática, especialmente no Fold fechado.
- Adicionar ajuste de tamanho dos números nas configurações.
- Preservar legibilidade dos dois estilos de placar existentes.

## Acceptance / Done Condition

- Dado o tamanho padrão, quando abro ou fecho o Fold ou giro o aparelho, então os números se adaptam sem cortes ou sobreposição.
- Quando ajusto o tamanho, então os dois números refletem a escolha sem encobrir nomes, regras ou controles.
- Dadas pontuações de um, dois e três dígitos, então o layout acomoda os valores dentro dos limites admitidos.

## Validation Route

Comparar padrão e extremos do ajuste com 0, 12 e 100, nos dois estilos, temas e formatos. Aprova se a escala melhora a leitura e mantém todos os elementos acessíveis; falha se recortar dígitos ou esconder comandos.

Aplicar também a [matriz comum](../../index.md#validação-comum). Este roteiro é para a futura implementação; não representa testes já executados.

## Out of Scope

Mudanças não descritas nesta HU, novas regras de jogo e alterações de permissões.

## Notes

Decidir com o Navigator: faixa/presets, persistência e alcance local ou compartilhado da preferência. Não assumir que mudar um aparelho deve mudar todos.

Origem: rodada de feedback do Navigator em 27/09/2026. Dependências técnicas, desenho final e versão serão definidos no checkpoint de planejamento da implementação.

