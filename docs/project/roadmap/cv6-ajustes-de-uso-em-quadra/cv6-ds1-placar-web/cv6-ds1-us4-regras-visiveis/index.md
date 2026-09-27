---
code: CV6.DS1.US4
level: User Story
status: Done
status_reason: validado e aceito pelo Navigator em 2026-09-27
updated: 2026-09-27
---

# CV6.DS1.US4 — Regras da partida visíveis no placar

## Intent

Como participante, quero ver a pontuação-alvo e a vantagem durante o jogo, para entender as regras sem precisar criar outra sala.

## Scope

- Exibir resumo das regras ativas, como “12 pontos | Vantagem”.
- Indicar também ausência de vantagem e teto quando configurado.
- Manter o resumo visível para controlador e espectador.

## Acceptance / Done Condition

- Dada uma partida configurada, quando acesso o placar, então vejo alvo e condição de vantagem corretos.
- Quando o administrador altera as regras pelas ações existentes, então o resumo se atualiza nos clientes conectados.
- Dado teto configurado, então o resumo não omite essa condição de encerramento.

## Validation Route

Abrir dois clientes; configurar 12 com vantagem, 15 sem vantagem e uma regra com teto. Aprova se ambos mostram as regras vigentes sem abrir ajustes; falha se o resumo estiver ausente, desatualizado ou ambíguo.

Aplicar também a [matriz comum](../../index.md#validação-comum). Este roteiro é para a futura implementação; não representa testes já executados.

## Out of Scope

Mudanças não descritas nesta HU, novas regras de jogo e alterações de permissões.

## Notes

Relacionada à configuração já existente em CV1.DS3.US1. Posicionamento deve ser conciliado com o cabeçalho compacto; não criar regras novas.

Origem: rodada de feedback do Navigator em 27/09/2026. Dependências técnicas, desenho final e versão serão definidos no checkpoint de planejamento da implementação.


## Entrega (2026-09-27)

Coberta sem branch própria: a US1 pôs "12 pontos · Vantagem · Teto N" no topo de quem opera (`resumirRegras`), e o placar do espectador já exibia alvo, vantagem e teto. O resumo vem do estado da partida e atualiza nos clientes conectados; o Navigator conferiu "15 pontos · Sem vantagem" ao validar a US5.
