---
code: CV8.DS4.US11
level: User Story
status: Active
status_reason: implementada na branch feature/cv8-ds4-us11-conduzir-o-mata-mata (0.38.0); aguarda validação do Navigator
updated: 2026-10-07
---

# Conduzir o mata-mata

## Intent

**Como** operador, **quero** que o sistema monte o mata-mata, **para** definir o campeão da rodada.

## Acceptance / Done Condition

- **CA1:** Vencedor da última partida vs. 1º rei; vencedor segue contra o próximo, em ordem cronológica.
- **CA2:** Sem reis → campeão direto.
- **CA3:** Partidas usam o mesmo fluxo de chamar/encerrar/desfazer.
- **CA4:** Entradas de novos times bloqueadas.
- **CA5:** Ao final, registra campeão e libera o próximo sorteio.

Regras: RN-04 (ver [regras-de-negocio.md](../../regras-de-negocio.md)).

## Validation Route

A definir no plano (Passo 2).

## Out of Scope

Formato trio e histórico entre sessões (fase 2).
