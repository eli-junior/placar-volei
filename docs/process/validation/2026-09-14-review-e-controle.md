# Checkpoint 2 — Correções da revisão e controle exclusivo

Estado: implementado, aguardando validação do Navigator. Versão pretendida: 0.3.0; release ainda não aceita. Sem commit ou push.

## Comportamento entregue

- ID público aleatório, sem credencial. Sessão privada armazenada por hash e cookie novo `placar_session_v3`; cookies da 0.2 não são reutilizados. A troca de versão segue a política já aprovada de recriar o banco.
- Criador começa como admin e operador. Admins autorizam participantes como admins. Apenas um participante controla os pontos e desfazimentos. Outro admin pode assumir imediatamente.
- Trocas de controle e autorizações aparecem no histórico e nos clientes conectados. Um número de mandato (`controle_versao`) invalida requisições antigas, inclusive se o mesmo admin recuperar o controle depois.
- Leitura, autorização e gravação em uma transação SQLite. Snapshots levam sequência; respostas atrasadas não regridem o frontend.
- URLs de arquivos não escapam da pasta pública; sala expirada é comunicada explicitamente, sem um falso placar 0 × 0.
- Criação concorrente respeita capacidade. Fixtures sem espaço são adiadas no startup. Erro de gravação da fixture devolve 503 e reverte a criação no banco.
- Docker usa 20 participantes e monta o diretório `fixtures/`, permitindo substituição atômica do JSON.
- `npm run check` configurado; feedback novo e histórico respeitam movimento reduzido.

## Evidência automatizada

Executado em Windows com Python 3.12:

```powershell
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
npm --prefix web run check
npm --prefix web test
npm --prefix web run build
docker compose config --format json
```

- Backend: 65 testes aprovados, 2 avisos de depreciação do TestClient/AnyIO.
- Frontend: 2 testes aprovados para descarte de resposta atrasada e de resposta de outra partida.
- Svelte: zero erros e zero avisos; build aprovado.
- Ruff: aprovado.
- Compose renderizado: limite efetivo de 20, fixture em `/srv/fixtures/defaultArenas.json`, montagem de diretório.
- Regressões cobrem exposição de sessão, cookie legado, traversal, transferência, exclusividade, mandato antigo, concorrência de pontos/desfazimentos/vitória, capacidade, expiração, restart e rollback de fixture.

Conferência no navegador: três sessões distintas na mesma instância; promoção de Admin B, transferência A → B, retirada dos botões de A, ponto propagado ao espectador e registro no histórico. Processo reiniciado, reconexão automática e controle de B/placar preservados; desfazimento sincronizado.

## Rota de validação do Navigator

### Preparação local

Na raiz do projeto, compile e inicie uma instância de teste separada do banco habitual:

```powershell
npm --prefix web run build
$env:DB_PATH = Join-Path $env:TEMP 'placar-aceite-030.db'
$env:DEFAULT_ARENAS_FILE = ''
uv run uvicorn app.main:app --host 0.0.0.0 --port 8013
```

Uma instância de validação foi deixada em `http://127.0.0.1:8013`, usando `%TEMP%/placar-review-validacao-030.db`. Se ainda estiver ativa, use-a diretamente. Não execute dois processos na mesma porta.

Abra três contextos com cookies separados: navegador comum, outro navegador/anônimo e um celular real. No celular, use `http://IP-DO-PC:8013`, na mesma rede, com a porta acessível. Três abas comuns do mesmo navegador compartilham identidade e não servem para este cenário.

### Controle e auditoria

1. Cliente A cria uma sala como **Admin A**. B e C entram pelo PIN como **Admin B** e **Espectador C**. A deve ver os botões de ponto/desfazer e `Controle: Admin A`; B e C acompanham.
2. A usa **Tornar admin** na linha de B. Sem recarregar, B deve ver **Assumir o controle**, mas nenhum botão de ponto. C continua espectador.
3. B assume. A perde os botões de ponto, B recebe os botões e os três veem `Controle: Admin B`. Observe a transição curta do nome. A linha do tempo registra quem autorizou B e quem assumiu.
4. B marca A, depois B e desfaz. Nas três telas, espere **1 × 0**, com três eventos e a anulação identificada. A não pode marcar até assumir novamente. C nunca recebe botões de controle.
5. A assume de volta. B perde os botões, A os recebe. Confira a nova transferência no histórico.

Aprova: um operador por vez, placar e histórico coerentes nas três telas, mudanças sem F5. Falha: dois operadores com ações aceitas, espectador autorizado a operar ou divergência persistente entre telas.

### Chamada forjada e requisição antiga

No console do navegador de C, substitua `PIN`:

```javascript
const q = await (await fetch('/api/quadras/PIN')).json();
const r = await fetch('/api/quadras/PIN/pontos', {
  method: 'POST',
  headers: {'Content-Type': 'application/json', 'x-control-version': String(q.controle_versao)},
  body: JSON.stringify({equipe: 'A'})
});
console.log(r.status); // 403
```

No console do admin que tem o controle, repita usando `x-control-version: '-1'`: deve retornar **409**, sem alteração do placar. Sem esse cabeçalho, deve retornar **428**. IDs da lista de participantes usados como `x-session-id` devem resultar em **403**.

### Reconexão, restart e acessibilidade

1. Com B no controle, desconecte B por cerca de 30 segundos. Enquanto isso, A assume e marca um ponto. Ao reconectar, B deve receber o placar atual e permanecer sem o controle.
2. Anote placar e operador. Pare o servidor de teste com Ctrl+C e execute o mesmo comando novamente, com o mesmo `DB_PATH`. Os clientes devem reconectar sem reentrada e recuperar placar, operador e histórico.
3. Ative `prefers-reduced-motion` no navegador e repita transferência/ponto/desfazer. A informação deve permanecer legível sem o movimento. No celular real, confira alvos de toque, retrato, paisagem e giro do espectador.

Aprova: reconciliação automática, nenhuma volta indevida de controle, estado preservado após restart e leitura clara no celular. Falha: precisar entrar novamente após simples restart, regredir pontuação ou recuperar controle automaticamente após outro admin assumir.

### Expiração acelerada em instância separada

Inicie outro terminal com:

```powershell
$env:DB_PATH = Join-Path $env:TEMP 'placar-expiracao-030.db'
$env:DEFAULT_ARENAS_FILE = ''
$env:QUADRA_TTL_SECONDS = '15'
uv run uvicorn app.main:app --host 127.0.0.1 --port 8014
```

Crie sala em `http://127.0.0.1:8014`, marque um ponto e aguarde cerca de 20 segundos sem ações. Deve voltar ao início com mensagem de expiração. A URL antiga também deve informar indisponibilidade. Falha: mostrar 0 × 0 como se a partida ainda estivesse válida ou continuar tentando reconectar indefinidamente.

### Docker / Mini PC

O daemon Docker local não respondeu, mesmo após tentativa de iniciar Docker Desktop. Build e execução do contêiner **ainda precisam ser validados**. Faça esta verificação em ambiente de teste, pois nova versão descarta o banco anterior pela política do projeto.

O arquivo agora é `fixtures/defaultArenas.json`. Se houver `DEFAULT_ARENAS_FILE` personalizado no ambiente local, ajuste-o. No host Linux, o diretório montado precisa permitir escrita pelo UID 1001 do contêiner. Na raiz do checkout de teste:

```bash
sudo chown -R 1001:1001 ./fixtures
docker compose up -d --build
docker compose ps
docker compose logs --tail 50
```

Valide `/health`, criação/entrada e troca de controle. Para a gravação legada, crie uma arena via `POST /api/arenas` com `{"nome":"Arena de aceite"}` e uma quadra via `POST /api/arenas/ID/quadras` com `{"nome":"Quadra de aceite"}`. O JSON em `fixtures/` deve refletir as criações; ambas devem retornar 201 sem erro de ponto de montagem. Reinicie com `docker compose restart`: o serviço deve voltar saudável e a partida/controle ativos devem permanecer.

Falha: erro de permissão/rename, 500/503 na criação em condições normais, startup interrompido por capacidade ou perda de partida após simples restart.

## Arquivos da implementação

- Backend alterado: `app/api.py`, `app/config.py`, `app/db.py`, `app/eventos.py`, `app/fixtures.py`, `app/main.py`, `app/projecao.py`, `app/quadras.py`.
- Backend novo: `app/comandos.py`, `app/identidade.py`.
- Frontend alterado: `web/src/App.svelte`, `web/src/components/SalaQuadra.svelte`, `ListaPresentes.svelte`, `ListaArenas.svelte`, `LinhaDoTempo.svelte`, `Placar.svelte`, `PlacarManual.svelte`.
- Frontend novo: `web/src/sync.js`, `web/svelte.config.js`, `web/tests/sync.test.js`.
- Testes alterados: `tests/conftest.py`, `test_desfazer.py`, `test_fixtures.py`, `test_linha_do_tempo.py`, `test_pontos.py`, `test_quadras_e_participantes.py`.
- Teste novo: `tests/test_review_regressions.py`.
- Empacotamento: `Dockerfile`, `docker-compose.yml`, `pyproject.toml`, `uv.lock`, `web/package.json`, `web/package-lock.json`.
- Fixture movida: `defaultArenas.json` → `fixtures/defaultArenas.json`.
- Este roteiro de validação.

## Pendências para os próximos checkpoints

- Aguardar validação manual do Navigator, incluindo celular real e Docker.
- No Checkpoint 3: avaliar refatoração, dívida e documentação antes do fechamento.
- Atualizar README, briefing, princípios, guia de desenvolvimento, decisão sobre controle e roadmap de permissões/fixtures. Revisar a decisão anterior de sucessão à luz de múltiplos admins; sucessão automática e owner continuam fora desta entrega.
- Só após aceite da release: preparar changelog a partir do diff e histórico, consolidar versão e propor commit em português. Nenhum push autorizado.
- Achado adicional: `npm audit` informa 4 ocorrências na cadeia de desenvolvimento do Vite antigo (1 alta, 3 moderadas). A correção sugerida envolve versões principais de Vite/plugin; registrar trabalho de atualização separado. Esses pacotes não fazem parte do runtime Python da imagem final.
