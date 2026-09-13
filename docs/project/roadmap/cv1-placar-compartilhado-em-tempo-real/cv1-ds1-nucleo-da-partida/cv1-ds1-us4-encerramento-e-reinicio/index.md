---
code: CV1.DS1.US4
level: User Story
status: Planned
status_reason:
updated: 2026-09-13
related:
  - CV1.DS3.US1
---

# CV1.DS1.US4 — Encerramento automático e reinício da partida

## Intent

Ao alguém vencer, o sistema anuncia e já deixa a quadra pronta para o próximo jogo, sem ninguém precisar mexer em nada.

## Scope

Avaliação da condição de vitória a cada ponto, evento `PARTIDA_ENCERRADA`, anúncio do vencedor na tela, arquivamento da partida e abertura automática de nova partida zerada na mesma quadra, com a mesma configuração.

## Acceptance / Done Condition

Given uma quadra configurada para 12 pontos com vantagem de 2
When o Time A chega a 12x10
Then todas as telas anunciam a vitória do Time A
And a partida é arquivada com seu log completo
And uma nova partida começa em 0x0 na mesma quadra
And em 12x11 a partida **não** encerra, seguindo até alguém abrir 2 pontos ou atingir o teto configurado.

## Validation Route

Três cenários: vitória direta (12x10), vitória por vantagem após empate (14x12) e, com teto configurado em 15, encerramento em 15x14. Confirmar em duas telas o anúncio e o placar zerado em seguida.

## Out of Scope

Contador de vitórias da rodada, tela de consulta de partidas arquivadas.

## Notes

Enquanto DS3 não entrega a configuração pela UI, os valores vêm de padrão no código (12 pontos, vantagem de 2 ligada, sem teto).

Desfazer o ponto da vitória logo após o encerramento precisa ter comportamento definido no plano desta story.
