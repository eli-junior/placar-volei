# Placar Vôlei

Placar de vôlei compartilhado em tempo real para pelada. Uma pessoa marca os pontos e todos os presentes acompanham no próprio celular, com registro auditável de cada ponto e de cada correção.

Roda no Mini PC de casa, exposto por Cloudflare Tunnel. Os dados não saem daqui.

## Estado

Versão `0.21.1` entregue: o CV6.DS1 deixou o placar web mais fácil de ler e operar. O topo cabe em uma linha, com as regras da partida e o status em bolinha. +1 / Desfazer / +1 ficam embaixo do placar, as configurações mostram a pontuação primeiro e cabem no Fold, e em tela em pé as equipes empilham, com tamanho dos números P/M/G em cada aparelho. Antes, a `0.20.0`: o CV5 deixou o placar mais robusto, seguro e acessível. Os limites de tentativa usam o IP real, o banco é limpo a cada start, o placar do navegador percebe conexão morta e volta sozinho, o relógio não perde lances nem trava a fila e ganhou build de release, e o web ficou acessível para leitor de tela e movimento reduzido. Antes, a `0.12.0`: ao fim da partida, o relógio mostra **↶ Desfazer | ▶ Nova**, e um toque começa a próxima partida com os mesmos times e regras (`CV3.DS2.US3`). A `0.11.0` trouxe o batimento no placar: o placar do Galaxy Watch mostra o batimento (`♥ bpm`) enquanto o Samsung Health grava o treino, sem interromper a gravação; o valor fica só no relógio (`CV3.DS2.US2`). A `0.10.1` manteve a tela do placar acesa (`CV3.DS2.US1`). A `0.10.0` trouxe um vínculo por vez no Galaxy Watch. Ao reabrir o app, o relógio oferece **Retornar** à quadra ou **Parear outra quadra**; o vínculo antigo só cai quando o código novo é aprovado (`CV3.DS1.US5`). A `0.9.0` trouxe o desfazer pelo relógio: a faixa **↶ Desfazer** corrige o último ponto que o relógio mostra, inclusive sem rede, sem nunca desfazer um ponto que o relógio não viu (`CV3.DS1.US3`). A `0.8.0` trouxe a pontuação pelo relógio: ele entra na sala como **Eli (Relógio)**, recebe o controle pelo botão **Passar controle** e marca os pontos com fila durável e sem duplicar (`CV3.DS1.US2`). A `0.7.0` trouxe o vínculo do relógio pelo telefone (`CV3.DS1.US1`; app Wear OS em `wear/`). Antes: Modo Sol aplicado à tela inteira (`0.6.1`), CV2 completo com layouts fluidos, Home ao vivo e WCAG 2.2 (`0.6.0`), e o CV1 com salas por PIN, papéis, regras configuráveis e linha do tempo auditável.

Próximo trabalho: fechar a `CV6.DS2.US1`, já validada no relógio real, e implementar a `CV6.DS2.US2`, aro de conexão discreto. A `CV3.DS1.US4` continua como pendência independente.

O ciclo CV6 também entregou no relógio números maiores com Teko local, batimentos centralizados, **Voltar Ponto** e **Nova** verde em dois toques (`CV6.DS2.US1`, versão 0.20.1). A próxima HU é o aro discreto de conexão.

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
