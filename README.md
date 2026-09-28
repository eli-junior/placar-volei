# Placar Vôlei

Placar de vôlei compartilhado em tempo real para pelada. Uma pessoa marca os pontos e todos os presentes acompanham no próprio celular, com registro auditável de cada ponto e de cada correção.

Roda no Mini PC de casa, exposto por Cloudflare Tunnel. Os dados não saem daqui.

## Estado

Wear OS `0.24.1` entregue: bola animada marca a equipe do último ponto, com retorno visual, tátil e sonoro após gravar o toque. Equipe A azul e B laranja; nomes dos jogadores em linhas separadas. Validado no Galaxy Watch pelo Navigator (`CV6.DS2.US3`). Backend e web seguem em `0.24.0`, compatíveis com este APK.

O relógio também tem aro de conexão, fila offline durável, desfazer e descarte de conflitos com aviso. O histórico das entregas está no [changelog](CHANGELOG.md).

Próximo trabalho: `CV6.DS2.US4` — apagar a tela e retomar pelo pulso, investigando continuidade da conexão durante o repouso.

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

Ver `docs/process/development-guide.md`. Verificação completa, a mesma do CI (`.github/workflows/ci.yml`):

```bash
cd web && npm ci && npm test && npm run check && npm run build && cd ..
uv run pytest && uv run ruff check app tests
cd web && npm run test:e2e   # Playwright + axe; na primeira vez: npx playwright install chromium
```
