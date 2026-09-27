---
code: CV6.DS1.US2
level: User Story
status: Done
status_reason: validado e aceito pelo Navigator em 2026-09-27
updated: 2026-09-27
---

# CV6.DS1.US2 — Pontuar e desfazer na parte inferior

## Intent

Como controlador, quero os botões de pontuação abaixo do placar e o desfazer próximo, para marcar e corrigir com facilidade.

## Scope

- Mover +1 de ambas as equipes para baixo também no tablet.
- No tablet e Fold aberto, colocar Desfazer entre os dois +1.
- No Fold fechado/celular, permitir Desfazer na linha abaixo.

## Acceptance / Done Condition

- Dado controle da partida, quando uso tablet ou Fold aberto, então encontro +1 / Desfazer / +1 abaixo dos números.
- Dada tela estreita, então o desfazer permanece visível e utilizável abaixo dos +1.
- Quando marco e desfaço após inverter lados, então a correção afeta o ponto esperado, mantendo o histórico e as permissões.

## Validation Route

Com controlador e espectador simultâneos, marcar alternadamente, inverter lados e desfazer; repetir nos três formatos. Aprova se ambos veem o resultado correto e os controles são acessíveis; falha se houver associação errada ou controle encoberto.

Aplicar também a [matriz comum](../../index.md#validação-comum). Este roteiro é para a futura implementação; não representa testes já executados.

## Out of Scope

Mudanças não descritas nesta HU, novas regras de jogo e alterações de permissões.

## Notes

Preservar estados desabilitados e proteções existentes; não alterar regras de pontuação.

Origem: rodada de feedback do Navigator em 27/09/2026. Dependências técnicas, desenho final e versão serão definidos no checkpoint de planejamento da implementação.


## Entrega (2026-09-27)

- Desfazer entrou na grade do palco em `Placar.svelte`: a partir de 600px de container, +1 / Desfazer / +1 sob o placar (altura de 86 a 120px); abaixo disso, Desfazer na linha de baixo em largura total.
- A inversão troca só os +1; o Desfazer fica no meio. Os +1 deixaram de ficar nas laterais em paisagem.
- e2e cobre posição no tablet, inversão e tela estreita.
