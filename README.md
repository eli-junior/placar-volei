# Placar Vôlei

Placar de vôlei compartilhado em tempo real para pelada. Uma pessoa marca os pontos e todos os presentes acompanham no próprio celular, com registro auditável de cada ponto e de cada correção.

Roda no Mini PC de casa, exposto por Cloudflare Tunnel. Os dados não saem daqui.

## Estado

Fase inicial. Fundação (`CV1.DS1.TS1`), criação de arenas, quadras e entrada por apelido (`CV1.DS1.US1`), marcação de pontos em tempo real (`CV1.DS1.US2`) e desfazer ponto a ponto até zerar com permissão por papel (`CV1.DS1.US3`) concluídas e testadas.

Próximo trabalho: `CV1.DS4.US1` — linha do tempo da partida.

## Como funciona

- **Arena** — clube ou complexo esportivo (ex: T9 Beach Club), que abriga múltiplas quadras.
- **Quadra** — sala de jogo dentro da arena, escolhida na lista.
- **Registro** — todo participante informa um apelido. Sem cadastro, sem senha.
- **Papéis** — o primeiro a entrar vira admin e pode promover controladores. Espectadores só assistem.
- **Partida** — set único até a pontuação-alvo configurada, com vantagem de 2 opcional e teto opcional. Ao encerrar, anuncia o vencedor e zera para a próxima.
- **Correção** — controladores desfazem ponto a ponto até zerar. Nada é apagado: a correção vira registro.
- **Linha do tempo** — mostra como o placar foi construído, ponto a ponto.

## Stack

Python + FastAPI, WebSocket, SQLite. Frontend em Svelte 5, compilado e servido como estáticos pelo próprio backend. Deploy em contêiner no Mini PC, com build multi-estágio — Node só no build, nunca no runtime.

O placar é uma projeção de um log de eventos append-only, não um contador. Ver `docs/project/decisions/records/`.

## Documentação

Este projeto usa **Ariad** como método de desenvolvimento humano-agente. O agente é o Driver, o humano é o Navigator.

- `AGENTS.md` — porta de entrada para agentes de código.
- `docs/project/briefing.md` — contexto estável do projeto.
- `docs/product/principles.md` — princípios de produto que orientam trade-offs.
- `docs/project/roadmap/` — o que vem pela frente, em CV / DS / US / TS.
- `docs/project/decisions/records/` — decisões tomadas e questões em aberto.
- `docs/process/development-guide.md` — contrato operacional: comandos, validação, política de commits.
- `docs/process/worklog/entries/` — marcos do projeto.

## Desenvolvimento

Ver `docs/process/development-guide.md`.
