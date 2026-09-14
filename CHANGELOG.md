# Changelog

Este changelog registra tanto o **trabalho ativo em andamento** (para coordenação multi-agente e handoff) quanto as **versões fechadas**.

A seção `## [Em Andamento]` no topo do arquivo rastreia todas as branches ativas geradas a partir da branch principal (`main`/`master`). Todo novo desenvolvimento deve ser registrado aqui com a branch, a história, o passo atual do ciclo Ariad, a assinatura do agente responsável e notas de handoff.

Quando uma história é validada e integrada na `main`, seu registro é removido de `[Em Andamento]` e incorporado à versão fechada correspondente.

## [Em Andamento]

*(Nenhum desenvolvimento ativo no momento)*

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
