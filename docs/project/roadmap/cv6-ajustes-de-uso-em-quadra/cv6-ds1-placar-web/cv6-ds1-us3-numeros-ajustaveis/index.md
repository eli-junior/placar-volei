---
code: CV6.DS1.US3
level: User Story
status: Done
status_reason: validado e aceito pelo Navigator em 2026-09-27
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


## Entrega (2026-09-27)

- Tela em pé (proporção mais alta que 3:4): equipes empilhadas, cada uma com a largura toda; o × some nesse modo. Vale para esportivo e clássico, e o ⇄ troca quem fica em cima.
- P/M/G só no aparelho (`placar:tamanho_numeros`), no menu ⋯. Na validação o Navigator pediu que o tamanho anterior virasse P: P = 1, M = 1,25 (padrão), G = 1,5.
- Limites medidos pelos dígitos reais (dois ≈ .62em, três ≈ .95em de largura) impedem corte e invasão do nome, inclusive com 100 pontos em G.
- Clássico já ocupa a coluna: P/M/G não o altera.
- Follow-up não feito: no tablet deitado o glifo fica acima do centro; centralizar liberaria altura para o G.

## Ajuste pós-entrega (0.21.1, 2026-09-27)

A escala P/M/G passou a valer também no placar clássico (cartões). O número segue o contêiner, multiplica por `--escala-numeros` e é limitado ao cartão, com variação para três dígitos e tela em pé. No clássico, P deixa de ser o antigo tamanho fixo de 7.2rem. Validado pelo Navigator.
