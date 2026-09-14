# Changelog

This project records only closed versions.

The Driver updates this file when a release boundary is accepted and a version is closed. Do not maintain an always-open `Unreleased` section here. Use the roadmap, worklog, or release-candidate notes for work that is still in motion.

Each closed version should name:

- the version and release date;
- the release boundary that closed, such as Value / CV, Delivery Story, User Story, Technical Story, or Maintenance;
- the people, agents, or runtimes who made the change;
- the relevant Git source, such as commit range, tag, pull request, or merge commit;
- the changes that matter to users, operators, contributors, or future agents.

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

## Template

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
