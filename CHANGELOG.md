# Changelog

Este changelog registra tanto o **trabalho ativo em andamento** (para coordenação multi-agente e handoff) quanto as **versões fechadas**.

A seção `## [Em Andamento]` no topo do arquivo rastreia todas as branches ativas geradas a partir da branch principal (`main`/`master`). Todo novo desenvolvimento deve ser registrado aqui com a branch, a história, o passo atual do ciclo Ariad, a assinatura do agente responsável e notas de handoff.

Quando uma história é validada e integrada na `main`, seu registro é removido de `[Em Andamento]` e incorporado à versão fechada correspondente.

## [Em Andamento]

### feature/cv2-ds1-blindagem-e-confiabilidade
- **História / Escopo**: CV2.DS1 — Blindagem e Confiabilidade do Placar (remoção de `codigo_mestre` do WS [C1], proteção contra fantasmas e lotação [C2], prevenção e feedback visual contra toques perdidos no +1 [C3] e normalização de erros 422 [A7])
- **Branch**: `feature/cv2-ds1-blindagem-e-confiabilidade`
- **Passo Ariad**: Passo 2 - Planejamento
- **Assinatura do Agente**: Agente: Antigravity (Driver) | Sessão: c99eaae7-a2c8-4084-8884-819f5cc9e494 | Data: 2026-09-15 17:45
- **Handoff / Próximos Passos**: Checkpoint 1 apresentado ao Navigator. Aguardando aprovação para iniciar a implementação no backend e frontend.

## 0.4.2 - 2026-09-15

Boundary: patch (faxina técnica: pagamento do débito debt-arenas-legadas, remoção de fixtures e garantia de banco limpo no versionamento)

Authors: Eli (Navigator); Antigravity (Driver)

Git source: tech/faxina-arenas-fixtures-e-banco-limpo (merge into master)

### Added

- [Faxina] Suíte de testes automatizados em `tests/test_banco_limpo_versao.py` validando que o SQLite inicializa com 0 quadras no startup e no versionamento, além de verificar rejeição com 404 em rotas obsoletas.

### Changed

- [Faxina] `init_db_sync` em `app/db.py`: recriação limpa e estéril garantida na subida de nova versão sem re-popular quadras pré-existentes.
- [Faxina] Blindagem de rotas no FastAPI (`app/main.py`): requisições a rotas não mapeadas sob o prefixo `/api/*` agora retornam `HTTP 404 Not Found` em vez de serem capturadas indevidamente pelo fallback de HTML da SPA.
- [Faxina] Bump de versão para `0.4.2` em `pyproject.toml`, `app/config.py` e `web/package.json`.
- [Débito] Encerramento e quitação de `debt-arenas-legadas` em `docs/project/debt/items/2026-09-14T1625Z-endpoints-legados-de-arenas.md`.

### Removed

- [Faxina] Exclusão completa do módulo de auto-seeding `app/fixtures.py` e do arquivo `fixtures/defaultArenas.json`.
- [Faxina] Exclusão da tabela `arenas`, coluna `arena_id` e índice `idx_quadras_arena` do SQLite em `SCHEMA_SQL`.
- [Faxina] Exclusão dos endpoints legados `/api/arenas`, `/api/arenas/{id}`, `/api/arenas/{id}/quadras` e modelo `CriarArenaBody` em `app/api.py`.
- [Faxina] Exclusão das funções auxiliares de arenas em `app/quadras.py` (`criar_arena_sync`, `listar_arenas_sync`, `obter_arena_sync`).
- [Faxina] Exclusão de componentes órfãos no frontend em `web/src/components/` (`ModalCriarArena.svelte`, `ListaArenas.svelte`, `ListaQuadras.svelte`).
- [Faxina] Remoção da cópia de fixtures no `Dockerfile` multi-estágio.

## 0.4.1 - 2026-09-15

Boundary: patch (entrega de CV1.DS2.TS1: endpoint de owner e proteção contra força bruta)

Authors: Eli (Navigator); Antigravity (Driver)

Git source: feature/cv1-ds2-ts1-endpoint-owner-rate-limit (merge into master)

### Added

- [TS1] Geração de código mestre criptograficamente seguro de 4 dígitos (`0000` a `9999`) persistido na criação de cada sala (`POST /api/quadras`).
- [TS1] Coluna `codigo_mestre TEXT` na tabela `quadras` em `SCHEMA_SQL` e migração idempotente no SQLite (`init_db_sync`).
- [TS1] Blindagem e sigilo: rotas públicas da API e WebSockets nunca retornam a coluna `codigo_mestre`.
- [TS1] Classe thread-safe `RateLimiter` em `app/rate_limit.py` implementando janela deslizante de 10 min, limite de 5 falhas e bloqueio progressivo de 5 min (`Retry-After: 300`).
- [TS1] Endpoint administrativo autenticado `GET /api/owner/quadras` (e atalho `GET /owner/quadras`) via header `Authorization: Bearer <segredo>` ou query param `?secret=<segredo>` usando comparação em tempo constante (`secrets.compare_digest`).
- [TS1] Camuflagem de segurança: requisições não autorizadas ou com segredo inválido retornam `HTTP 404 Not Found` em vez de 401, ocultando a rota contra scanners de rede.
- [TS1] Suíte de testes automatizados em `tests/test_owner_endpoint.py` com 7 testes cobrindo autenticação, rate limiting por IP, bloqueio progressivo e isolamento de dados.

## 0.4.0 - 2026-09-15

Boundary: minor (entrega de CV1.DS3.US1 e encerramento da Delivery Story CV1.DS3: regras da partida configuráveis pela quadra)

Authors: Eli (Navigator); Antigravity (Driver)

Git source: feature/cv1-ds3-us1-configurar-regras-da-partida (merge into master)

### Added

- [US1] Seção "Regras da Partida" no formulário de criação de salas com seleção de pontuação-alvo via botões de 1 toque (12, 15, 21, 25) e valor personalizado (1 a 100).
- [US1] Configuração de exigência de vantagem de 2 pontos (liga/desliga) e teto máximo de pontuação opcional.
- [US1] Validação preventiva no frontend e estrita no backend (HTTP 422) impedindo configuração de teto menor que a pontuação-alvo.
- [US1] Persistência auditável de `alvo`, `vantagem` e `teto` no payload do evento `PARTIDA_INICIADA` e na narrativa inicial da Linha do Tempo.
- [US1] Badge de destaque no cabeçalho da quadra em `SalaQuadra.svelte` exibindo as regras ativas da sala para todos os participantes.
- [US1] Suporte a vitória por alcance do teto máximo (mesmo com diferença de 1 ponto) e vitória direta no alvo quando a vantagem está desabilitada.
- [US1] Preservação automática das regras configuradas em partidas consecutivas na mesma sala (`POST /reiniciar`).
- [US1] Suíte de testes automatizados em `tests/test_configurar_regras.py` cobrindo cenários de presets, encerramento por teto, sem vantagem, rejeição de teto inválido e reinício.

## 0.3.3 - 2026-09-15

Boundary: patch (entrega de CV1.DS2.US2: sucessão automática de admin após 2 minutos de ausência)

Authors: Eli (Navigator); Antigravity (Driver)

Git source: feature/cv1-ds2-us2-sucessao-automatica-de-admin (merge into master)

### Added

- [US2] Rastreio de presença e ausência com atualização de `ultimo_visto_em` no banco em eventos de conexão e desconexão de WebSocket.
- [US2] Rotina periódica em background no lifespan do FastAPI para checagem contínua de tolerância de ausência do administrador (`settings.admin_timeout_seconds`, padrão 120s).
- [US2] Eleição determinística do controlador online mais antigo (`criado_em ASC`) como novo administrador da sala.
- [US2] Rebaixamento atômico e seguro do admin ausente para `CONTROLADOR`, garantindo que ao reconectar não recupere o posto sem autorização.
- [US2] Gravação do evento auditável `ADMIN_SUCEDIDO` e projeção narrativa na Linha do Tempo da partida.
- [US2] Suporte a estado degradado sem admin online (posto vago), mantendo a capacidade dos controladores de pontuar e desfazer pontos normalmente.
- [US2] Suíte de testes automatizados em `tests/test_sucessao_admin.py` cobrindo antiguidade, reconexão de ex-admin, tolerância e propagação via WebSocket.

## 0.3.2 - 2026-09-14

Boundary: patch (entrega de CV1.DS3.US2: jogadores das equipes e inversão local de lados)

Authors: Eli (Navigator); Antigravity (Driver)

Git source: feature/cv1-ds3-us2-jogadores-das-equipes-e-inversao-de-lados (merge into master)

### Added

- [US2] Formulário de criação de placar com definição de jogadores (Jogador 1 obrigatório e Jogador 2 opcional para cada time) e formatação automática de duplas ou individuais.
- [US2] Suporte no event store e projeção para `jogadores_a` e `jogadores_b`, refletindo os nomes reais dos atletas nos botões de marcação (+1), banners de vitória e registros da linha do tempo.
- [US2] Botão "⇄ Inverter Lados" nos modos controlador e espectador, permutando instantaneamente as colunas e botões via CSS Grid.
- [US2] Persistência desacoplada em `localStorage` por ID de sala (`placar:lados_invertidos:<quadraId>`), mantendo a inversão estritamente local em cada navegador sem alterar a visão dos demais participantes.
- [US2] Suporte a novos nomes de jogadores ou preservação automática dos times anteriores no reinício de partidas (`POST /api/quadras/{id}/reiniciar`).
- [US2] Suíte de testes automatizados em `tests/test_jogadores_e_inversao.py` cobrindo jogadores individuais, duplas, linha do tempo e reinício com persistência de times.

## 0.3.1 - 2026-09-14

Boundary: patch (entrega de CV1.DS2.US1: controle e permissões de quadra com promoção e revogação de controladores)

Authors: Eli (Navigator); Antigravity (Driver)

Git source: feature/cv1-ds2-us1-promover-e-revogar-controladores (merge into master)

### Added

- [US1] Suporte completo ao papel de `CONTROLADOR` no motor de comandos, permitindo marcação e anulação de pontos e disputa de controle ativo.
- [US1] Endpoints REST `POST /api/quadras/{id}/participantes/{alvo_id}/promover` e `.../revogar` (e `/papel` genérico) restritos exclusivamente ao `ADMIN`.
- [US1] Transferência automática de turno ao promover controlador (permitindo pontuação imediata sem recarregar a tela ou cliques adicionais) e retorno seguro ao admin na revogação.
- [US1] Proteção rigorosa no servidor contra requisições forjadas: espectadores recebem HTTP 403 ao tentar pontuar, anular pontos ou assumir o controle.
- [US1] Interface reativa em Svelte 5: botões "Tornar controlador" e "Revogar controlador" visíveis apenas para o Admin; badges estilizados para `ADMIN`, `CONTROLADOR` e `ESPECTADOR`.
- [US1] Suíte de testes automatizados em `tests/test_promover_revogar_controladores.py` cobrindo ciclos de permissão, concorrência e eventos via WebSocket.

### Changed

- Projeção de `PAPEL_ALTERADO` na Linha do Tempo detalha quem promoveu ou revogou cada participante.
- Bump de versão para `0.3.1` em `pyproject.toml` e `app/config.py`.
- Roadmap e README atualizados refletindo `CV1.DS2` como ativa e `US1` como concluída.

## 0.3.0 - 2026-09-14

Boundary: minor (conclusão da CV1.DS1 - Núcleo da Partida: pontuação, rotação de saque, desfecho/encerramento e reinício sob demanda)

Authors: Eli (Navigator); Antigravity (Driver)

Git source: feature/cv1-ds1-us4-encerramento-e-reinicio (merge into master)

### Added

- [US4] Encerramento formal da partida ao atingir a condição de vitória (mínimo de 12 pontos com 2 de vantagem, ou teto em 15 pontos).
- [US4] Registro do evento `PARTIDA_ENCERRADA` no log da partida e atualização do status para `'ENCERRADA'`.
- [US4] Bloqueio de pontuações na interface ao encerrar a partida, exibindo banner com time vencedor e destaque do placar final.
- [US4] Botão **"▶ Iniciar Nova Partida"** exibido exclusivamente para o criador/admin da sala após a vitória.
- [US4] Endpoint REST `POST /api/quadras/{quadra_id}/reiniciar` para zerar o placar mantendo a mesma sala, código PIN e participantes conectados via WebSocket.
- [US4] Mensagem contextual de espera para espectadores durante o término da partida ("Aguardando o administrador iniciar uma nova partida...").
- [US4] Possibilidade de desfazer o ponto de vitória pelo admin, retornando o status da partida para `'EM_ANDAMENTO'`.
- [US4] Suíte de testes automatizados em `tests/test_encerramento_e_reinicio.py` (6 cenários cobrindo vantagem, teto, reversão e WebSocket).

### Changed

- `snapshot` e `obter_quadra_sync` ajustados para carregar a partida mais recente por data de criação (`criado_em DESC`), permitindo visualização e continuidade após encerramento.
- Keepalive do WebSocket em `app/main.py` preserva conexões ativas na mesma quadra na transição para uma nova partida.
- Bump de versão para `0.3.0` em `pyproject.toml` e `app/config.py`.
- Roadmap e README atualizados refletindo a conclusão da Delivery Story `CV1.DS1`.

## 0.2.1 - 2026-09-14

Boundary: patch (governança Ariad: branches por história, tracking ativo no changelog, assinatura de agentes e sync remoto)

Authors: Eli (Navigator); Antigravity (Driver)

Git source: chore/ariad-multi-agent-branching-and-changelog (merge into master)

### Added

- Seção `## [Em Andamento]` no topo de `CHANGELOG.md` para monitoramento ativo de branches, passos do ciclo Ariad e notas de handoff.
- Assinatura obrigatória de agentes (`Agente: <Nome> (Driver) | Conversa: <ID> | Data: YYYY-MM-DD HH:mm`) no changelog e commits.
- Política de push remoto contínuo da branch de trabalho (`git push -u origin <branch>`) a cada checkpoint para proteção contra congelamento por esgotamento de créditos.

### Changed

- Princípios e regras do Ariad em `AGENTS.md` e `docs/process/development-guide.md` atualizados: mandatório criar branch a partir de `main`/`master` para qualquer novo desenvolvimento; commits diretos no tronco são proibidos.
- Registro formal de decisão arquitetural no ADR `2026-09-14T1710Z-branches-por-historia-registro-changelog-e-assinatura-de-agentes.md`.

## 0.2.0 - 2026-09-14

Boundary: minor (simplificação de arquitetura: salas por código PIN de 5 dígitos e SQLite efêmero)

Authors: Eli (Navigator); Antigravity (Driver)

Git source: master

### Added

- Entrada simplificada com tela inicial direta oferecendo "Criar Placar" e "Acompanhar".
- Geração aleatória de código PIN de 5 dígitos (10000 a 99999) por sala.
- Atribuição imediata do papel de ADMIN para o criador da sala e ESPECTADOR para ingressantes via código.
- Limite de capacidade para proteção da instância: máximo de 20 salas simultâneas e 20 participantes por sala.
- Expiração e limpeza automática em cascata de salas inativas por mais de 1 hora (TTL de 3600s), com rotina periódica no lifespan do FastAPI.
- Banner destacado com o código da sala e botão de cópia com um clique no topo da sala.
- Tabela `app_meta` no SQLite para detecção de versão e recriação limpa automática ao atualizar a aplicação.

### Changed

- Remoção de volume persistente do SQLite em `docker-compose.yml` e `Dockerfile`, garantindo banco limpo a cada novo deploy.
- Bump de versão para 0.2.0 em `pyproject.toml`, `app/config.py` e `app/main.py`.
- Precedência de cabeçalho `x-session-id` sobre cookies em todos os endpoints REST.

## Templates

### Template de Trabalho em Andamento (Em Andamento)
```markdown
### <nome-da-branch>
- **História / Escopo**: <Código da história e resumo do objetivo>
- **Branch**: `<nome-da-branch>`
- **Passo Ariad**: Passo <N> - <Nome do Passo> (ex: Passo 3 - Implementação)
- **Assinatura do Agente**: Agente: <Nome> (Driver) | Sessão: <ID> | Data: YYYY-MM-DD HH:mm
- **Handoff / Próximos Passos**: <O que já foi feito e o que o próximo agente deve executar>
```

### Template de Versão Fechada
```markdown
## X.Y.Z - YYYY-MM-DD

Boundary: patch | minor | major | project-specific boundary

Authors: Person Name; Agent or Runtime Name

Git source: tag, commit range, pull request, or merge commit

### Added

- ...

### Changed

- ...

### Fixed

- ...

### Removed

- ...
```
