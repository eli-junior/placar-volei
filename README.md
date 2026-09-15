# Placar Vôlei

Placar de vôlei compartilhado em tempo real para pelada. Uma pessoa marca os pontos e todos os presentes acompanham no próprio celular, com registro auditável de cada ponto e de cada correção.

Roda no Mini PC de casa, exposto por Cloudflare Tunnel. Os dados não saem daqui.

## Estado

Versão `0.3.3` entregue: Sucessão automática de admin após 2 minutos de ausência (`CV1.DS2.US2`). Nomes reais de jogadores nas equipes e inversão local de lados na quadra (`CV1.DS3.US2`). Promoção e revogação de controladores (`CV1.DS2.US1`). Núcleo completo da partida (`CV1.DS1`): fundação (`TS1`), criação de salas por código PIN (`US1`), marcação em tempo real (`US2`), desfazer ponto a ponto (`US3`), encerramento de partida e reinício sob demanda (`US4`), empacotamento Docker multi-estágio (`TS2`), modo imersivo com placar dobrável manual (`US5`), fixtures declarativas (`TS3`) e linha do tempo auditável (`CV1.DS4.US1`).

Próximo trabalho: `CV1.DS3.US1` (regras da partida configuráveis) ou `CV1.DS2.TS1` / `CV1.DS2.US3` (owner takeover e proteção).

## Como funciona

- **Criar Placar** — o criador informa um apelido, a aplicação gera um código numérico aleatório de 5 dígitos (ex: `48291`) exibido com destaque no topo e ele assume o papel de **Admin**.
- **Acompanhar** — qualquer pessoa digita o código de 5 dígitos e seu apelido na tela inicial, ingressando imediatamente como **Espectador**.
- **Registro** — todo participante informa um apelido. Sem cadastro, sem senha.
- **Papéis e Sucessão** — o criador é Admin. O Admin pode promover Espectadores a **Controlador** (e revogar permissões a qualquer momento). Admins e Controladores podem marcar e desfazer pontos. Se o Admin ficar offline por mais de 2 minutos, o controlador mais antigo é promovido automaticamente a Admin via WebSocket. Ao reconectar, o admin anterior retorna como Controlador.
- **Capacidade e Ciclo de Vida** — suporta até 20 salas ativas e 20 pessoas por sala. Salas sem lances há mais de 1 hora são limpas automaticamente.
- **Partida** — set único até a pontuação-alvo configurada, com vantagem de 2 opcional e teto opcional.
- **Correção** — admin desfaz ponto a ponto até zerar. Nada é apagado: a correção vira registro.
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
