# Changelog

Este changelog registra tanto o **trabalho ativo em andamento** (para coordenação multi-agente e handoff) quanto as **versões fechadas**.

A seção `## [Em Andamento]` no topo do arquivo rastreia todas as branches ativas geradas a partir da branch principal (`main`/`master`). Todo novo desenvolvimento deve ser registrado aqui com a branch, a história, o passo atual do ciclo Ariad, a assinatura do agente responsável e notas de handoff.

Quando uma história é validada e integrada na `main`, seu registro é removido de `[Em Andamento]` e incorporado à versão fechada correspondente.

## [Em Andamento]

### feature/cv1-ds3-us2-jogadores-das-equipes-e-inversao-de-lados
- **História / Escopo**: CV1.DS3.US2 — Nomes de jogadores nas equipes (1 ou 2 por time) e inversão de lados na quadra
- **Branch**: `feature/cv1-ds3-us2-jogadores-das-equipes-e-inversao-de-lados`
- **Passo Ariad**: Passo 6 - Documentação
- **Assinatura do Agente**: Agente: Antigravity (Driver) | Sessão: 7bb92112-8818-44ae-87d5-4e2d9a077f33 | Data: 2026-09-14 22:50
- **Handoff / Próximos Passos**: Atualizar roadmap, documentação da história, worklog e realizar Coherence Check.

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
