---
status: Decided
raised: 2026-09-27
decided: 2026-09-27
deciders:
  - Eli (Navigator)
  - Codex (Driver)
related:
  - CV6.DS2.US1
---

# Leitura e correção curta no placar do relógio

## Decision

O placar do relógio usa a fonte Teko local, com tamanho ajustado ao espaço disponível para também caberem três dígitos. O indicador de batimentos fica centralizado no topo. A correção usa o rótulo curto **Voltar Ponto**, enquanto a descrição para acessibilidade mantém a equipe do último ponto. A ação **Nova** permanece verde e exige dois toques.

## Rationale

O relógio é consultado rapidamente e em mostrador circular. A hierarquia precisa privilegiar os números, sem perder a identificação do ponto que será corrigido. A fonte é redistribuída sob a SIL Open Font License e acompanha o APK; não há download durante o jogo.

## Consequences

O layout reserva espaço para avisos, batimentos e ações. A cor e o texto visível não carregam sozinhos toda a informação: o conteúdo acessível informa estado e equipe. A futura `CV6.DS2.US2` pode trocar o indicador atual pelo aro sem mover o placar principal.

## Review Trigger

Revisar se a validação em outro modelo de relógio mostrar recorte, baixa legibilidade ou conflito entre o aro e os batimentos.
