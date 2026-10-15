---
code: CV8.DS2.US23
level: User Story
status: Validated
status_reason: validada pelo Navigator em 2026-10-15 (0.53.0)
updated: 2026-10-15
related:
  - ../../regras-de-negocio.md
  - ../../../../decisions/records/2026-10-15T1200Z-fila-por-tempo-sem-jogar.md
---

# Fila das rodadas seguintes por tempo sem jogar

## Intent

**Como** jogador, **quero** que nas rodadas seguintes joguem primeiro os times de quem está há mais tempo sem jogar, **para** ninguém abrir uma rodada e fechar a outra, parado tempo demais.

## Acceptance / Done Condition

- **Dado** que a rodada 1 foi encerrada, com quem perdeu a 1ª partida descansando e o campeão tendo jogado a última,
- **Quando** o operador sortear a rodada 2,
- **Então** as duplas saem equilibradas como antes (RN-01, RN-10, RN-14),
- **E** a fila começa pelos times de maior descanso médio (RN-13 revista),
- **E** quem jogou por último vai para o fim, à frente só do time incompleto (RN-05).
- Partida de rodada cancelada conta como jogada. Na 1ª rodada nada muda.

## Validation Route

[test-guide.md](test-guide.md).

## Out of Scope

O ímpar sempre por último (US24); gravar o descanso usado na rodada.
