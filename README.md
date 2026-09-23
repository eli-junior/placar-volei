# Placar Vôlei

Placar de vôlei compartilhado em tempo real para pelada. Uma pessoa marca os pontos e todos os presentes acompanham no próprio celular, com registro auditável de cada ponto e de cada correção.

Roda no Mini PC de casa, exposto por Cloudflare Tunnel. Os dados não saem daqui.

## Estado

Versão `0.8.0` entregue: pontuar pelo Galaxy Watch. O relógio entra na sala como **Eli (Relógio)**, recebe o controle pelo botão **Passar controle** e marca os pontos com fila durável e sem duplicar (`CV3.DS1.US2`). A `0.7.0` trouxe o vínculo do relógio pelo telefone (`CV3.DS1.US1`; app Wear OS em `wear/`). Antes: Modo Sol aplicado à tela inteira (`0.6.1`), CV2 completo com layouts fluidos, Home ao vivo e WCAG 2.2 (`0.6.0`), e o CV1 com salas por PIN, papéis, regras configuráveis e linha do tempo auditável.

Próximo trabalho: `CV3.DS1.US2`, ver e marcar pontos pelo relógio.

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
