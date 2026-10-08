---
code: CV8.DS1.US2
level: User Story
status: Validated
status_reason: validada pelo Navigator em 2026-10-07 (0.33.0); aguarda merge
updated: 2026-10-07
related:
  - ../../../../decisions/records/2026-10-07T2300Z-sessao-unica-presenca-e-ordem-de-chegada.md
---

# Abrir sessão e marcar presença

## Intent

**Como** operador, **quero** abrir a sessão do dia e marcar quem está presente, **para** definir quem entra no sorteio.

## Acceptance / Done Condition

- **CA1:** Só uma sessão aberta por vez.
- **CA2:** Marcar/desmarcar presença a partir da base; permitir cadastro rápido inline (substituído, na 0.46.0, pelo botão Gerenciar jogadores).
- **CA3:** Entre rodadas, adicionar/remover presentes livremente.
- **CA4:** A ordem de chegada é registrada: cada presença marcada recebe a próxima posição (1º, 2º, 3º…) e a lista a exibe. Ao marcar presença (inclusive desmarcar e marcar de novo) o jogador vai automaticamente para o fim da ordem.
- **CA5:** O operador pode reordenar a fila de chegada manualmente a qualquer momento antes do sorteio (RN-15).

Regras: RN-11, RN-13, RN-15 (ver [regras-de-negocio.md](../../regras-de-negocio.md)).

## Entregue

Sessão única por índice no banco, presença a partir da base com cadastro rápido, ordem de chegada de 1 a N editável (↑/↓), aviso do mínimo de 4, encerrar sessão e inativar tirando da presença. Plano: [plan.md](plan.md). Validação: [test-guide.md](test-guide.md).

## Validation Route

A definir no plano (Passo 2).

## Out of Scope

Formato trio e histórico entre sessões (fase 2).
