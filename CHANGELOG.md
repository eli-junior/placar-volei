# Changelog

Este changelog registra tanto o **trabalho ativo em andamento** (para coordenação multi-agente e handoff) quanto as **versões fechadas**.

## [Em Andamento]

### CV8.DS7.US17 — Segredo do dono não some por engano

- **Branch:** `fix/cv8-ds7-us17-segredo-nao-some`
- **Passo Ariad:** Passo 2 - Planejamento (aguardando Checkpoint 1)
- **Assinatura do Agente:** Agente: Claude Sonnet 5.5 (Driver) | Sessão: c9898a4f | Data: 2026-10-08
- **Handoff / Próximos Passos:** plano em `docs/project/roadmap/cv8-gerenciador-de-times/cv8-ds7-joguinho-sem-becos/cv8-ds7-us17-segredo-nao-some-por-engano/plan.md`; nenhum código escrito. Depois da confirmação: servidor (sem cabeçalho não conta; 4429 no WS), cliente (`recusado`, `Retry-After`) e testes.

## 0.46.3 - 2026-10-08

Boundary: Technical Story CV8.DS7.TS2 — quadra do joguinho não some no meio da rodada (patch; backend, web e APK em 0.46.3, APK `versionCode` 26; só o backend muda de comportamento; Wear OS inalterado em 0.27.0).

Authors: Eli (Navigator); Claude Sonnet 5.5 (Driver) — Agente: Claude Sonnet 5.5 (Driver) | Sessão: c9898a4f | Data: 2026-10-08

Git source: merge `--no-ff` de `fix/cv8-ds7-ts2-quadra-do-joguinho` em `master`.

### Fixed

- **Quadra de uma rodada em andamento não expira por TTL** (QA P2/F3): o servidor renova a quadra vinculada na subida e a cada ciclo da limpeza (`min(300 s, TTL/2)`). A regra do TTL não mudou; fora de rodada em andamento a quadra expira como antes.
- **Vínculo com quadra que sumiu** (reinício, por exemplo): sem partida chamada o joguinho passa a mostrar "Nenhuma quadra vinculada"; com partida chamada mostra "indisponível — anule a partida", e depois de anular o vínculo é limpo. Vale também para a resposta das operações, não só para a leitura.

### Decision

- Registro `quadra-da-rodada-renovada-pelo-servidor`: o banco das quadras segue efêmero (decisão de 2026-09-27); o joguinho se reconcilia com ele.

### Verification

- `uv run pytest` (586 numa rodada completa; `tests/test_sorteio.py` oscila nesta máquina, também no `master`, e 485 passam sem ele), `ruff` limpo, e2e da condução (12). Validado pelo Navigator em 2026-10-08.

## 0.46.2 - 2026-10-08

Boundary: fix CV8.DS7.US16 — anular partida chamada, primeira correção da auditoria do QA de 2026-10-08 (patch; backend, web e APK em 0.46.2, APK `versionCode` 25; Wear OS inalterado em 0.27.0).

Authors: Eli (Navigator); Claude Opus 5.5 (Driver) — Agente: Claude Opus 5.5 (Driver) | Sessão: ae33f4a8 | Data: 2026-10-08

Git source: merge `--no-ff` de `fix/joguinho-sempre-encerravel` em `master`.

### Fixed

- **Joguinho preso com partida chamada numa quadra que sumiu** (QA P1/P6/F1): não dava para encerrar a partida, trocar ou desvincular a quadra, nem encerrar o joguinho sem cancelar a rodada. Agora há **Anular partida** (sempre disponível com partida chamada, com confirmação): a partida não conta, os times voltam a ser a próxima partida e a rodada segue. O placar da quadra não é tocado.
- **Cancelar rodada** apaga a partida chamada; antes ela ficava pendurada e travava o vínculo da quadra para sempre. A trava passou a olhar só a rodada em andamento, o que destrava bancos já presos.
- Mensagens que mandavam "vincular de novo" (impossível com partida chamada) agora apontam a saída: anular.

### Planned

- O restante da auditoria virou a CV8.DS7 no roadmap: TS2 (quadra não some no meio da rodada), US17 (segredo não some por engano), US18 (rota `/joguinho` e 404), US19 (retirar jogador), US20 (joguinho de ontem e mensagens), US21 (resultado de partida abandonada, adiada).

### Verification

- `uv run pytest` (581), `npm run check`, `npm test` (185), `npm run test:e2e` (84). Validado pelo Navigator em produção (2026-10-08): anulou a partida presa e revinculou a quadra.

## 0.46.1 - 2026-10-08

Boundary: fix — placar do controlador coberto pelos botões +1 (patch; backend, web e APK em 0.46.1, APK `versionCode` 24; Wear OS inalterado em 0.27.0).

Authors: Eli (Navigator); Claude Sonnet 5.5 (Driver)

Git source: merge `--no-ff` de `fix/placar-controlador-com-fila` em `master`.

### Fixed

- Na tela do controlador (altura fixa, sem rolagem), o cartão "Rodada / Fila / Reis" da US13 (0.44.0) tomava a altura do placar e os botões +1 ficavam sobre o placar do time de baixo. O controlador passa a ver a faixa compacta de uma linha; o cartão completo segue para quem só acompanha.
- Teste de regressão em `e2e/conducao.spec.js` (placar com mais de 200 px e acima dos botões, em 360×700).

## 0.46.0 - 2026-10-08

Boundary: Maintenance CV8 — ajustes da tela "Novo joguinho" (minor; backend, web e APK em 0.46.0, APK `versionCode` 23; Wear OS inalterado em 0.27.0).

Authors: Eli (Navigator); Claude Sonnet 5.5 (Driver)

Git source: merge `--no-ff` de `feature/cv8-joguinho-ajustes` em `master`.

### Changed

- **Pontos da partida:** slider de 6 a 25 (padrão 10), no lugar de 10 ou 12. Schema 10: a tabela `rodadas` é recriada preservando as linhas (o CHECK do alvo mudou).
- **Mínimo para sortear:** a mensagem acompanha o formato ("Faltam 6 presentes para sortear" no trio); o rótulo é só "Trios".
- **Cadastro rápido** saiu: entrou o botão "Gerenciar jogadores" (abre a tela de Jogadores; o jogador cadastrado não é marcado presente sozinho).
- **Ordem de chegada:** arrastar pela alça ⠿ (pointer events), além dos botões ↑ ↓.

### Verification

- `uv run pytest` (575), `npm run check`, `npm test` (185), `npm run test:e2e` (82). Validado pelo Navigator no celular.
- Dívida nova: endpoint `/presencas/rapido` sem uso na tela; arrastar sem rolagem automática.

## Sem versão - 2026-10-08 (Placar Web)

Boundary: Maintenance — o app instalado pelo navegador (PWA) passa a se chamar "Placar Web", para conviver com o APK "Placar Vôlei" no mesmo aparelho (sem versão nova).

Authors: Eli (Navigator); Claude Sonnet 5.5 (Driver)

Git source: merge `--no-ff` de `chore/nome-placar-web` em `master`.

### Changed

- `web/public/manifest.webmanifest`: `name` e `short_name` = "Placar Web". O APK segue "Placar Vôlei". Quem já instalou o PWA pode precisar reinstalar para o nome novo aparecer.

## Sem versão - 2026-10-08

Boundary: Maintenance — renomear "Sessão" para "Joguinho" na interface (sem versão nova; backend, web e APK seguem em 0.45.0).

Authors: Eli (Navigator); Claude Sonnet 5.5 (Driver)

Git source: merge `--no-ff` de `chore/renomear-sessao-joguinho` em `master`.

### Changed

- Textos da tela vazia: "Nenhum joguinho rolando", "Comece um novo joguinho para marcar quem chegou." e botão "Novo joguinho" (branch `chore/textos-joguinho`).
- O botão da tela inicial e o título da tela passam a dizer "Joguinho". Textos internos ("Abrir sessão"), mensagens e API não mudaram.

## 0.45.0 - 2026-10-08

Boundary: CV8.DS6.US15 — formato trio (minor; backend, web e APK em 0.45.0, APK `versionCode` 22; Wear OS inalterado em 0.27.0).

Authors: Eli (Navigator); Claude Sonnet 5.5 (Driver)

Git source: merge `--no-ff` de `feature/cv8-ds6-us15-formato-trio` em `master`.

### Added

- **Rodada em trios (RN-16):** ao sortear, o operador escolhe Duplas ou Trios (mínimo 6 presentes). Trios equilibrados pela nota e mistos: nenhum fecha só de um sexo havendo alternativa; sem sexo suficiente, o sorteio minimiza os trios de um sexo.
- **Sobra:** 1 jogador sobrando escolhe 2 parceiros; 2 sobrando escolhem 1; um por vez, e a partida só é chamada com o time completo. Fila, rei da quadra, mata-mata, desfazer, substituição, atrasado e espectador funcionam com 3 nomes.
- Schema 9 (aditivo): `rodadas.formato`. API: `formato` em `/api/rodada/sorteio` e `/resortear`.

### Verification

- `uv run pytest` (569, com `tests/test_trio.py`), `npm run check`, `npm test`, `npm run test:e2e` (80). Aguarda validação do Navigator, incluindo 3 nomes no relógio físico.
- Dívida nova: dois algoritmos de sorteio (dupla e N); sem teste do relógio com 3 nomes.

## Sem versão - 2026-10-08

Boundary: CV6.DS2.US4 (follow-up) — medição de repouso no relógio; só documentação, sem versão nova (Wear em 0.27.0).

Authors: Eli (Navigator); Claude Sonnet 5.5 (Driver)

Git source: merge `--no-ff` de `feature/cv6-ds2-us4-pausa-no-repouso` em `master`.

### Documented

- Pausa de sensor e animação em repouso já existia (medido); ponto remoto com a tela apagada validado.
- Placar sair ao levantar o pulso vinha do `wear_activity_auto_resume_timeout_ms` do Wear OS (60 s); ajuste por aparelho via ADB, validado.
- Não observados: reconexão após queda real de rede, treino ativo e bateria. CV6.DS2 marcada como `Done`.

## 0.44.0 - 2026-10-07

Boundary: CV8.DS5.US13 e CV8.DS5.US14 — exibição; fecha a CV8.DS5 e a CV8 (minor; backend, web e APK em 0.44.0, APK `versionCode` 21; Wear OS inalterado em 0.27.0).

Authors: Eli (Navigator); Claude Sonnet 5.5 (Driver)

Git source: merge `--no-ff` de `feature/cv8-ds5-exibicao` em `master`.

### Added

- **Fila e reis para o espectador (US13):** quem está na sala da quadra vinculada à sessão vê, além do placar, quem joga, a fila de espera e os reis (só nomes curtos e vitórias; sem notas, ids nem saldo). No modo imersivo aparece uma faixa ("Fila: … · Reis: …"); fora dele, um cartão completo. Atualiza sozinho a cada mudança do gerenciador (`EXIBICAO_ATUALIZADA`) e já vem no `ESTADO_INICIAL`; ao fim da rodada mostra os campeões.
- **Nomes das duplas no relógio (US14):** já entregue pela chamada de partida (CV8.DS3.US5): o `estado_partida` do WebSocket leva `equipe_a`/`jogadores_a` e o relógio (Wear 0.27.0) mostra os nomes em linhas. Coberto por `tests/test_chamada.py`; nenhum código novo.

### Verification

- `uv run pytest` (552, com `tests/test_exibicao.py`), `npm run check`, `npm run test:e2e` (com o teste novo do espectador). Aguarda validação do Navigator em lote, incluindo o relógio físico (US14).
- Dívida nova: ao desvincular a quadra, a sala antiga mantém a última fila até reconectar.

## 0.43.0 - 2026-10-07

Boundary: CV8.DS3.US7 — desfazer a última partida; fecha a CV8.DS3 (minor; backend, web e APK em 0.43.0, APK `versionCode` 20; Wear OS inalterado em 0.27.0).

Authors: Eli (Navigator); Claude Sonnet 5.5 (Driver)

Git source: merge `--no-ff` de `feature/cv8-ds3-us7-desfazer-ultima-partida` em `master`.

### Added

- **Desfazer última partida (RN-09):** em "Partidas encerradas", **Desfazer última partida** (com confirmação) apaga a última partida encerrada e devolve fila, reis, eliminados, vitórias e histórico ao instante anterior. Um nível só (até a próxima partida ser encerrada). Uma partida já chamada depois dela é descartada junto.
- **Mata-mata e campeão agora têm desfazer:** desfazer a partida que deu o campeão reabre a rodada (também pelo cartão "Campeões da rodada", enquanto não há outra rodada ativa); desfazer a última da fila cancela o início do mata-mata.
- API `POST /api/rodada/desfazer-partida`; `pode_desfazer` no estado da sessão; schema 8 (aditivo): `rodadas.desfeito`.

### Verification

- `uv run pytest` (548, com `tests/test_desfazer_partida.py`), `npm run check`, `npm run test:e2e`. Aguarda validação do Navigator em lote. Fecha a CV8.DS3 (US5 a US10).
- Paga a dívida "mata-mata e campeão sem como desfazer". Não desfaz a escalação do parceiro nem a substituição feitas depois da partida.

## 0.42.0 - 2026-10-07

Boundary: CV8.DS3.US10 — substituir jogador que saiu (minor; backend, web e APK em 0.42.0, APK `versionCode` 19; Wear OS inalterado em 0.27.0).

Authors: Eli (Navigator); Claude Sonnet 5.5 (Driver)

Git source: merge `--no-ff` de `feature/cv8-ds3-us10-substituir-jogador-que-saiu` em `master`.

### Added

- **Substituir quem saiu (RN-08):** no painel da condução, escolha quem saiu de um time ativo (em quadra, fila ou rei) e quem entra: o ímpar/atrasado que aguarda na fila (o time dele deixa de existir) ou um eliminado da lista de escalação (joga por um segundo time, "escalado"). O time mantém vitórias e posição; não forma H+H havendo mulher elegível (RN-01); bloqueado com partida chamada.
- Quem saiu fica **ausente** na sessão (reversível: "Chegou atrasado" durante a rodada ou "Presente" depois dela).
- API `POST /api/rodada/substituir`; `conducao.substituicao` com as opções. Sem schema novo.

### Verification

- `uv run pytest` (541), `npm run check`, `npm run test:e2e`. Aguarda validação do Navigator em lote.
- Dívida nova: o histórico de partidas do time passa a ser creditado ao substituto no saldo (as linhas de `time_jogadores` são trocadas).

## 0.41.0 - 2026-10-07

Boundary: CV8.DS3.US9 — registrar atrasado (minor; backend, web e APK em 0.41.0, APK `versionCode` 18; Wear OS inalterado em 0.27.0).

Authors: Eli (Navigator); Claude Sonnet 5.5 (Driver)

Git source: merge `--no-ff` de `feature/cv8-ds3-us9-registrar-atrasado` em `master`.

### Added

- **Atrasado no meio da rodada (RN-06):** com a rodada em andamento, **Chegou atrasado** (lista de ausentes) marca a presença no fim da ordem e cria um time incompleto só dele no fim da fila (`origem = 'atrasado'`); ele escolhe o parceiro na sua vez pela lista de escalação. Dois atrasados nunca formam dupla entre si. Bloqueado após o início do mata-mata (continua ausente e entra no próximo sorteio).
- API `POST /api/rodada/atrasado`; sem schema novo (`times.origem` já existia).

### Verification

- `uv run pytest` (537), `npm run check`, `npm run test:e2e` (77). Aguarda validação do Navigator (em lote com US10/US7).

## 0.40.0 - 2026-10-07

Boundary: CV8.DS2.US4 — sortear rodadas seguintes com reequilíbrio; fecha a CV8.DS2 (minor; backend, web e APK em 0.40.0, APK `versionCode` 17; Wear OS inalterado em 0.27.0).

Authors: Eli (Navigator); Claude Sonnet 5.5 (Driver)

Git source: merge `--no-ff` de `feature/cv8-ds2-us4-sortear-rodadas-seguintes` em `master`.

### Added

- **Reequilíbrio entre rodadas:** da segunda rodada em diante o sorteio usa a **nota efetiva** (RN-14: ajuste de até ±15 pelo saldo médio por partida, só na sessão; a nota cadastrada não muda) e evita as duplas já formadas na sessão entre as combinações equivalentes (RN-10). A proposta mostra o ajuste ("Ana (68 +8)").
- A ordem de chegada vale em todas as rodadas (RN-13 revista). Rodada cancelada não entra no saldo nem nas duplas anteriores.

### Verification

- `uv run pytest` (533), `npm run check`, `npm run test:e2e` (77). Validada pelo Navigator.
- Sem schema novo. Dívida nova: consulta por time em `saldos_da_sessao`; `rodada.py` em 548 linhas.

## 0.39.0 - 2026-10-07

Boundary: CV8.DS4.US12 — persistir a sessão; fecha a CV8.DS4 (minor; backend, web e APK em 0.39.0, APK `versionCode` 16; Wear OS inalterado em 0.27.0).

Authors: Eli (Navigator); Claude Sonnet 5.5 (Driver)

Git source: merge `--no-ff` de `feature/cv8-ds4-us12-persistir-sessao` em `master`.

### Changed

- Toda conexão do `gerenciador.db` grava com `PRAGMA synchronous=FULL`: o resultado de uma partida não se perde numa queda.

### Verification

- `uv run pytest` (521), com `tests/test_persistencia.py`: o mesmo estado após reiniciar a cada partida, no mata-mata e no campeão; registro completo (placar, vencedor, fase, horários, times, notas, campeão) para o ranking futuro; partidas preservadas ao cancelar a rodada e encerrar a sessão. Validada pelo Navigator com reinício do contêiner.
- Sem schema nem rota novos. Dívidas carregadas: mata-mata sem como desfazer; concentração em `rodada.py` e `Sessao.svelte`.

## 0.38.0 - 2026-10-07

Boundary: CV8.DS4.US11 — conduzir o mata-mata (minor; backend, web e APK em 0.38.0, APK `versionCode` 15; Wear OS inalterado em 0.27.0).

Authors: Eli (Navigator); Claude Sonnet 5.5 (Driver)

Git source: merge `--no-ff` de `feature/cv8-ds4-us11-conduzir-o-mata-mata` em `master`.

### Added

- **Mata-mata manual:** no fim da fila, **Iniciar mata-mata** (ou **Coroar campeão**, sem reis) fecha as entradas. O desafiante (o time sozinho na quadra, ou o último rei se a quadra esvaziou) enfrenta os reis na ordem de coroação; partida única, ganhou ficou, perdeu saiu.
- **Campeão da rodada:** ao encerrar o último confronto a rodada se encerra com o campeão registrado e o próximo sorteio é liberado; o cartão "Campeões da rodada N" aparece em todos os aparelhos.
- API `POST /api/rodada/iniciar-mata-mata`; schema 7 (aditivo): `rodadas.mata_mata_em`, `rodadas.campeao_time_id`, `partidas_rodada.fase`.

### Verification

- `uv run pytest` (517), `npm run check`, `npm run test:e2e` (77, com mata-mata em dois aparelhos e axe). Validada pelo Navigator.
- Dívida nova: mata-mata e campeão sem como desfazer; agravadas: `rodada.py` (529 linhas) e `Sessao.svelte` (369).

## 0.37.0 - 2026-10-07

Boundary: CV8.DS3.US8 — escalar o parceiro do time incompleto (minor; backend, web e APK em 0.37.0, APK `versionCode` 14; Wear OS inalterado em 0.27.0).

Authors: Eli (Navigator); Claude Sonnet 5.5 (Driver)

Git source: merge `--no-ff` de `feature/cv8-ds3-us8-escalar-parceiro-do-time-incompleto` em `master`.

### Added

- **Escolha do parceiro** do time incompleto quando ele chega à quadra: lista de escalação (eliminados fora de time ativo), com **gênero** (homem incompleto só vê mulheres, salvo falta de alternativa) e **ordem de chegada**; **Chamar partida** fica bloqueado até a escolha. Destrava as rodadas de número ímpar.
- O escalado joga por um **segundo time** (histórico das duas partidas preservado), sai de "Eliminados" enquanto joga e volta se esse time perder; "· escalado" ao lado do nome.
- **Saldo da rodada** no painel (pontos feitos − sofridos, somando os dois times do escalado).
- API `POST /api/rodada/escalar-parceiro`; schema 6 (aditivo): `times.origem` (pronta para os atrasados) e `time_jogadores.escalado`.

### Verification

- `uv run pytest` (507), `npm test` (183), `npm run check`, `npm run test:e2e` (76, com o fluxo do ímpar, dois aparelhos e axe). Validada pelo Navigator.
- Dívidas novas: `rodada.py` concentra regras/painel/escalação, escalação sem como desfazer, rodada trava sem elegíveis; agravada: `Sessao.svelte` com 362 linhas.

## 0.36.0 - 2026-10-07

Boundary: CV8.DS3.US6 — encerrar partida e aplicar o rei da quadra (minor; backend, web e APK em 0.36.0, APK `versionCode` 13; Wear OS inalterado em 0.27.0).

Authors: Eli (Navigator); Claude Sonnet 5.5 (Driver)

Git source: merge `--no-ff` de `feature/cv8-ds3-us6-encerrar-partida-e-rei-da-quadra` em `master`.

### Added

- **Encerrar partida**: lê o placar final da quadra vinculada e grava placar e vencedor; só aceita partida terminada pelas regras do placar e que seja a da chamada.
- **A fila anda**: o perdedor é eliminado, o vencedor segue ou vira rei com 2 vitórias seguidas e entram os 2 próximos; os reis aparecem em ordem.
- **Painel**: placar ao vivo da partida chamada (sem atualizar), botão **Encerrar partida** que habilita ao terminar, histórico das partidas encerradas e faixa de **fim da fila** (mata-mata é a US11), que bloqueia novas chamadas.
- Cada evento da quadra vinculada avisa o gerenciador (só com aparelho conectado; nunca derruba o placar).

### Changed

- **Cancelar rodada** com partidas registradas pede confirmação reforçada; nada é apagado.
- Rotas da rodada reunidas em `app/rodada_rotas.py` (`sessao.py` volta a ser só sessão e presença).
- Teste de composições de gênero do sorteio enxugado (menos CPU na máquina de desenvolvimento).

### Verification

- `uv run pytest` (483), `npm test` (182), `npm run check`, `npm run test:e2e` (75, com axe e dois aparelhos). Validada pelo Navigator.
- Dívidas quitadas: `cancelar-rodada-nao-checa-partidas`, `rotas-da-rodada-na-sessao-py`. Novas: `ponte.py` concentra três responsabilidades, o aviso do placar recalcula o estado completo, o erro de encerrar aparece no bloco da quadra.

## 0.35.0 - 2026-10-07

Boundary: CV8.DS3.US5 — visualizar e conduzir a fila (minor; backend, web e APK em 0.35.0, APK `versionCode` 12; Wear OS inalterado em 0.27.0).

Authors: Eli (Navigator); Claude Sonnet 5.5 (Driver)

Git source: merge `--no-ff` de `feature/cv8-ds3-us5-visualizar-e-conduzir-a-fila` em `master`.

### Added

- **Vínculo da sessão com a quadra do placar**: "Criar quadra e vincular" ou por código; conferido a cada uso (pode ficar "indisponível").
- **Chamar partida**: carrega as duplas ("Ana + Gil"), o alvo da rodada e a vantagem de 2 no placar da quadra, zerado; recusada se a quadra tem partida em andamento com pontos; uma partida chamada por rodada.
- **Painel da condução** em `/sessao`: quadra do placar, partida em quadra ou próxima, fila numerada, reis (com a ordem) e eliminados; bloqueio quando o time incompleto entra em quadra (US8).
- **Sincronia entre aparelhos** pelo WebSocket `/ws/gerenciador` (segredo na primeira mensagem, nunca na URL), com selo "Ao vivo" e reconexão; todas as mudanças da sessão, da rodada, dos jogadores e do vínculo chegam sem atualizar.
- Schema 5 do `gerenciador.db` (migração aditiva): `sessoes.quadra_id` e `partidas_rodada`. Módulo puro `app/conducao.py`.

### Changed

- A tela da sessão acompanha os outros aparelhos sozinha; "Atualizar" e a volta de foco ficam como reserva.

### Verification

- `uv run pytest` (552), `npm test` (182), `npm run check`, `npm run test:e2e` (73, com axe e dois aparelhos sincronizando). Validada pelo Navigator.
- Dívidas registradas: leitura do estado limpa quadras expiradas, difusão do estado completo, WebSocket não fecha ao trocar o segredo; agravadas: rotas da rodada em dois arquivos e `Sessao.svelte` com 346 linhas.

## 0.34.0 - 2026-10-07

Boundary: CV8.DS2.US3 — sortear a primeira rodada (minor; backend, web e APK em 0.34.0, APK `versionCode` 11; Wear OS inalterado em 0.27.0).

Authors: Eli (Navigator); Claude Sonnet 5.5 (Driver)

Git source: merge `--no-ff` de `feature/cv8-ds2-us3-sortear-primeira-rodada` em `master`.

### Added

- **Sorteio da primeira rodada** (tela `/sessao`): alvo 10 ou 12, duplas equilibradas pela nota (sem aleatoriedade), gênero com o número mínimo de duplas H+H, ímpar = último a chegar como time incompleto no fim da fila, fila pela ordem de chegada e primeira partida em destaque.
- **Proposta** persistida para **confirmar**, **resortear** (outra combinação igualmente equilibrada, até 3 pontos pior), **descartar**; rodada em andamento com **cancelar**.
- **Presença travada** durante a proposta e a rodada em andamento; inativar quem está na rodada e encerrar a sessão com rodada ativa são recusados.
- API `/api/rodada/{sorteio,resortear,confirmar,descartar,cancelar}`; a rodada também vem no `GET /api/sessao`. Schema 4 do `gerenciador.db` (migração aditiva).

### Changed

- Módulo comum `app/gerenciador_db.py` (conexão, esquema, erros, transação de escrita), usado por jogadores, sessão e rodada.

### Verification

- `uv run pytest` (519), `npm test` (179), `npm run check`, `npm run test:e2e` (68, com axe). Validada pelo Navigator.
- Dívida `modulo-comum-do-gerenciador-db` quitada; novas: rotas da rodada na `sessao.py`, `Sessao.svelte` grande, sorteio heurístico sem prova de ótimo, cancelar rodada sem checar partidas.

## 0.33.1 - 2026-10-07

Boundary: CV8.TS1 — backup e restauração do `gerenciador.db` (patch; backend, web e APK em 0.33.1, APK `versionCode` 10; Wear OS inalterado em 0.27.0).

Authors: Eli (Navigator); Claude Sonnet 5.5 (Driver)

Git source: merge `--no-ff` de `feature/cv8-ts1-backup-do-gerenciador` em `master`.

### Added

- **Backup automático** do `gerenciador.db`: cópia pela API de backup do SQLite, verificada antes de ganhar o nome final, na subida e a cada 6 h, mantendo as 28 mais recentes. Falha é logada, não derruba o app e nunca substitui nem faz podar cópias boas.
- **Linha de comando** `python -m app.backup agora | listar | restaurar <arquivo> [--destino <caminho>]`; a restauração verifica a cópia e guarda o banco atual como `.antes-<data>`.
- **Compose:** pasta do host `./backups` montada em `/backups`, fora do volume do banco; variáveis `GERENCIADOR_BACKUP_DIR`, `GERENCIADOR_BACKUP_INTERVALO_HORAS` e `GERENCIADOR_BACKUP_MANTER`.
- Procedimento de backup e restauração no `docs/process/development-guide.md`.

### Fixed

- A cópia sai como arquivo único (modo `DELETE`), sem `-wal`/`-shm` soltos na pasta.
- Um backup não apaga mais a sobra `.parcial` de outro em andamento (só as com mais de 1 h).

### Verification

- `uv run pytest` (316; 13 novos), fumaça com servidor real e restauração de ensaio. Validada pelo Navigator.
- Dívida `sem-backup-do-volume-de-jogadores` quitada; novas: cópias na mesma máquina, falha de backup só no log, `.antes-*` acumulando.

## 0.33.0 - 2026-10-07

Boundary: CV8.DS1.US2 — abrir sessão e marcar presença; fecha a CV8.DS1 (minor; backend, web e APK em 0.33.0, APK `versionCode` 9; Wear OS inalterado em 0.27.0).

Authors: Eli (Navigator); Claude Sonnet 5.5 (Driver)

Git source: merge `--no-ff` de `feature/cv8-ds1-us2-abrir-sessao-e-presenca` em `master`.

### Added

- **Sessão do dia** (tela `/sessao`, botão "Sessão" na Home): abrir, encerrar com confirmação, uma aberta por vez (garantido por índice no banco).
- **Presença a partir da base** e **cadastro rápido** (nome e sobrenome, gênero, nota opcional) que já marca presente.
- **Ordem de chegada** de 1 a N: marcar entra no fim, desmarcar renumera, reordenar por ↑/↓. Aviso "faltam N para poder sortear" (mínimo 4).
- API `/api/sessao`, protegida pelo `OWNER_SECRET`; tabelas `sessoes` e `presencas` (schema 3 do `gerenciador.db`, migração aditiva).

### Changed

- Inativar um jogador presente o tira da presença da sessão aberta e renumera a ordem.
- Formulário de segredo extraído para um componente compartilhado pelas telas de Jogadores e Sessão.

### Fixed

- Reordenar com a tela desatualizada recarrega a lista em vez de só mostrar o erro.
- Renumeração da ordem não pode mais empatar posições.

### Verification

- `uv run pytest` (303), `npm test` (175), `npm run check`, `npm run test:e2e` (64, com axe). Validada pelo Navigator.
- Dívidas registradas: módulo comum do `gerenciador.db`, contraste do contador de quadras na Home, sessões encerradas sem histórico.

## 0.32.0 - 2026-10-07

Boundary: CV8.DS1.US15 — nota, sobrenome e foto do jogador (minor; backend, web e APK em 0.32.0, APK `versionCode` 8; Wear OS inalterado em 0.27.0).

Authors: Eli (Navigator); Claude Sonnet 5.5 (Driver)

Git source: merge `--no-ff` de `feature/cv8-ds1-us15-nota-sobrenome-e-foto` em `master`.

### Added

- **Nota do jogador** de 1 a 100; vazia no cadastro vale 60.
- **Foto opcional**, tirada na hora pelo botão de câmera (celular) ou escolhida (computador); reduzida no aparelho, JPEG de até 256 KB, guardada no `gerenciador.db`. Trocar e remover.
- Miniatura (ou iniciais) e nota na lista de jogadores.

### Changed

- **Nome exige ao menos 2 palavras** (criar e editar). Nomes antigos de uma palavra seguem válidos até a edição.
- `gerenciador.db` passa ao schema 2 por migração aditiva; jogadores da 0.31.0 ficam com nota 60.

### Verification

- `uv run pytest` (290), `npm test` (172), `npm run check`, `npm run test:e2e` (58, com axe). Validada pelo Navigator.
- Dívidas registradas: corpo da foto sem teto na leitura, fotos sem exclusão em massa, lista baixa fotos uma a uma.

## 0.31.0 - 2026-10-07

Boundary: CV8.DS1.US1 — cadastrar jogadores (minor; backend, web e APK em 0.31.0, APK `versionCode` 7; Wear OS inalterado em 0.27.0).

Authors: Eli (Navigator); Claude Sonnet 5.5 (Driver)

Git source: merge `--no-ff` de `feature/cv8-ds1-us1-cadastrar-jogadores` em `master`.

### Added

- **Base de jogadores** (nome e gênero H/M): criar, editar, inativar e reativar. Nome único entre ativos, sem diferenciar caixa nem acento; inativar libera o nome.
- **Tela `/jogadores`** na web, com botão na Home. Pede o `OWNER_SECRET` uma vez e o guarda no aparelho; oculta em qualquer página aberta no APK.
- **API** `/api/jogadores` (listar, criar, editar, inativar, reativar), toda protegida pelo `OWNER_SECRET`.
- **Armazenamento durável:** `gerenciador.db` (`GERENCIADOR_DB_PATH`) no volume `gerenciador-dados`, fora do reset efêmero do banco das quadras.

### Verification

- `uv run pytest` (274), `npm test` (169), `npm run check`, `npm run test:e2e` (56, com axe). Validada pelo Navigator.
- Dívidas registradas: segredo no `localStorage`, sem backup do volume, listagem sem paginação.

## 2026-10-07 — Registro da CV8 (sem versão)

Boundary: documentação — CV8 Gerenciador de times registrada no roadmap (14 User Stories em `Planned`, regras RN-01..RN-12); sem mudança de código nem de versão.

Authors: Eli (Navigator); Claude Sonnet 5.5 (Driver)

Git source: merge `--no-ff` de `docs/roadmap-gerenciador-de-times` em `master`.

## 0.30.1 - 2026-10-02

Boundary: manutenção — destaque do último ponto legível (patch; backend, web e APK em 0.30.1, APK `versionCode` 6; Wear OS inalterado em 0.27.0).

Authors: Eli (Navigator); Claude Code (Driver) | Sessão: 8c235e38

Git source: merge `--no-ff` de `fix/destaque-ultimo-ponto` em `master`.

### Changed

- **Quem tomou o ponto não é mais apagado.** O número do outro time ficava com 42% de opacidade e pouca saturação, claro demais para ler; agora fica como no 0x0, nos modos clássico e resultado.
- **Clássico:** o cartão de quem pontuou ganha borda de 4px na cor do time, além de crescer, acender e ter a bolinha.
- **Resultado:** sai a moldura cinza arredondada em volta do placar; fica só a borda reta na cor de quem pontuou.

### Fixed

- Restaurada no CHANGELOG a seção 0.30.0 (reiniciar partida), perdida no merge da 0.29.1.

### Verification

- `npm test` (164) e `npm run build`. APK release instalado no Galaxy Z Fold e aprovado pelo Navigator.

## 0.30.0 - 2026-10-02

Boundary: Manutenção — reiniciar partida pelo menu ⋯ (minor; backend, web e APK em 0.30.0, APK `versionCode` 5; Wear OS inalterado em 0.27.0).

Authors: Eli (Navigator); Claude Sonnet 5.5 (Driver) | Sessão: 3e3250cd

Git source: merge `--no-ff` de `feature/reiniciar-partida-menu` em `master`.

### Added

- Botão **Reiniciar partida** no menu ⋯ (web e quadra local do APK), com confirmação: zera pontos e linha do tempo no meio da partida e mantém regras, nomes e tema. Só para admin com o controle.
- `zerar` no corpo de `POST /quadras/{id}/reiniciar`; sem ele, reiniciar continua exigindo partida encerrada.

### Verification

- `uv run pytest` (226), `npm test` (164), `npm run check`, `npm run test:e2e` (51); validado pelo Navigator na web e no APK.

## 0.29.1 - 2026-10-02

Boundary: manutenção — MCP de dispositivos (patch do pacote em 0.29.1; APK 0.29.0 e Wear 0.27.0 seguem iguais, pois o produto não mudou).

Authors: Eli (Navigator); Claude Code (Driver) | Sessão: 014YCmLkudLSJamwqvTsmtEJ

Git source: merge `--no-ff` de `chore/mcp-dispositivos` em `master`.

### Added

- **MCP `dispositivos`** (`tools/mcp-dispositivos/`, registrado em `.mcp.json`): servidor MCP que deixa um agente parear, conectar, compilar, instalar, capturar a tela, tocar e ler o log no celular e no relógio. Ferramentas: `listar_dispositivos`, `conectar`, `parear`, `descobrir_portas`, `registrar_dispositivo`, `reiniciar_adb`, `estado_tela`, `info_app`, `compilar`, `instalar`, `compilar_e_instalar`, `desinstalar`, `iniciar_app`, `parar_app`, `tocar`, `deslizar`, `tecla`, `texto`, `capturar_tela`, `logcat`, `adb_shell`.
- As armadilhas deste projeto ficam no código: celular sempre com `--user 0` (Dual App do Samsung), release que não atualiza debug (recusa e só desinstala com pedido explícito), porta do `adb` sem fio achada por varredura (o `mDNS` não funciona no WSL), reconexão automática do relógio, captura da tela ativa do Z Fold, e nunca contornar o bloqueio de tela.
- `AGENTS.md` e `docs/process/development-guide.md` mandam usar o MCP para os aparelhos físicos.

### Notes

- Os endereços dos aparelhos ficam em `~/.config/placar-dispositivos.json`, fora do repositório.
- O servidor fixa `mcp<2` (a 2.x renomeou a API).

### Verification

- `uv run pytest` (258, 33 do MCP com um `adb` falso) e `ruff`. Servidor testado com um cliente MCP real contra o Galaxy Z Fold e o Galaxy Watch: ferramentas listadas, `estado_tela`, `info_app`, `capturar_tela` (PNG válido da tela ativa) e `reboot` recusado.

## 0.29.0 - 2026-10-02

Boundary: CV7.US2 — relógio na quadra local do celular; fecha a CV7 (minor; backend, web e APK em 0.29.0, APK `versionCode` 4; Wear OS 0.27.0, `versionCode` 15).

Authors: Eli (Navigator); Claude Code (Driver) | Sessão: 014YCmLkudLSJamwqvTsmtEJ

Git source: merge `--no-ff` de `feature/cv7-us2-relogio-na-quadra-local` em `master`.

### Added

- Relógio na quadra local: com a sala local aberta no celular, o app do relógio a mostra sozinho (tag **LOCAL**), com o mesmo placar, a mesma fila offline durável e o mesmo desfazer de sempre, em fila própria. Marcar no relógio e no celular mantém os dois placares iguais; nova partida pelo relógio.
- O celular decide o modo (escolha do Navigator): publica `sala_aberta` e um sinal de vida a cada 20 s, e responde ao `ping` do relógio que abre. A quadra local ganha de uma quadra do servidor a que o relógio esteja vinculado.

### Changed

- `ScoreScreen` do relógio depende da interface `PlacarFonte` (servidor ou quadra local); o modo servidor não mudou.
- **Wear OS 0.27.0.** Continua com o `applicationId` `br.com.placarvolei` da 0.26.0 (desinstalar o antigo e revincular as quadras do servidor).

### Notes

- Sem sinal do celular por 90 s o relógio volta ao servidor, exceto com lances na fila: aí mantém a quadra local com o anel vermelho até enviá-los ou o celular fechar a sala (com a tela do celular apagada o sinal para).
- Dívida: `debt-relogio-local-sem-servico-em-primeiro-plano` (nova); `debt-quadra-local-so-atende-relogio-com-tela-acesa` atualizada.
- Para usar no relógio de produção: Wear 0.27.0 de release (assinado com a mesma keystore do celular) e revincular as quadras do servidor.
- `chore/apk-release-assinado`: o `release` do celular passa a ser assinado com a mesma keystore do relógio (fora do repositório). APKs de release 0.29.0 (celular) e 0.27.0 (relógio) gerados e instalados no Galaxy Z Fold e no Galaxy Watch SM-L330.

### Verification

- `npm test` (163), `npm run check`, `npm run test:e2e` (51), `uv run pytest` (225); relógio: 81 testes JVM, lint e APK debug. No Galaxy Z Fold e no Galaxy Watch SM-L330: relógio entra sozinho na quadra local, toques nos dois sentidos, saída e volta da sala, queda do app do celular.

## 0.28.1 - 2026-10-02

Boundary: CV7.TS3 — ponte Data Layer entre o celular e o relógio (patch no backend, web e APK em 0.28.1, `versionCode` 3; Wear OS 0.26.0, `versionCode` 14). Sem mudança visível: a tela do relógio para a quadra local é a CV7.US2.

Authors: Eli (Navigator); Claude Code (Driver) | Sessão: 014YCmLkudLSJamwqvTsmtEJ

Git source: merge `--no-ff` de `feature/cv7-ts3-ponte-data-layer` em `master`.

### Added

- Celular: a quadra local aplica os lances do relógio (`aplicarComandoRelogio`) com o contrato do servidor, recibos gravados com o log (reenvio sem duplicar, mesmo depois de reabrir o app), partida antiga recusada e desfazer por `alvo_seq` ou `alvo_comando`. Plugin `PlacarRelogio` e `RelogioListenerService` (Java) com a ponte JS, ligados enquanto a sala local está aberta.
- Relógio: `CelularLink`, respostas casadas por id e `CelularListenerService`; estado da quadra local por DataItem (sem a linha do tempo, abaixo do limite de ~100 KB). Disparador `DebugCelular` por `adb`, só nas builds debug.

### Changed

- **Wear OS 0.26.0:** o `applicationId` passa de `br.com.placarvolei.watch` para `br.com.placarvolei`, o mesmo do celular (o Data Layer exige o mesmo id e a mesma assinatura). Incompatível: é preciso desinstalar o app antigo do relógio e vincular as quadras do servidor de novo.

### Notes

- Plano B (Navigator): o spike mostrou que o JS do WebView para ~2 min depois de a tela apagar, mesmo com serviço em primeiro plano e wake lock parcial. A quadra local mantém a tela acesa; com ela apagada, a fila offline do relógio segura os lances e eles entram em ordem, uma vez só, quando o celular volta.
- Em release, celular e relógio precisam ser assinados com a mesma keystore.
- Dívida: `debt-quadra-local-so-atende-relogio-com-tela-acesa` (nova); `debt-apk-caminhos-nativos-sem-teste-automatico` e `debt-apk-release-sem-assinatura` atualizadas.

### Verification

- `npm test` (161), `npm run check`, `npm run test:e2e`, `uv run pytest` (225); relógio: 59 testes JVM, lint e APK debug. No Galaxy Z Fold e no Galaxy Watch SM-L330: ponto A/B e desfazer aplicados, lance enfileirado com o celular fora da sala e reenviado sem duplicar.

## 0.28.0 - 2026-10-02

Boundary: CV7.US1 — quadra local no celular (minor; backend, web e APK em 0.28.0, APK versionCode 2). O backend só alinha a versão.

Authors: Eli (Navigator); Claude Code (Driver) | Sessão: 014YCmLkudLSJamwqvTsmtEJ

Git source: merge `--no-ff` de `feature/cv7-us1-quadra-local` em `master`.

### Added

- Quadra local no APK: plano B quando não há comunicação com o servidor, uma por APK, com o log guardado no aparelho (`@capacitor/preferences`) e as regras da 0.27.1. Marcar, desfazer, duplas e regras, tema do placar, linha do tempo e nova partida, sem relógio, compartilhar nem lista de presentes. "Apagar quadra local" no ⚙.
- A tela inicial decide o modo pela conexão: servidor no ar libera só a quadra online; sem ele, só a local. Uma partida local em andamento continua acessível se a conexão voltar.

### Changed

- Teste de conexão do APK pela rede nativa (`CapacitorHttp`): só vale `200` com `status: ok` no `/health`. Um 502 do túnel com o backend fora conta como sem comunicação.
- Áreas seguras do sistema unificadas (`--sa-*`): a folha de ações e as demais ficavam cortadas pela barra de navegação do Android no APK.

### Fixed

- O resumo da quadra local na tela inicial não atualizava ao voltar da sala (Continuar ficava habilitado com a partida encerrada).

### Notes

- Dados ilegíveis da quadra local ficam guardados à parte e a pessoa decide ("Começar do zero"). Erro de leitura do aparelho não é tratado como dado ruim.
- Dívida: teste de conexão quitada; novas `debt-apk-caminhos-nativos-sem-teste-automatico`; crescimento da `SalaQuadra` registrado.

### Verification

- `npm test` (143), `npm run check`, `npm run test:e2e` (51), `uv run pytest` (225). Navigator validou no Galaxy Z Fold com o servidor de produção fora do ar.

## 0.27.1 - 2026-10-02

Boundary: CV7.TS2 — regras e projeção da partida em JS (patch; sem mudança visível; backend, web e APK em 0.27.1).

Authors: Eli (Navigator); Claude Code (Driver) | Sessão: 014YCmLkudLSJamwqvTsmtEJ

Git source: merge `--no-ff` de `feature/cv7-ts2-regras-e-projecao-em-js` em `master`.

### Added

- `web/src/lib/partida.js`: projeção do estado e da linha do tempo e comandos puros de ponto, desfazer, configurar e reiniciar, com as mesmas recusas do servidor. Base da quadra local do APK.
- Paridade Python↔JS: `tests/paridade_fixtures.py` gera fixtures a partir do backend real (9 logs à mão e 18 cenários, 8 deles aleatórios) e `web/tests/paridade.test.js` exige resultado idêntico. `tests/test_paridade_fixtures.py` falha se as fixtures ficarem para trás da regra em Python.
- Comando para regerar as fixtures: `uv run python -m tests.paridade_fixtures`.

### Verification

- `npm test` (129), `npm run check`, `uv run pytest` (225). Navigator validou quebrando a regra nos dois lados.

## 0.27.0 - 2026-10-01

Boundary: CV7.TS1 — casca Capacitor do APK Android (minor; web e APK 0.27.0, backend só alinha a versão).

Authors: Eli (Navigator); Claude Code (Driver) | Sessão: 014YCmLkudLSJamwqvTsmtEJ

Git source: merge `--no-ff` de `claude/scoreboard-improvements-ni7ols` em `master`.

### Added

- APK Android `br.com.placarvolei` (Capacitor 8) que embarca a web e abre a quadra online do servidor fixo do build (`PLACAR_SERVIDOR`), na mesma origem, sem mudar o backend. `scripts/build-apk.sh [debug|release]`.
- Tela inicial do APK testa `/health` e só libera "Abrir quadras online" se o servidor responder; senão mostra "Servidor indisponível" e "Testar de novo".
- Ícone do launcher com a bola do `favicon.svg`.
- ADR `apk-capacitor-e-quadra-local`, roadmap CV7 e dois itens de dívida (teste de conexão só detecta rede; release sem assinatura).

### Notes

- Instalar com `adb install -r --user 0`: sem isso o Samsung duplica o app no perfil Dual App.
- Versões: backend, web e APK em 0.27.0.

### Verification

- `npm test` (100), `npm run check`, `npm run test:e2e` (40), `uv run pytest` (224). Navigator validou o APK no Galaxy Z Fold.

## 0.26.1 - 2026-10-01

Boundary: patch da web (ajuste da CV6.DS1.US9 após uso em quadra); Wear segue em 0.25.0.

Authors: Eli (Navigator); Claude Code (Driver) | Sessão: 014YCmLkudLSJamwqvTsmtEJ

Git source: merge `--no-ff` de `claude/scoreboard-improvements-ni7ols` em `master`.

### Changed

- Destaque do último ponto permanente e forte, não só no pulso: moldura e fundo na cor da equipe, bolinha fixa (como no relógio), número 14% maior; o outro lado apagado e dessaturado. Todos conferem se o ponto foi para o lado certo.
- Faixa de sequência mais visível: bolinhas de 18 px numa pílula com fundo.
- Versões: backend e web 0.26.1.

### Verification

- `npm test` (97), `npm run check`, `npm run test:e2e` (36; `sequencia.spec.js` confere o destaque após o pulso nos dois clientes), `uv run pytest`. Navigator validou no celular.

## 0.26.0 - 2026-09-30

Boundary: minor da web e do backend (CV6.DS1.US9); Wear segue em 0.25.0.

Authors: Eli (Navigator); Claude Code (Driver, Passos 1–7) | Sessão: 014YCmLkudLSJamwqvTsmtEJ

Git source: merge `--no-ff` de `claude/scoreboard-improvements-ni7ols` em `master`.

### Changed

- O placar web destaca a equipe do último ponto: número maior e aceso, o outro apagado, com um pulso por ponto marcado (sem pulso no desfazer; parado com movimento reduzido). Temas esportivo e clássico, operador e espectador.
- Faixa de sequência sob o placar: uma bolinha por ponto ativo da partida atual, nas cores das equipes, a mais recente à direita. Desfazer remove a bolinha; partida nova limpa a faixa.
- Versões: backend e web 0.26.0.

### Verification

- `npm test` (97), `npm run check`, `npm run test:e2e` (36, incluindo `sequencia.spec.js` com dois clientes), `uv run pytest` (224). Navigator validou no celular.

## 0.24.1 - 2026-09-29

Boundary: patch da web (manutenção fora de história — tela do celular acesa entre partidas); Wear segue em 0.25.0.

Authors: Eli (Navigator); Claude Code, Opus 5.5 (Driver, Passos 1–7) | Sessão: b97ff9ae

Git source: merge `--no-ff` de `fix/tela-acesa-entre-partidas-2` em `master` (desenvolvida como 0.23.2 sobre base antiga, reaplicada sobre 0.25.0).

### Fixed

- A tela do celular apagava ao fim da partida e o relógio perdia a conexão. O Wake Lock agora fica ativo enquanto a sala da quadra estiver aberta, com ou sem partida em andamento, e só é liberado ao sair da sala.
- Versões: backend e web 0.24.1.

### Verification

- Build do web. Navigator validou no celular.

## 0.25.0 - 2026-09-28 (atualizado em 2026-09-29)

Boundary: minor do Wear OS (CV6.DS2.US4); backend e web permanecem em 0.24.0. Manutenção de testes e2e da web em 2026-09-29.

Authors: Eli (Navigator); Codex (Driver, US4); Antigravity (Driver, manutenção e2e) | Sessões: cv6-ds2-us3-us4-20260928; 22a7f4ef-3f50-406e-af46-16af48e95824

Git source: branch `feature/cv6-ds2-us4-repouso-e-retomada` e `fix/e2e-superficies-topo`, integradas em `master` com `--no-ff`.

### Changed

- Tela do placar respeita o repouso do sistema. Serviço foreground e Ongoing Activity mantêm a sessão e oferecem ações visíveis para voltar ao placar ou encerrar acompanhamento.
- Sessão do relógio sobrevive à pausa da Activity sem abrir proprietários concorrentes do WebSocket. A permissão de notificações é solicitada ao vincular.
- APK Wear 0.25.0 (versionCode 13); nenhuma mudança de protocolo, backend ou web.

### Fixed

- Testes e2e de superfícies (`superficies.spec.js`): alinhadas as expectativas com o topo da sala da 0.23.4 (uso de nome padrão sem repetir código e abertura de configurações no Fold fechado via menu `⋯` quando não couber no topo).

### Verification

- 59 testes do relógio passaram; builds debug/release e lint concluídos.
- 35/35 testes e2e do Playwright verdes, 96 testes unitários web, svelte-check sem erros, 224 testes pytest no backend e linters ruff 100% aprovados. CI do GitHub Actions verde.
- No Galaxy Watch SM-L330/Android 16, serviço foreground e WebSocket permaneceram ativos por 60 s em Dozing via ADB; Navigator aceitou essa evidência limitada.
- Gesto físico, atualização recebida durante repouso, queda de rede, treino ativo e bateria não foram observados. Animações e leitura de frequência cardíaca não são pausadas no repouso; limitações e follow-up constam no roteiro/revisão da US4.

## 0.24.1 - 2026-09-28

Boundary: patch do Wear OS (CV6.DS2.US3); backend e web permanecem em 0.24.0.

Authors: Eli (Navigator); Codex (Driver) | Sessão: cv6-ds2-us3-us4-20260928

Git source: branch `feature/cv6-ds2-us3-retorno-ao-pontuar`, integrada em `master` com `--no-ff`.

### Changed

- Ponto gravado no relógio destaca a equipe por 200 ms, vibra e solicita som de toque respeitando as preferências do sistema. Reenvios e snapshots não repetem esse retorno.
- Bola de vôlei persistente e animada identifica a equipe do último ponto válido, inclusive pendente; acompanha desfazer e pontos do telefone e some ao zerar. Compartilha o desenho da abertura e fica estática com animações desativadas.
- Equipe A azul e B laranja, títulos menores e nomes completos dos jogadores em linhas separadas. Posição da bola ajustada no Galaxy Watch pelo Navigator.
- APK 0.24.1 (versionCode 12) instalado no relógio, sem mudança de protocolo ou necessidade de reiniciar o servidor.

### Verification

- 59 testes do relógio passaram; builds debug/release e lint concluídos. Avisos de dependências/KTX permanecem.
- Navigator validou no aparelho e autorizou o fechamento. Roteiro e revisão na pasta da US3.
- Dívida de testes de tela Compose permanece; esta entrega não introduz dependências nem nova dívida estrutural identificada.

## 0.24.0 - 2026-09-28

Boundary: minor (fecha a CV3.DS1.US4, a CV3.DS1 e a CV3)

Authors: Eli (Navigator); Claude Code, Opus 5.5 (Driver, Passos 1–7) | Sessão: 9add80cf

Git source: merge `--no-ff` de `feature/cv3-ds1-us4-revisao-no-telefone` em `master`.

### Changed

- Relógio: conflito da fila offline (controle com outra pessoa, partida nova, placar mudado por fora ou vínculo encerrado) descarta a fila inteira e mostra por 3 s "N lances não enviados · motivo", voltando ao placar do servidor. Substitui a pausa com **Descartar** manual e a revisão pelo telefone que estava planejada (decisão `conflito-do-relogio-descarta-com-aviso`).
- Filas pausadas por versões anteriores são descartadas ao abrir o app, com o mesmo aviso.
- Roadmap: CV6.DS2.US2 marcada como Done (entregue na 0.22.1).
- Versões: backend e web 0.24.0; relógio 0.24.0 (versionCode 11).

### Verification

- 56 testes do relógio (6 novos), build e lint sem avisos novos. Servidor e web sem mudança de código. Navigator validou no relógio real.

## 0.23.4 - 2026-09-28

Boundary: patch (manutenção visual do topo da sala, fora de história)

Authors: Eli (Navigator); Claude Code, Opus 5.5 (Driver, Passos 1–7) | Sessão: 2c64122a

Git source: merge `--no-ff` de `fix/topo-prioridade-ajustes` em `master`.

### Changed

- ⚙ Duplas e regras e ⇄ Inverter lados entram na fila de prioridade do topo, à frente das demais ações; sem espaço, vão para o ⋯ por último. O código da sala é reservado inteiro e não é mais cortado.
- Regras no topo em três níveis: `10 pts com vantagem`, `10 pontos Ⓥ` ou `10 pts Ⓥ`, conforme o espaço.
- Versões: backend e web 0.23.4.

### Verification

- 96 testes unitários web, svelte-check sem erros e build. Testes de navegador ajustados, não executados nesta sessão. Navigator validou no Fold aberto e fechado.

## 0.23.3 - 2026-09-28

Boundary: patch (manutenção do fim de partida e do compartilhamento, fora de história)

Authors: Eli (Navigator); Claude Code, Opus 5.5 (Driver, Passos 1–7) | Sessão: 2c64122a

Git source: merge `--no-ff` de `feature/reinicio-rapido` em `master`.

### Changed

- Fim de partida: "Reinício Rápido" zera o placar e mantém duplas, regras e tema; "Ajustar e Iniciar" abre o modal de ajustes. Sai o "Compartilhar Resultado".
- Tocar no código da sala abre o compartilhamento (link e QR) em vez de copiar o código; "Compartilhar e QR" sai do ⋯ e dos atalhos do topo.
- Versões: backend e web 0.23.3.

### Verification

- 96 testes unitários web, svelte-check sem erros e build. Testes de navegador ajustados, não executados nesta sessão. Navigator validou.

## 0.23.2 - 2026-09-28

Boundary: patch (manutenção visual do topo da sala, fora de história)

Authors: Eli (Navigator); Claude Code, Opus 5.5 (Driver, Passos 1–7) | Sessão: 2c64122a

Git source: merge `--no-ff` de `fix/topo-sala-menu-e-codigo` em `master`.

### Changed

- Ações do ⋯ sobem para o topo quando há espaço, nesta prioridade: modo sol/escuro, relógio, linha do tempo, números, compartilhar e girar. O ⋯ fica com o que não coube e com os presentes.
- Código da sala em duas linhas: `#código` em cima e o nome menor embaixo; sem nome próprio (vazio ou `Quadra #código`), só o código.
- Regras no topo: `10 pts com vantagem` quando há espaço; senão `10 pts` com o selo Ⓥ, aceso com vantagem e apagado sem.
- Versões: backend e web 0.23.2.

### Fixed

- Tipo do estado em `resumirRegrasCurto` (3 erros do svelte-check).

### Verification

- 96 testes unitários web, svelte-check sem erros e build. Testes de navegador ajustados, não executados nesta sessão. Navigator validou no Fold e no desktop.

## 0.23.1 - 2026-09-28

Boundary: patch (manutenção fora de história — limpar nomes das equipes)

Authors: Eli (Navigator); Claude Code, Opus 5.5 (Driver, Passos 1–7) | Sessão: 0886f1e8-8abe-4d50-9a13-a03a795ce8f7

Git source: merge `--no-ff` de `feature/limpar-nomes-equipe` em `master` (desenvolvida como 0.22.3, renumerada após 0.23.0).

### Added

- Botão "Limpar" nos jogadores de cada equipe: esvazia os dois nomes de uma vez. Salvar após limpar volta ao nome padrão ("Equipe A"/"Equipe B"); cancelar mantém os nomes.
- Versões: backend e web 0.23.1.

### Verification

- Build e `e2e/atalhos.spec.js` (2/2, esportivo e clássico). Navigator validou.

## 0.23.0 - 2026-09-28

Boundary: minor (CV6.DS1.US7 — pontuação por slider, topo curto e selo de papel; CV6.DS1.US8 — admin libera a quadra)

Authors: Eli (Navigator); Claude Code, Opus 5.5 (Driver, Passos 1–7) | Sessão: 5bfc5c62

Git source: merge `--no-ff` de `feature/cv6-ds1-us7-us8-pontuacao-e-liberar-quadra` em `master`.

### Added

- Admin libera a quadra no ⚙, com confirmação: a quadra some na hora e todos os aparelhos voltam à tela inicial (`POST /api/quadras/{id}/liberar`, só admin).
- Selo do papel em caixinha no topo, Ⓐ admin ou Ⓒ controlador, com dica ao tocar.

### Changed

- Alvo padrão passa de 12 para 10 pontos. Quadras existentes mantêm o alvo.
- Pontuação por slider de 6 a 20; Personalizado aceita inteiro de 1 a 100 e desliga o slider.
- Topo curto: `10 pts · +2 · até 15`; o texto por extenso fica no leitor de tela.
- Versões: backend e web 0.23.0.

### Verification

- 224 testes Python, 96 unitários web, svelte-check, build e 34 testes de navegador (novo `e2e/liberar-e-selo.spec.js`). Navigator validou no Fold.

## 0.22.3 - 2026-09-28

Boundary: patch (manutenção visual da sala, fora de história)

Authors: Eli (Navigator); Claude Code (Driver) | Sessão: session_018HHNpGHW3MAqyaYZzNwmse

Git source: merge `--no-ff` de `claude/placar-classico-melhorias-wnyd4f` em `master`.

### Changed

- Placar clássico: o × ganhou o divisor do esportivo (X em SVG sobre linha em degradê; horizontal com a tela em pé).
- O aviso "Enviando o toque…" saiu de cima do placar. Lances a sincronizar aparecem como número dentro da bolinha de conexão do topo (como o `↑N` do relógio), e o leitor de tela ouve a quantidade no rótulo.
- Bolinha de conexão maior (24px; pílula de 28px com fila) e, quando conectada, onda de pulso vazando para fora.
- Versões: backend e web 0.22.3.

### Verification

- 94 testes unitários web, svelte-check, build e 31 testes de navegador aprovados. Navigator validou.

## 0.22.2 - 2026-09-27

Boundary: patch (manutenção visual da sala, fora de história)

Authors: Eli (Navigator); Claude Code, Opus 5.5 (Driver) | Sessão: a56a1487-0857-48f4-b41d-683dee5accbe

Git source: merge `--no-ff` de `fix/ajustes-visuais-sala` em `master`.

### Changed

- Voltar e status do topo viram botões redondos; voltar com chevron em SVG e status com bolinha maior (18px).
- Divisor do placar: × sem círculo, maior e mais grosso, cinza cheio no centro e sumindo nas pontas, sobre uma linha vertical com o mesmo degradê.


## 0.22.1 - 2026-09-27

Boundary: patch (CV6.DS2.US2 — conexão indicada por aro discreto)

Authors: Eli (Navigator); Codex (Driver, Passos 1–2) | Sessão: cv6-ds2-us2-20260927; Claude Code, Opus 5.5 (Driver, Passos 3–7, assumido do Codex)

Git source: merge `--no-ff` de `feature/cv6-ds2-us2-aro-de-conexao` em `master`.

### Changed

- Relógio: a bolinha de conexão virou um aro fino na borda da tela (verde conectado, amarelo reconectando/enviando, vermelho sem conexão). Batimentos sozinhos no centro; lances pendentes aparecem como `↑N` só quando existem. O leitor de tela ouve o estado e a quantidade de pendentes no cabeçalho. O aro não recebe toque.
- Versões: backend e web 0.22.1; app do relógio `versionName` 0.22.1 (`versionCode` 10).

### Verification

- 53 testes JVM do relógio, builds debug/release e lint Android aprovados. Navigator validou no Galaxy Watch.

## 0.22.0 - 2026-09-27

Boundary: minor (CV6.DS1.US6 — atalhos de ajuste no placar)

Authors: Eli (Navigator); Claude Code (Driver, Passos 1–7) | Sessão: session_0116vQyfn2t4ewHrNfdCCTkk

Git source: merge `--no-ff` de `feature/cv6-ds1-us6-atalhos-no-placar` em `master`.

### Added

- Tocar no resumo de regras do topo abre só Pontuação e Vantagem; tocar no nome da equipe (esportivo e clássico) abre só os jogadores dela. Tocar fora fecha sem salvar. Mesma permissão do ⚙; o espectador não tem atalho.

### Fixed

- No esportivo, o número gigante cobria o nome da equipe e engolia o toque.

### Verification

- 93 testes unitários web, svelte-check, build e 31 testes de navegador (novo `e2e/atalhos.spec.js`) aprovados. Navigator validou.

## 0.21.1 - 2026-09-27

Boundary: patch (ajuste da CV6.DS1.US3 no placar clássico; fechamento documental da CV2.DS3.TS1)

Authors: Eli (Navigator); Claude Code (Driver) | Sessão: session_0116vQyfn2t4ewHrNfdCCTkk

Git source: merges `--no-ff` em `master` de `claude/hus-fora-relogio-pgvzgt` e `feature/cv6-ds1-us3-escala-no-classico`.

### Changed

- Tamanho dos números P/M/G (menu ⋯) também no placar clássico: o número do cartão acompanha a tela, cresce com a escolha e fica sempre dentro do cartão, inclusive com três dígitos e em tela em pé. No clássico, P deixa de ser o antigo tamanho fixo.
- CV2.DS3.TS1 (tokens e cores semânticas) registrada como `Done` com aceite do Navigator.

### Verification

- Testes unitários web, svelte-check e build aprovados; novo e2e mede P/M/G do clássico no tablet e no Fold fechado. Navigator validou.

## 0.21.0 - 2026-09-27

Boundary: minor (CV6.DS1 — placar web mais legível e fácil de operar; 5 histórias)

Authors: Eli (Navigator); Claude Code, Opus 5.5 (Driver, Passos 1–7 de cada história) | Sessão: 8fcca862-38a5-4f3d-ad4e-e8e690004f76

Git source: merges `--no-ff` em `master` das branches `feature/cv6-ds1-us1-cabecalho-compacto`, `feature/cv6-ds1-us2-controles-inferiores`, `feature/cv6-ds1-us5-ajustes-espacosos` e `feature/cv6-ds1-us3-numeros-ajustaveis`. A US4 foi coberta pela US1.

### Changed

- Topo da quadra em uma linha para operador e espectador: voltar, código, regras da partida, ajustes (⚙), inverter lados (⇄), menu e status. Status vira bolinha em caixa no canto direito: verde pulsante, amarela (reconectando) ou vermelha (aparelho sem rede), com nome acessível. "Duplas e regras" sai do menu para o ⚙; ⇄ e ⋯ saem de dentro do placar. "Você está no controle" dá lugar ao resumo "12 pontos · Vantagem" (`CV6.DS1.US1`, merge de `feature/cv6-ds1-us1-cabecalho-compacto`).
- Pontuar e desfazer embaixo do placar: +1 / Desfazer / +1 no tablet e no Fold aberto; Desfazer na linha de baixo em tela estreita. Os +1 deixam as laterais em paisagem (`CV6.DS1.US2`, merge de `feature/cv6-ds1-us2-controles-inferiores`).
- Configurações da partida com Pontuação primeiro, margem interna, modal mais largo no tablet e Salvar/Cancelar sempre visíveis, inclusive no Fold fechado com teclado aberto (`CV6.DS1.US5`, merge de `feature/cv6-ds1-us5-ajustes-espacosos`).
- Tela em pé empilha as equipes, uma sobre a outra, com números bem maiores no Fold fechado. Tamanho dos números P/M/G só no aparelho, pelo menu ⋯: P é o tamanho anterior, M (padrão) +25%, G +50%, sempre dentro da coluna (`CV6.DS1.US3`, merge de `feature/cv6-ds1-us3-numeros-ajustaveis`).
- Regras da partida visíveis no topo para quem opera; o espectador já as via no placar (`CV6.DS1.US4`, coberta pela US1).

### Fixed

- Teste de axe media contraste durante fades e falhava de forma intermitente; agora espera as animações finitas.

## 0.20.1 - 2026-09-27

Boundary: patch (CV6.DS2.US1 — leitura e operação mais claras no relógio)

Authors: Eli (Navigator); Codex (Driver, Passos 1–7)

Git source: merge commit `ed4502d` de `feature/cv6-ds2-us1-leitura-no-pulso` em `master`.

### Changed

- Números do placar no relógio usam Teko local e se ajustam para caber de 0 a três dígitos no mostrador circular.
- Batimentos ficam centralizados no topo, com `♥ --` sem leitura e indicador oculto sem permissão.
- Controle no telefone usa a mensagem curta **Controle no telefone.**.
- Correção usa **Voltar Ponto**, mantendo a equipe na descrição acessível; **Nova** fica verde e continua protegida por dois toques.
- README, briefing, documentação Wear OS, decisão, worklog e roteiro de validação foram alinhados ao comportamento entregue.

### Verification

- 52 testes JVM do relógio, 221 testes backend, build debug/release, lint Android e Svelte Check aprovados.
- Navigator validou a leitura e os fluxos no Galaxy Watch SM-L330; release instalado sem apagar o vínculo.
- Permanece Carried a dívida de testes automatizados da tela do relógio.

## 0.20.0 - 2026-09-27

### Documentação posterior à entrega — 2026-09-27

- Consolidação aceita pelo Navigator: nove HUs planejadas em [CV6 — Ajustes de uso em quadra](docs/project/roadmap/cv6-ajustes-de-uso-em-quadra/index.md), cobrindo navegador e relógio. Desenvolvimento e validação do produto permanecem futuros; sem alteração de versão.
- Git source: `codex/docs-feedback-telas-20260927`; merge em `master` autorizado pelo Navigator.
- Agente: Codex (Driver) | Sessão: 01a0e3cc-4e34-7061-8559-a9949280d6f0 | Data: 2026-09-27.
- Verificação documental: 12 documentos, links relativos válidos e `git diff --check` sem erros.

Boundary: minor (CV5 — robustez, segurança e acessibilidade; 13 histórias)

Authors: Eli (Navigator); Claude Code, Opus 5.5 (Driver, Passos 1–7, automode autorizado pelo Navigator) | Sessão: 51cc5422-0716-48a4-a737-c2ae18bfcf4d

Git source: `integracao/cv5` (merge das branches `feature/cv5-*`), integrada em `master` após o Checkpoint 4.

### Added

- Servidor manda `PING` pelo WebSocket a cada 20 s; o navegador reconecta após 45 s de silêncio e na hora ao voltar para a aba ou para a rede (`CV5.DS3.US1`).
- Relógio: "▶ Nova" em dois toques, desfazer que mostra a equipe (`+1 Nós`), aviso de fila ilegível e build de release com R8 e assinatura (`CV5.DS4.US1`, `CV5.DS2.TS1`, `CV5.DS2.TS4`).

### Changed

- Limites de tentativa pelo IP real (`CF-Connecting-IP` com `TRUST_CLOUDFLARE`), limite de códigos de sala errados em `/entrar`, PIN com `secrets`. O lobby continua público: o PIN identifica a sala e não a protege (`CV5.DS1.TS1`).
- `OWNER_SECRET` obrigatório e recusado com o valor de exemplo em produção; cookie `Secure`; `/health` sem o caminho do banco; banco apagado a cada start do contêiner (decisão do Navigator) (`CV5.DS1.TS2`).
- Broadcast paralelo com prazo de 2 s por socket (`CV5.DS3.TS1`); limpeza de salas apaga os recibos do relógio e os locks; a listagem não disputa o lock de escrita (`CV5.DS1.TS3`).
- Relógio: gravação da fila fora da thread da tela, 408/425/429 sem travar a fila, sensor e polling desligados quando não precisam, tela liberada após 10 min parado, `targetSdk` 36 com a permissão granular de batimento (`CV5.DS2.TS2`, `CV5.DS2.TS3`, `CV5.DS2.TS4`).
- Web: Linha do Tempo no `Dialogo` nativo, regiões vivas estáveis, movimento reduzido global, "Reconectando…" como único estado de conexão, "{nome} venceu!", selo de papel legível e apelido numa chave só (`CV5.DS4.US2`, `CV5.DS4.US3`).

### Fixed

- QR do "Compartilhar" nunca aparecia (assinatura errada de `gerarQrCode`).
- Backoff de reconexão do web zerava a cada tentativa.
- "Copiado!" aparecia mesmo quando a cópia falhava; um 502 do túnel virava "Unexpected token <".

### Development

- `lib/conexao.js` e `lib/tema.js` extraídos e testados; `@ts-check` nos módulos de lógica (`CV5.DS5.TS1`).
- Débitos: `debt-banco-de-producao-sem-volume-persistente` virou Dropped; `debt-limite-de-vinculo-do-relogio-por-ip-e-em-memoria` pago em parte; novo `debt-sala-quadra-grande-e-props-sem-tipo`.

### Verification

- Backend: 221 testes; ruff limpo. Web: svelte-check sem erros nem avisos, `node --test` e build. Relógio: testes JVM, lint, APK de debug e de release. Imagem Docker compilada.
- Produção (0.20.0): owner com `X-Forwarded-For` trocado → 429; 21 códigos errados → 429; cookie `Secure`; `/ws/abc` recusado; `PING` aos 20 s. O Navigator validou o restart com banco limpo e a mensagem legível num 502.

## 0.19.0 - 2026-09-26

Boundary: minor (fila offline do relógio com placar persistido; conclui `CV3.DS1.TS1`)

Authors: Eli (Navigator); Claude Code, Opus 5.5 (Driver, Passos 1–2) | Sessão: session_01SeCZMypfz5yGenXJ6UNy66; Claude Code, Opus 5.5 (Driver, Passos 3–7) | Sessão: 9c609b1a-8c8a-449c-84cd-7c42bcc4f75b

Git source: `feature/cv3-ds1-us4-offline-reconciliacao`, integrada em `master` pelo merge `b5e71f4` após o Checkpoint 4.

### Added

- Relógio reaberto sem rede mostra o último placar confirmado e segue marcando; a fila sincroniza ao reconectar, um efeito por lance.
- Controle devolvido ao relógio com a partida inalterada: a fila pendente é aplicada em vez de retida (`base_seq`).

### Changed

- Versão exibida alinhada em 0.19.0 no backend, no web e no APK (estavam em 0.10.1 e 0.12.0).

### Development

- `ScoreSync` extraída do `WatchModel`, com testes de servidor falso; fixture e helpers do relógio em `tests/watch_support.py`.
- Dívida `fluxos-da-interface-sem-teste-de-ponta-a-ponta` paga em parte.

### Verification

- Backend: 198 testes; ruff limpo. Relógio: 44 testes unitários, build e lint.
- Cinco cenários físicos validados pelo Navigator em 2026-09-26.

## 0.18.1 - 2026-09-26

Boundary: patch (regressão, acessibilidade e CI; conclui `CV4.DS3.TS1`, `CV4.DS3` e o CV4)

Authors: Eli (Navigator); Claude Code, Opus 5.5 (Driver, Passos 1–7) | Sessão: session_01SeCZMypfz5yGenXJ6UNy66

Git source: `feature/cv4-ds3-ts1-regressao`, integrada em `master` pelo merge `535fbc3` após o Checkpoint 4.

### Fixed

- A aplicação não carrega mais o Google Fonts: Inter e Teko já eram locais e o link externo sobrava no `index.html`.

### Development

- Suíte de navegador `npm run test:e2e` (Playwright 1.56.1 e axe 4.13.0, só desenvolvimento): 24 testes cobrindo espectador, operador, superfícies, axe nos dois temas e ausência de requisições externas.
- CI no GitHub Actions a cada push e pull request: pytest, ruff, `npm test`, `svelte-check`, build e navegador.
- Dívida de contraste do Modo Sol paga; nova dívida `testes-estaticos-dependem-do-build`.

### Verification

- Backend: 191 testes; frontend: 66 testes unitários e 24 de navegador; Svelte sem avisos.
- CI verde (run #3, `a9b2354`).
- Rota V6 e matriz física aprovadas pelo Navigator em 2026-09-26.

## 0.18.0 - 2026-09-26

Boundary: minor (superfícies auxiliares e estados coerentes; conclui `CV4.DS3.US2`)

Authors: Eli (Navigator); Claude Code, Opus 5.5 (Driver, Passos 1–7) | Sessão: session_01SeCZMypfz5yGenXJ6UNy66

Git source: `feature/cv4-ds3-us2-superficies`, integrada em `master` pelo merge `834278e` após o Checkpoint 4.

### Added

- Menu ⋯ também para o espectador (compartilhar/QR, girar, tema e presentes), compartilhado com o operador em `MenuSala.svelte`.
- Diálogos devolvem o foco a quem os abriu e mantêm o campo focado visível com o teclado virtual.

### Changed

- Cabeçalho do espectador: voltar, tela cheia, ⋯ e conexão.
- Selos de papel (admin, controlador, espectador) neutros, sem as cores das equipes.

### Removed

- Botões de tema, compartilhar, inverter e girar do cabeçalho do espectador (cada ação ficou num lugar só) e a lista de presentes sobreposta ao placar.

### Verification

- Backend: 191 testes aprovados.
- Frontend: 66 testes aprovados, Svelte com zero erros/advertências e build de produção concluído.
- Chromium headless com dois clientes: foco de retorno, menus por papel, 360 px sem estouro, campo visível em 390×380 e vitória nos dois clientes.
- Rota V5 validada pelo Navigator em 2026-09-26.

## 0.17.0 - 2026-09-26

Boundary: minor (operação a um toque para admin e controlador; conclui `CV4.DS3.US1`)

Authors: Eli (Navigator); Claude Code, Opus 5.5 (Driver, Passos 1–7) | Sessão: session_01SeCZMypfz5yGenXJ6UNy66

Git source: `feature/cv4-ds3-us1-controle`, integrada em `master` pelo merge `8063c75` após o Checkpoint 4.

### Added

- Faixa de posse do controle, separada do papel, com **Assumir** quando cabe.
- Menu ⋯ único com compartilhar/QR, duplas e regras, linha do tempo, relógio, tema e presentes (promover, revogar, passar controle).
- Desfazer indica o ponto que será anulado ("último: +1 Equipe").

### Changed

- Operação cabe numa tela sem rolagem: barra compacta com código e conexão; +1 sob cada equipe, nas laterais em paisagem, seguindo a inversão de lados.
- Sem o controle, os +1 aparecem desabilitados em vez de sumir; papel aparece em selo neutro.
- No tema Clássico, a operação usa a mesma representação do espectador.

### Removed

- Card de código da sala, cartão "conectado como" e botões repetidos (Duplas & Regras, Inverter, QR, Linha do Tempo).

### Verification

- Backend: 191 testes aprovados.
- Frontend: 63 testes aprovados, Svelte com zero erros/advertências e build de produção concluído.
- Chromium headless com dois clientes: sem rolagem em 390×844 e 1066×600, inversão dos +1, troca de posse e chamada forjada sem controle recusada (403).
- Rota V4 validada pelo Navigator em 2026-09-26.

## 0.16.0 - 2026-09-26

Boundary: minor (tela cheia real e imersão estável do espectador; conclui `CV4.DS2.US2` e a `CV4.DS2`)

Authors: Eli (Navigator); Claude Code, Opus 5.5 (Driver, Passos 1–7) | Sessão: session_01SeCZMypfz5yGenXJ6UNy66

Git source: `feature/cv4-ds2-us2-imersao`, integrada em `master` pelo merge `492d798` após o Checkpoint 4.

### Added

- Botão **Tela cheia** para o espectador: pedido feito no próprio toque, estado confirmado pelo navegador e aviso claro em caso de recusa ou falta de suporte.
- Módulo `web/src/lib/telaCheia.js`, testável sem navegador.

### Changed

- Controles do espectador sobrepõem o placar: revelar ou esconder não move os pontos.
- O toque que revela os controles não aciona o botão que surge sob o dedo.
- A ocultação automática (3 s) espera diálogo aberto, foco de teclado e avisos.

### Verification

- Backend: 191 testes aprovados.
- Frontend: 54 testes aprovados, Svelte com zero erros/advertências e build de produção concluído.
- Chromium headless: posição do placar idêntica ao revelar controles em 360×640, 390×780 e 1066×600; entrada, saída e recusa de tela cheia.
- Validação física no Fold aprovada pelo Navigator em 2026-09-26. Tablet segue na matriz física da `CV4.DS3.TS1`.

## 0.15.0 - 2026-09-26

Boundary: minor (temas de placar escolhidos pelo administrador; conclui `CV4.DS2.US3`)

Authors: Eli (Navigator); Codex (Driver, Passos 1–3) | Sessão: 01a0dd8e-b3b3-7482-a278-5f22f9738d3e; Claude Code, Opus 5.5 (Driver, Passos 3–7) | Sessão: 97b0d6cb-d126-47e1-abd8-f3528d3bf7b0

Git source: `feature/cv4-ds2-us3-temas-placar`, integrada em `master` pelo merge `59c389d` após o Checkpoint 4.

### Added

- Temas visuais **Esportivo** (padrão) e **Clássico**, escolhidos pelo administrador nas configurações, persistidos na sala e aplicados na hora a administradores, controladores e espectadores.
- Representação clássica reutilizável (`PlacarClassico`), sem regras nem transporte.

### Changed

- O indicador **Ao vivo** tem a mesma altura dos demais controles do cabeçalho.
- Claro/escuro continua preferência local do aparelho, independente do tema do placar.

### Verification

- Backend: 191 testes aprovados; Ruff check e format check aprovados.
- Frontend: 45 testes aprovados, Svelte com zero erros/advertências e build de produção concluído.
- Validação manual aprovada pelo Navigator em 2026-09-26.

## 0.14.0 - 2026-09-26

Boundary: minor (placar esportivo responsivo do espectador; conclui `CV4.DS2.US1`)

Authors: Eli (Navigator); Codex (Driver) | Sessão: 01a0dd8e-b3b3-7482-a278-5f22f9738d3e

Git source: `feature/cv4-ds2-us1-placar-espectador`, integrada em `master` após o Checkpoint 4.

### Added

- Resultado visual reutilizável, sem dependência de transporte ou permissões, com pontos dominantes e escala pela área disponível.
- Escala própria para placares de três dígitos, feedback curto de atualização e anúncio acessível.

### Changed

- O espectador passa a usar painel esportivo em lugar do cavalete retrô; identificação e regras ficam compactas.
- A composição imersiva ocupa toda a altura útil e preserva tema, sessão, resultado, inversão local e linha do tempo.

### Verification

- Backend: 185 testes aprovados; Ruff check e format check aprovados.
- Frontend: 39 testes aprovados, Svelte com zero erros/advertências e build de produção concluído.
- Inspeção visual com sala isolada nos temas claro e escuro, em 658 × 781 e 1066 × 600 CSS px; escala final aprovada pelo Navigator.
- A matriz física completa de Fold e tablet permanece em `CV4.DS3.TS1`.

## 0.13.2 - 2026-09-26

Boundary: patch (ajuste de alinhamento e proporção na Home)

Authors: Eli (Navigator); Codex (Driver) | Sessão: 01a0dd8e-b3b3-7482-a278-5f22f9738d3e

Git source: `fix/home-alinhamento-codigo-abrir`, aprovada pelo Navigator.

### Fixed

- Código da quadra centralizado sem recuo tipográfico adicional.
- Ação **Abrir** sem seta, com texto maior e preenchimento integral da última coluna.

### Verification

- Frontend: 32 testes aprovados, Svelte com zero erros/advertências, build concluído e validação visual aprovada em 658 px.

## 0.13.1 - 2026-09-26

Boundary: patch (restaura a alternância de tema da Home)

Authors: Eli (Navigator); Codex (Driver) | Sessão: 01a0dd8e-b3b3-7482-a278-5f22f9738d3e

Git source: `fix/home-tema-claro-escuro`, hotfix autorizado pelo Navigator.

### Fixed

- O botão Claro/Escuro volta a aplicar e persistir o tema correto. O modo claro agora escreve `data-tema="sol"`, valor esperado pelos tokens, e o modo escuro remove o atributo.

### Verification

- Frontend: 32 testes aprovados, Svelte com zero erros/advertências e build de produção concluído.

## 0.13.0 - 2026-09-26

Boundary: minor (nova experiência de entrada e partidas ativas; fecha a CV4.DS1)

Authors: Eli (Navigator); Codex (Driver) | Sessão: 01a0dd8e-b3b3-7482-a278-5f22f9738d3e

Git source: `codex/cv4-ds1-us1-home`, integrada em `master` após o Checkpoint 4.

### Added

- Home em painel esportivo (`CV4.DS1.US1`) com entrada por código como ação inicial, criação preservada e composição responsiva para telefone, Fold, tablet e computador.
- Cards de partidas ativas em três colunas: metadados compactos, placar Teko dominante e ação **Abrir** ocupando a coluna final.
- Identificação textual do tema Claro/Escuro e uso integral de fontes e ícones locais.

### Fixed

- Recusas ao entrar por uma partida ativa agora mantêm a aba Acompanhar, preservam o código, mostram o erro junto ao formulário e devolvem o foco ao apelido.

### Debt

- Pago: `debt-erro-de-entrada-pela-home-fora-da-vista`.

### Verification

- Backend: 185 testes aprovados; Ruff check e format check aprovados.
- Frontend: 31 testes aprovados, Svelte com zero erros/advertências e build de produção concluído.
- Inspeção visual em 658, 904 e 1440 px; quatro rodadas de validação no navegador aprovadas pelo Navigator.

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
- **Passo Ariad**: Passo <N> - <Nome do Passo> (ex: Passo 6 - Documentação)
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
