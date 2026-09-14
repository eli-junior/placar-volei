---
code: CV1.DS1.US4
level: User Story
status: Active
status_reason: em andamento na branch feature/cv1-ds1-us4-encerramento-e-reinicio
updated: 2026-09-14
related:
  - CV1.DS3.US1
---

# CV1.DS1.US4 — Encerramento da partida e reinício sob demanda

## Intent

Ao alguém vencer, o sistema anuncia a vitória com destaque na tela e disponibiliza o botão "Iniciar Nova Partida" para o controlador, mantendo o histórico auditável da partida anterior e iniciando um novo jogo em 0x0 sob demanda.

## Scope

Avaliação da condição de vitória a cada ponto, gravação do evento `PARTIDA_ENCERRADA`, anúncio do vencedor na tela, arquivamento da partida encerrada e abertura de nova partida zerada na mesma quadra quando o botão "Iniciar Nova Partida" for acionado.

## Acceptance / Done Condition

Given uma quadra configurada para 12 pontos com vantagem de 2
When o Time A chega a 12x10
Then todas as telas anunciam a vitória do Time A
And o evento `PARTIDA_ENCERRADA` é registrado no log
And a partida atual é arquivada
And um botão "Iniciar Nova Partida" é exibido para o controlador
When o controlador clica em "Iniciar Nova Partida"
Then uma nova partida começa em 0x0 na mesma quadra com as mesmas regras
And em 12x11 a partida **não** encerra, seguindo até alguém abrir 2 pontos ou atingir o teto configurado.

## Validation Route

Três cenários: vitória direta (12x10), vitória por vantagem após empate (14x12) e, com teto configurado em 15, encerramento em 15x14. Confirmar em duas telas o anúncio e o placar zerado em seguida.

## Out of Scope

Contador de vitórias da rodada, tela de consulta de partidas arquivadas.

## Notes

Enquanto DS3 não entrega a configuração pela UI, os valores vêm de padrão no código (12 pontos, vantagem de 2 ligada, sem teto).

Desfazer o ponto da vitória logo após o encerramento precisa ter comportamento definido no plano desta story.
