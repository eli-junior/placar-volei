---
code: CV8.DS4.US12
level: User Story
status: Validated
status_reason: implementada na branch feature/cv8-ds4-us12-persistir-sessao (0.39.0); validada pelo Navigator em 2026-10-07 (0.39.0); aguarda merge
updated: 2026-10-07
---

# Persistir sessão

## Intent

**Como** dono do sistema, **quero** que sessões, rodadas, partidas e placares sejam salvos, **para** habilitar rankings futuros.

## Acceptance / Done Condition

- **CA1:** Tudo persistido ao encerrar cada partida (resiliente a queda do servidor — retoma o estado).
- **CA2:** Sem tela de histórico no MVP.

## Validation Route

Plano: [plan.md](plan.md). Rota: [test-guide.md](test-guide.md).

## Entregue

Gravação síncrona (`synchronous=FULL`) e testes que provam a retomada do estado após cada partida, o mata-mata e o campeão, o registro completo para ranking e a preservação das partidas ao cancelar a rodada ou encerrar a sessão. Sem schema nem rota novos.

## Out of Scope

Formato trio e histórico entre sessões (fase 2).
