# Placar Vôlei

Placar de vôlei compartilhado em tempo real para pelada. Uma pessoa marca os pontos e todos os presentes acompanham no próprio celular, com registro auditável de cada ponto e de cada correção.

Roda no Mini PC de casa, exposto por Cloudflare Tunnel. Os dados não saem daqui.

## Estado

APK Android do celular (`0.27.0`, `CV7.TS1`): casca Capacitor que abre a quadra online do servidor fixo do build, depois de testar a conexão. Para gerar e instalar:

```bash
export ANDROID_HOME=/caminho/do/Android/Sdk
PLACAR_SERVIDOR=https://placar.exemplo.com scripts/build-apk.sh debug
adb install -r --user 0 android/app/build/outputs/apk/debug/app-debug.apk
```

Precisa de Node, JDK 21 e Android SDK. Validado no Galaxy Z Fold; quadra local e ponte com o relógio ficam para a CV7.


Wear OS `0.25.0` entregue: inclui retorno perceptível ao pontuar e acompanhamento em segundo plano para repousar a tela e retomar pelo pulso (`CV6.DS2.US3–US4`). No Galaxy Watch SM-L330/Android 16, serviço e WebSocket permaneceram ativos durante 60 s em repouso via ADB; gesto físico, atualização remota durante repouso, reconexão, treino e bateria não foram validados. Backend e web seguem em `0.24.0`, compatíveis com este APK.

O relógio também tem bola animada para o último ponto, Equipe A azul e B laranja, aro de conexão, fila offline durável, desfazer e descarte de conflitos com aviso. O histórico das entregas está no [changelog](CHANGELOG.md).

Limitações conhecidas da retomada pelo pulso e evidências estão registradas no [roteiro da US4](docs/project/roadmap/cv6-ajustes-de-uso-em-quadra/cv6-ds2-placar-no-relogio/cv6-ds2-us4-repouso-e-retomada/test-guide.md).

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
