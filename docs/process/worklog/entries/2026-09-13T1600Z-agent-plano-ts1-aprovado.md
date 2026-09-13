---
date: 2026-09-13T16:00:00Z
author: Claude (Driver)
kind: milestone
related:
  - CV1.DS1.TS1
  - CV1.DS1.TS2
verification:
  - plano apresentado no Checkpoint 1 e aprovado pelo Navigator
---

# Plano da TS1 aprovado e documentado; implementação adiada

## What changed

Repositório publicado em `git@github.com:eli-junior/placar-volei.git`, público. `.gitignore` criado cobrindo `.env`, SQLite, `node_modules`, `.venv` e estáticos gerados pelo build.

Checkpoint 1 de `CV1.DS1.TS1` apresentado e aprovado. O Navigator optou por registrar o plano e adiar a implementação, então o ciclo parou aqui por decisão dele, não por bloqueio.

- `cv1-ds1-ts1-fundacao-e-event-store/plan.md` — plano completo: estrutura de arquivos, modelo de dados, envelope do evento e sete decisões de design com alternativas rejeitadas.
- `cv1-ds1-ts1-fundacao-e-event-store/test-guide.md` — doze casos de teste automatizado e a rota de validação do Navigator, com condições de aprovação e falha.
- `CV1.DS1.TS2` criada — empacotamento e deploy no Mini PC, que era risco anotado no plano da TS1 e virou trabalho nomeado.

## Why it matters

Duas decisões do plano resolvem pendências que estavam anotadas em outras stories:

- `PONTO_DESFEITO` referenciando o `seq` do ponto anulado faz desfazer o ponto da vitória devolver a partida ao estado não encerrado sem tratamento especial — era o pendente aberto em `CV1.DS1.US4`.
- A projeção aplicar a configuração vigente no momento da avaliação, e não a do início da partida, é o que faz `CV1.DS3.US1` funcionar como especificado.

O plano aprovado também significa que a próxima sessão de trabalho na TS1 entra direto em implementação, sem repetir o Checkpoint 1.

## Verification

Nenhum código escrito. Plano revisado e aprovado pelo Navigator.

## Follow-up

- Implementar `CV1.DS1.TS1` a partir de `plan.md`.
- Definir a estratégia mínima de migração de schema antes da primeira partida real gravada.
- Corrigir os comandos do development guide com o retorno da primeira execução do Navigator.
- Registrar em `docs/project/debt/items/` se o shell indisponível na máquina do Navigator passar a atrapalhar o ciclo de forma recorrente.
