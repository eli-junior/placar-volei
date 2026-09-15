---
code: CV1
level: Value
status: Done
status_reason: MVP completo e validado em quadra com todas as entregas (DS1 a DS4)
updated: 2026-09-15
related:
  - docs/project/briefing.md
  - docs/product/principles.md
---

# CV1 — Placar compartilhado e auditável para pelada

## Intent

Um grupo de vôlei consegue jogar uma pelada inteira com o placar mantido no celular, sincronizado entre todos os presentes, com cada ponto e cada correção registrados e consultáveis.

## Scope

Quadras múltiplas, registro por apelido, papéis e permissões, marcação e correção de pontos em tempo real, regras de pontuação configuráveis, encerramento e reinício automático, linha do tempo da partida e recuperação de administração pelo operador da instância.

## Acceptance / Done Condition

O Navigator conduz uma pelada real do início ao fim usando apenas o sistema, com pelo menos três participantes em celulares distintos, sem precisar de placar paralelo em papel e sem intervenção no Mini PC durante o jogo.

## Validation Route

Partida real em quadra, com o sistema publicado via Cloudflare Tunnel, validada pelo Navigator e pelos participantes.

## Out of Scope

Sets múltiplos e tie-break, indicador de saque e troca de lado, nomes personalizados de times, contador de vitórias da rodada, tela de histórico de partidas encerradas, estatísticas por jogador, aplicativo nativo.

## Notes

Delivery Stories: DS1 núcleo da partida, DS2 controle e permissões, DS3 regras configuráveis, DS4 auditoria visível.

Ordem sugerida: DS1 → DS2 → DS3 → DS4. DS3 e DS4 podem trocar de ordem conforme o Navigator; DS4 depende do event store entregue em DS1.
