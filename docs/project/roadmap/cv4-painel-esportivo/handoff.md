# Handoff — CV4 Painel esportivo

## Estado em 2026-09-26

### Atualização mais recente — CV4.DS2.US1

- Branch `feature/cv4-ds2-us1-placar-espectador`, baseada em `origin/master` `42f514d` (0.13.2).
- Passo Ariad 7 concluído; Checkpoints 1–4 aprovados e integração em `master` autorizada.
- O placar esportivo do espectador foi implementado, validado e integrado como versão `0.14.0`.
- Evidência: backend 185 testes; frontend 39 testes; Svelte sem avisos; build e Ruff aprovados; inspeção visual nos dois temas em 658 × 781 e 1066 × 600 CSS px.
- O Navigator pediu números maiores durante a validação e aprovou a escala final. Fullscreen continua exclusivamente na US2.
- Próxima entrega: `CV4.DS2.US2`, em branch própria criada da `master` atualizada; apresentar seu Checkpoint 1 antes de implementar fullscreen.
- A versão técnica continua `0.10.1` em backend/web porque `app.config.version` controla a recriação do banco. Este ciclo não deve usar esse campo como versão visual de release sem decisão de migração.

- **Agente:** Codex (Driver), sessão `01a0dd8e-b3b3-7482-a278-5f22f9738d3e`.
- **História concluída:** `CV4.DS1.US1 — Home esportiva e entrada responsiva`.
- **Branch:** `codex/cv4-ds1-us1-home`.
- **Base sincronizada:** `origin/master` em `33534a5`, release 0.12.0.
- **Checkout:** `C:/Users/eli/.codex/worktrees/cv4-home-esportiva/placar_volei`.
- **Passo Ariad:** Passo 7 concluído; Checkpoints 1, 2, 3 e 4 aprovados. Merge autorizado.
- **Remoto:** branch publicada e atualizada continuamente.

## Resultado da E1

- A Home inicia por **Acompanhar**, com criação preservada.
- Em telas largas, acesso e partidas aparecem lado a lado; em telas estreitas, são empilhados.
- Cada partida separa metadados, placar Teko central e ação **Abrir**.
- Tema mostra texto Claro/Escuro e mantém fontes e ícones locais.
- Erro de entrada fica junto ao formulário, com código preservado e foco no apelido.
- A dívida `debt-erro-de-entrada-pela-home-fora-da-vista` foi paga.
- O Navigator aprovou a experiência após quatro rodadas de inspeção no navegador.

## Verificações

- `uv run pytest`: 185 aprovados.
- `npm test`: 31 aprovados.
- `npm run check`: 0 erros e 0 advertências.
- `npm run build`: aprovado.
- `uv run ruff check .`: aprovado; houve apenas aviso local ao gravar cache.
- `uv run ruff format --check .`: 222 arquivos formatados.
- Inspeção visual: 658×900, 904×1000 e 1440 px, temas e partida real isolada.

## Próxima ação exata

Integração autorizada no Checkpoint 4:

1. integrar `codex/cv4-ds1-us1-home` em `master`;
2. enviar `master` ao remoto;
3. encerrar os servidores locais de validação.

Não iniciar `CV4.DS2` na mesma branch. A próxima história precisa de branch própria baseada na master já integrada.

## Próxima entrega planejada

`CV4.DS2.US1 — Placar do espectador e responsividade`. Ler o [plano](plan.md), a [rota V2](test-guide.md) e a [história](cv4-ds2-acompanhamento/cv4-ds2-us1-placar/index.md). Fullscreen pertence à história seguinte, `CV4.DS2.US2`.

## Coerência

- Roadmap: CV4 ativa; CV4.DS1 e sua única US concluídas; CV4.DS2 e CV4.DS3 permanecem planejadas.
- Decisão visual existente continua válida; não foi necessária uma nova decisão.
- Princípios de produto permanecem coerentes e não exigem alteração.
- README e briefing não precisam descrever a aparência da Home; o worklog registra a mudança observável.
- Versões declaradas em backend/web ainda divergem do changelog e já eram assim na base. Esta história não amplia esse problema nem altera Wear OS; alinhar a versão no fechamento de release apropriado.
- Testes completos de navegador e matriz física permanecem em `CV4.DS3.TS1`; nenhuma evidência futura foi registrada como executada.
