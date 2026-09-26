# Changelog

Este changelog registra tanto o **trabalho ativo em andamento** (para coordenação multi-agente e handoff) quanto as **versões fechadas**.

## [Em Andamento]

Nenhum trabalho ativo.

## 0.12.0 - 2026-09-26

Boundary: minor (nova capacidade no relógio: nova partida rápida ao fim da partida; fecha o CV3.DS2)

Authors: Eli (Navigator); Claude Opus 5.5 (Driver) | Sessão: 53afbbcf

Git source: feature/cv3-ds2-us3-nova-partida-rapida-no-relogio (merge 7d1dd89 into master)

### Added

- [Relógio] **Nova partida rápida** (`CV3.DS2.US3`): com a partida encerrada, a faixa inferior vira **↶ Desfazer | ▶ Nova**. Um toque começa a próxima partida em 0 × 0, com os mesmos times, jogadores, alvo, vantagem e teto. Só com conexão e fila vazia.
- API: `acao: "nova_partida"` em `POST /api/watch/comandos` (reusa o `reiniciar`, com recibo idempotente) e `pode_nova_partida` em `GET /api/watch/session`.

### Decisions

- `nova-partida-pelo-relogio-de-admin`.

### Debt

- Novo: `debt-erro-de-entrada-pela-home-fora-da-vista` (relato do Navigator; anotado para depois).
- Riscos anotados na US3: recusa sem aviso no relógio; `pode_nova_partida` lido ao entrar na quadra.

### Verification

- `pytest` 185/185, `ruff check` e `ruff format --check` ok; Android: 36 testes, `assembleDebug` e `lintDebug` (JDK 21).
- Teste físico no Galaxy Watch 8 aprovado pelo Navigator.

## 0.11.0 - 2026-09-26

Boundary: minor (nova capacidade no relógio: batimento no placar durante o treino do Samsung Health; fecha o CV3.DS2)

Authors: Eli (Navigator); Claude Opus 5.5 (Driver) | Sessão: c5f8bb01

Git source: feature/cv3-ds2-us2-frequencia-cardiaca-no-placar (merge 296e847 into master)

### Added

- [Relógio] **Batimento no placar** (`CV3.DS2.US2`): `♥ bpm` ao lado da bolinha de conexão, lido pelo `MeasureClient` do Health Services só com o placar visível. O Samsung Health continua gravando o treino. Sem leitura, `♥ --`; sem permissão, o placar fica como era. O valor não sai do relógio.

### Decisions

- `batimento-no-relogio-por-measureclient`.

### Debt

- Nenhum item novo. Riscos anotados na US2: só `BODY_SENSORS` é pedido em tempo de execução; bateria com tela acesa e sensor ligado não medida.

### Verification

- Android: 36 testes e `assembleDebug` (JDK 21).
- Teste físico no Galaxy Watch 8 com treino do Samsung Health ativo aprovado pelo Navigator.

## 0.10.1 - 2026-09-26

Boundary: patch (ajuste de ergonomia no relógio: o placar mantém a tela acesa; primeira entrega do CV3.DS2)

Authors: Eli (Navigator); Claude Opus 5.5 (Driver) | Sessão: c5f8bb01

Git source: feature/cv3-ds2-us1-tela-acesa-no-placar (merge into master)

### Changed

- [Relógio] **Tela acesa no placar** (`CV3.DS2.US1`): enquanto o placar está visível, a tela não apaga sozinha e o toque marca sem acordar o relógio. Vínculo e escolha seguem o tempo normal de tela; cobrir com a palma ainda apaga.

### Fixed

- [Build] `.gitattributes` fixa LF em `gradlew` e `*.sh`: o checkout do Windows (`core.autocrlf=true`) quebrava `./wear/gradlew` no WSL.

### Decisions

- `tela-acesa-no-placar-do-relogio`: substitui a decisão 3 do plano do CV3.DS1 ("não manter tela permanentemente acesa por padrão").

### Debt

- Nenhum item novo. Medição de bateria com o placar aceso fica em aberto na US1.

### Verification

- Android: 33 testes, `assembleDebug` e `lintDebug` (0 erros), com o `./wear/gradlew` do checkout rodando no WSL; `pytest` 178/178, `ruff check` e `ruff format --check` ok.
- Teste físico no Galaxy Watch 8 aprovado pelo Navigator; bateria não medida.

## 0.10.0 - 2026-09-23

Boundary: minor (nova capacidade: retomar ou trocar de quadra pelo Galaxy Watch, um vínculo por vez; quarta entrega do CV3)

Authors: Eli (Navigator); Claude Opus 5.5 (Driver) | Sessão: 060492ed

Git source: feature/cv3-ds1-us5-um-vinculo-por-vez (merge into master)

### Added

- [Relógio] **Retornar ou parear outra quadra** (`CV3.DS1.US5`): ao reabrir o app, o botão **Retornar** (com o nome da quadra) ou a faixa **Parear outra quadra**. O relógio fica em uma quadra por vez.
- [Relógio] Aviso antes de trocar com lances pendentes ("2 lances marcados em q1 ainda não foram enviados…"), com **Parear mesmo assim**; nada é descartado se o código não for aprovado.
- API: `substitui` em `POST /api/watch/pairing` (`watch_devices.substitui_id`, migração aditiva); a aprovação revoga o vínculo antigo e devolve o controle na quadra anterior ("relógio foi para outra quadra"). `DELETE /api/watch/pairing` cancela o código ao desistir. `court_name` em `GET /api/watch/session`.

### Changed

- [Relógio] Telas de vínculo no padrão do placar: conteúdo no centro e ação na faixa inferior. Sem vínculo, uma bola quicando e **Ingressar numa quadra**; o código vem com a dica de onde aprová-lo no telefone.
- [Relógio] Nada pisca enquanto o relógio consulta o servidor: a bola fica até a resposta, na abertura e depois de **Retornar**.

### Decisions

- `um-vinculo-por-vez-troca-na-aprovacao`.

### Debt

- `debt-fluxos-da-interface-sem-teste-de-ponta-a-ponta` (Carried, atualizado com o relógio).
- `debt-banco-de-producao-sem-volume-persistente`, `debt-limite-de-vinculo-do-relogio-por-ip-e-em-memoria` e `debt-regra-de-vitoria-duplicada-no-relogio` (Carried).

### Verification

- `pytest` 178/178, `ruff check` e `ruff format --check` ok; web `npm test` 27/27, `npm run check` sem erros/avisos, `npm run build` ok; Android: 33 testes, `assembleDebug` e `lintDebug` (0 erros) ok.
- Dois testes físicos no Galaxy Watch 8 em produção, na branch da HU, aprovados pelo Navigator, incluindo a troca entre duas quadras e o controle.

## 0.9.0 - 2026-09-23

Boundary: minor (nova capacidade: desfazer pontos pelo Galaxy Watch, terceira entrega do CV3)

Authors: Eli (Navigator); Claude Opus 5.5 (Driver) | Sessão: 37fec51a

Git source: feature/cv3-ds1-us3-desfazer (merge into master)

### Added

- [Relógio] **Desfazer no pulso** (`CV3.DS1.US3`): a faixa **↶ Desfazer**, embaixo, corrige o último ponto que o relógio mostra, com vibração própria e o número descendo. Funciona sem rede e antes do envio: ponto e desfazer saem em ordem e aparecem os dois na linha do tempo. Continua ativa na vitória, para reabrir a partida.
- [Relógio] **Bolinha de conexão** no alto: verde conectado, amarela enviando ou reconectando, vermelha sem conexão, com o número de lances pendentes.
- API: `acao: "desfazer"` em `POST /api/watch/comandos`, com `alvo_seq` (ponto confirmado) ou `alvo_comando` (lance da fila). Só desfaz se o alvo ainda for o último ponto ativo; senão recusa sem tocar em outro ponto. O alvo entra no recibo (`watch_recibos.alvo`, migração aditiva) e na idempotência.
- `estado_partida.equipes_ativas`: a equipe de cada ponto ativo, para o relógio prever o placar.

### Changed

- [Relógio] A tela de vínculo mostra só **Gerar código**: o endereço do servidor fica fixo no APK (`-PserverUrl` na compilação).
- [Relógio] Sem o controle, a faixa de desfazer some e o aviso "Controle no telefone…" fica embaixo, fora dos números.

### Decisions

- `desfazer-do-relogio-com-alvo-explicito-e-registro-antes-do-envio`: o relógio atrasado nunca desfaz um ponto que não viu; o toque acidental corrigido offline fica registrado.

### Debt

- `debt-regra-de-vitoria-duplicada-no-relogio` (Carried, atualizado): o relógio também prevê a pilha de pontos.
- `debt-fluxos-da-interface-sem-teste-de-ponta-a-ponta`, `debt-banco-de-producao-sem-volume-persistente` e `debt-limite-de-vinculo-do-relogio-por-ip-e-em-memoria` (Carried).

### Roadmap

- Nova `CV3.DS1.US5` (Planned, próxima): retomar ou trocar de quadra ao abrir o app, com o relógio vinculado a uma quadra por vez.

### Verification

- `pytest` 166/166, `ruff check` e `ruff format --check` ok; web `npm test` 27/27, `npm run check` sem erros/avisos, `npm run build` ok; Android: 26 testes, `assembleDebug` e `lintDebug` (0 erros) ok.
- Validação física no Galaxy Watch 8 em produção, na branch da HU, aprovada pelo Navigator, incluindo os ajustes de tela pedidos no teste.

## 0.8.0 - 2026-09-23

Boundary: minor (nova capacidade: marcar pontos pelo Galaxy Watch com controle delegado, segunda entrega do CV3)

Authors: Eli (Navigator); Claude Opus 5.5 (Driver)

Git source: feature/cv3-ds1-us2-ver-e-marcar (merge into master)

### Added

- [Relógio] **Placar no pulso** (`CV3.DS1.US2`): duas metades grandes, **Nós** (equipe A) e **Eles** (equipe B), ou as iniciais dos jogadores (EC × RM). O toque é gravado no relógio antes de vibrar; o placar previsto aparece diferente do confirmado, com "N pendentes". Lances saem em ordem, e sem rede ficam na fila (com o app aberto).
- [Relógio] **Participante "Eli (Relógio)"**: ao aprovar o código, o relógio entra na sala como participante próprio. O admin o torna controlador e usa **Passar controle**; quem tem o controle pontua.
- API: `POST /api/watch/comandos`, com recibo durável (`watch_recibos`) na mesma transação do evento. Reenvio não duplica ponto; recusas também geram recibo; lance de partida anterior nunca vale para a atual.
- [Site] Botão **Passar controle** na lista de presentes (a rota existia desde a CV2.DS2.US5, sem botão) e marcação de quem está no controle.
- [Site] Ícone de relógio no cabeçalho; quem não é Eli vê "Em breve…".

### Changed

- `eli`, `ELI` ou `Eli` entram como `Eli` e já habilitam o relógio (`WATCH_AUTO_GRANT=eli`). O apelido-senha `eli.relogio` deixa de existir.
- O controle nas mãos do relógio não volta ao admin por ausência (a tela apaga durante o jogo); o admin retoma com "Assumir o controle".
- O relógio conectado conta como presença do dono para a sucessão de admin.
- Revogar o relógio remove o Eli (Relógio) da sala e devolve o controle ao dono.

### Fixed

- [Site] A engrenagem das configurações aparecia vazia desde a CV2: o ícone `engrenagem` não existia no conjunto. Novo teste confere todo ícone usado nas telas.

### Decisions

- `relogio-como-participante-com-controle-delegado`, que substitui `apelido-senha-habilita-relogio` e a decisão 1 do plano da DS1. Redirecionamento do Navigator durante o teste físico; a chave "Controlar pelo Relógio" da revisão 2 foi implementada e removida.

### Debt

- `debt-fluxos-da-interface-sem-teste-de-ponta-a-ponta` (New, Carried).
- `debt-regra-de-vitoria-duplicada-no-relogio` (New, Carried).
- `debt-limite-de-vinculo-do-relogio-por-ip-e-em-memoria` e `debt-banco-de-producao-sem-volume-persistente` (Carried).

### Verification

- `pytest` 151/151, `ruff check` e `ruff format --check` ok; web `npm test` 27/27, `npm run check` sem erros/avisos, `npm run build` ok; Android: 18 testes, `assembleDebug` e `lintDebug` ok.
- Validação física no Galaxy Watch 8 (44 mm) em produção aprovada pelo Navigator: vínculo com `eli`, Eli (Relógio) na sala, controle delegado e pontuação pelo relógio. Fila em modo avião, tela apagada, telefone bloqueado, recusa com descarte, fim de partida, revogação e ergonomia não foram confirmados um a um no aparelho; os casos de servidor têm teste automatizado.

## 0.7.0 - 2026-09-23

Boundary: minor (nova capacidade: vincular o Galaxy Watch à sala pelo telefone, primeira entrega do CV3)

Authors: Eli (Navigator); Codex (Driver, Passos 1–4); Claude Opus 5.5 (Driver, Passos 4–7)

Git source: feature/cv3-ds1-us1-vincular-relogio (merge into master); API antecipada em feature/cv3-ds1-us1-api-relogio

### Added

- [Relógio] **Vínculo pessoal do Wear OS** (`CV3.DS1.US1`): o relógio gera um código de 8 dígitos, válido por 5 minutos; o dono aprova no telefone em **Relógio**. O relógio passa a representar o mesmo participante, sem duplicar a pessoa na sala. Credencial própria, guardada cifrada no Android Keystore e revogável pelo telefone sem derrubar a sessão dele.
- [Relógio] **Apelido-senha `eli.relogio`**: quem entra com ele aparece só como `eli` e já fica habilitado para o relógio (`WATCH_AUTO_GRANT`). `scripts/watch_access.py` continua como alternativa com segredo de owner.
- [Relógio] App Wear OS em `wear/` (Kotlin/Compose), com endereço do servidor pré-configurado.
- API: `/api/watch/pairing`, `/api/watch/session`, `/api/watch/state`, `/api/owner/watch-access` e `/api/quadras/{court}/watch*`, com WebSocket por Bearer.

### Fixed

- [Relógio] O campo do código no site recusava todo código: em template Svelte, `pattern="[0-9]{8}"` era compilado como `[0-9]8`.

### Decisions

- `apelido-senha-habilita-relogio`: a habilitação usa um apelido que só o dono digita, e a sala vê apenas o nome público. Substitui a habilitação por apelido público, que podia ser copiada.

### Debt

- `debt-limite-de-vinculo-do-relogio-por-ip-e-em-memoria` (Carried).
- `debt-banco-de-producao-sem-volume-persistente` (Carried).

### Verification

- `pytest` 133/133, `ruff check` e `ruff format --check` ok; web `npm test` 22/22, `npm run check` sem erros/avisos, `npm run build` ok; Android: 5 testes, `assembleDebug` e `lintDebug` ok.
- Validação física no Galaxy Watch em produção aprovada pelo Navigator (cenários 1–4 do test-guide).

## 0.6.1 - 2026-09-20

Boundary: patch (o Modo Sol passa a valer para a tela inteira: placar, sobreposicoes e acentos deixam de usar cor literal)

Authors: Eli (Navigator); Claude Opus 5 (Driver)

Git source: fix/modo-sol-placar (merge into master)

### Fixed

- [Tema] **Modo Sol aplicado ao placar e as superficies fixas**: o tema claro trocava apenas os tokens de `:root`, mas os componentes ainda carregavam cerca de 130 cores literais — o fundo clareava e o placar continuava preto. Os cartoes do placar viram papel branco com numeral preto puro (21:1), sem gradiente e sem brilho neon; as 44 sobreposicoes `rgba(255, 255, 255, x)` passam pelo token `--veu`; o azul de informacao, o texto dos badges e os estados de erro ganham variantes escurecidas para manter contraste sobre fundo claro.
- [Tema] **Superficies escuras literais na Home e na sala**: `#0f172a`, `#1e293b`, `#334155` e afins estavam escritos nos componentes e nao acompanhavam o tema. Agora resolvem por token.

### Added

- [Design System] Tokens `--veu`, `--cartao-*`, `--ilhos-*`, `--acento-info-*`, `--badge-*-texto`, `--texto-medio`, `--estado-erro-suave` e `--borda-ativa-rgb`, documentados em `docs/product/design-tokens.md`.

### Decisions

- `cores-de-tema-como-token-e-veu-como-canal-de-cor`: nenhum componente declara cor literal, e o veu e publicado como canal de cor em vez de escala fechada de opacidade — a escala exigiria reclassificar 17 opacidades e alteraria a aparencia do Modo Noite.

### Debt

- `debt-contraste-do-modo-sol-sem-verificacao-automatica` (Carried): o contraste dos dois temas e verificado a mao; o projeto nao tem runner de browser.

### Verification

- Paridade do Modo Noite provada comparando o CSS construido antes e depois com as variaveis resolvidas: 388 regras de cor, 381 identicas, 7 consolidacoes deliberadas de tons quase iguais.
- `npm test` 21/21, `pytest` 114/114, `npm run build` ok. Modo Sol e Modo Noite validados manualmente pelo Navigator.

## 0.6.0 - 2026-09-16

Boundary: minor (conclusão do Capability Value 2 completo: layouts fluidos sem overflow, Home com placar ao vivo, entrada em 1 toque, conformidade WCAG 2.2 com zoom e leitores de tela, e quitação total do Technical Debt Ledger)

Authors: Eli (Navigator); Antigravity (Driver)

Git source: feature/cv2-ds3-layouts-fluidos-e-acessibilidade (merge into master)

### Added

- [Responsividade & Layout] **Grid Fluido e Prevenção Global de Overflow** (`CV2.DS3.US1`): Contenção de viewport com `overflow-x: hidden; max-width: 100vw;` e grade responsiva de 2 colunas para desktop (≥960px).
- [Home & Descoberta] **Placar ao Vivo e Indicador 'Ao Vivo' na Home** (`CV2.DS3.US2`): Projeção síncrona leve em `GET /api/quadras` com placar parcial, nomes das equipes e badge pulsante `AO VIVO`.
- [Acesso Rápido] **Entrada em 1 Toque para Espectadores** (`CV2.DS3.US3`): Acesso instantâneo à sala a partir do card da quadra sem telas intermediárias se o apelido já estiver registrado.
- [Ergonomia Visual] **Placar do Espectador em Retrato Otimizado** (`CV2.DS3.US4`): Escala de cartões aproveitando até ~40% da altura da tela móvel em retrato via container queries.
- [Acessibilidade] **Conformidade WCAG 2.2** (`CV2.DS3.US5`): Zoom 200% reabilitado (`user-scalable` desbloqueado), alvos de toque mínimos de 44×44px em todos os botões e narração dinâmica via leitor de tela (`role="status" aria-live="polite"`).

### Debt Paid

- `debt-acessibilidade-e-overflow`: Quitado. Zero débitos técnicos remanescentes no ledger do projeto.

## 0.5.0 - 2026-09-16

Boundary: minor (entrega da Onda 2 do CV2: ergonomia de arbitragem, modo sol, wake lock, modais nativos com <dialog>, QR code SVG, celebração de vitória, PWA e ciclo de múltiplas partidas com duplas configuráveis in-game)

Authors: Eli (Navigator); Antigravity (Driver)

Git source: claude/subagentes-backlog-features-sqbsfs (merge into master)

### Added

- [Ergonomia] **Modo Quadra em Paisagem** (`CV2.DS2.US1`): Orientação horizontal em tela cheia sem rolagem vertical, dividida 50/50 entre equipes e com botão de desfazer sempre acessível.
- [Ergonomia] **Zona do Polegar** (`CV2.DS2.US2`): Botões de marcação e desfazimento posicionados ergonomicamente no terço inferior da tela móvel, com feedback tátil e estado visual `aria-busy`.
- [Confiabilidade] **Screen Wake Lock API** (`CV2.DS2.US3`): Prevenção automática de desligamento da tela enquanto o jogo estiver em andamento, com religamento no evento `visibilitychange`.
- [Visibilidade] **Modo Sol de Alto Contraste** (`CV2.DS2.US4`): Tema claro via atributo `data-tema="sol"` otimizado para legibilidade sob sol forte sem borrões ou reflexos de glow.
- [Governança] **Governança de Controle e Apelidos Únicos** (`CV2.DS2.US5`, `CV2.DS2.US6`): Bloqueio de repasse de controle para participantes desconectados, auto-retorno ao admin após 15s de inatividade do operador e unicidade de apelidos na quadra.
- [Transporte] **Reconexão Resiliente** (`CV2.DS2.TS1`): WebSocket com reconexão por backoff exponencial e jitter aleatório.
- [Acessibilidade] **Padronização de Diálogos Nativos** (`CV2.DS4.US2`): Componente `Dialogo.svelte` baseado em `<dialog>` com focus trap, tecla Escape e clique no backdrop em todos os modais.
- [Compartilhamento] **QR Code SVG Puro e Web Share API** (`CV2.DS4.US5`): Gerador local de QR Code SVG sem CDNs (`qrcode.js`), botão de cópia de link e integração com folha nativa de compartilhamento.
- [Celebração] **Tela de Celebração de Vitória** (`CV2.DS4.US1`): Encerramento comemorativo com troféu pulsante, cores do campeão e atalhos rápidos.
- [PWA & Performance] **Instalação PWA e Fontes Locais** (`CV2.DS4.US6`): Manifesto PWA `webmanifest`, ícones adaptativos e fontes locais WOFF2 latin (Inter e Teko).
- [Produto] **Onboarding Ultralight & Configuração In-Game**: Criação de quadra sem fricção na Home (somente apelido e nome opcional) e botão de configuração in-game e no reinício para trocar duplas e ajustar regras (`POST /api/quadras/{id}/configurar` e `POST /api/quadras/{id}/reiniciar`) permitindo múltiplas partidas na mesma sala.

### Debt Paid

- `debt-modais-ad-hoc-e-reconexao`: Quitado com `<dialog>` nativo e backoff com jitter.
- `debt-apelidos-e-transferencia-de-controle`: Quitado com unicidade de apelidos e governança de controle.
- `debt-tokens-e-cores-acopladas`: Quitado com tokens em `app.css` e cores de time exclusivas.
- `debt-codigo-mestre-no-websocket`: Quitado com allowlist no snapshot do WebSocket.
- `debt-lotacao-fantasma`: Quitado com contagem de capacidade baseada em presença real.
- `debt-integridade-de-toques-e-erros-422`: Quitado com fila de comandos e normalização legível de 422.

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
