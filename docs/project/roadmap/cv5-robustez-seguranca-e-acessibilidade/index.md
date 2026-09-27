---
code: CV5
level: Value
status: Planned
status_reason: criado a partir da revisão por especialistas (backend, Svelte, Wear OS, UX) de 2026-09-27
updated: 2026-09-27
---

# CV5 — Robustez, segurança e acessibilidade

## Intent

Fechar as fragilidades encontradas na revisão de 2026-09-27: salas que qualquer um descobre, deploy que perde dados, relógio que pode travar ou perder lances, placar que congela sem aviso e barreiras de acessibilidade na quadra.

## Ordem proposta

A ordem vai do maior risco com menor esforço para o polimento. Cada Delivery Story fecha sozinha.

1. [DS1 — Segurança e deploy](cv5-ds1-seguranca-e-deploy/index.md): pequeno, alto risco, só backend.
2. [DS2 — Relógio sem perda e sem crash](cv5-ds2-relogio-sem-perda/index.md): prepara o terreno da `CV3.DS1.US4`.
3. `CV3.DS1.US4` (revisão de conflito pelo telefone) retoma aqui, já sobre a fila endurecida.
4. [DS3 — Tempo real que não congela](cv5-ds3-tempo-real-confiavel/index.md).
5. [DS4 — Acessibilidade e UX na quadra](cv5-ds4-acessibilidade-e-ux/index.md).
6. [DS5 — Manutenção do frontend](cv5-ds5-manutencao-do-frontend/index.md): sem mudança visível; pode entrar entre outras quando houver folga.

## Acceptance / Done Condition

Nenhum PIN é descoberto sem ser compartilhado, um deploy não apaga dados, o relógio não perde lance nem fecha sozinho, o espectador percebe quando a conexão cai e as telas passam no roteiro de acessibilidade com leitor de tela e movimento reduzido.

## Out of Scope

- Envio da fila do relógio em segundo plano (WorkManager): continua como follow-up da `CV3.DS1.US4`.
- Novas funcionalidades de produto.

## Notes

Achados originais com arquivo e linha ficam nas histórias. Débitos relacionados: `debt-banco-de-producao-sem-volume-persistente`, `debt-limite-de-vinculo-do-relogio-por-ip-e-em-memoria`.
