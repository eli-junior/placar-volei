---
status: Superseded
raised: 2026-09-14
decided: 2026-09-14
deciders:
  - Navigator
  - Driver
superseded_by: 2026-09-15T1730Z-remocao-de-arenas-e-banco-limpo-no-versionamento
supersedes:
related:
  - CV1.DS1.TS3
  - CV1.DS1.US1
---

# Preservação de Arenas e Quadras por Fixtures Declarativas em JSON

## Question

Como permitir que o banco de dados SQLite local seja limpo ou descartado sem perder os nomes de arenas e suas quadras já cadastradas?

## Decision

Adotar o arquivo `defaultArenas.json` na raiz do repositório como fonte declarativa de persistência para nomes de arenas e quadras.

1. **Auto-seeding na inicialização:** Ao rodar `init_db_sync()`, a aplicação verifica se as arenas e quadras contidas em `defaultArenas.json` já existem no SQLite. Se não existirem, popula-as automaticamente com partidas ativas e eventos iniciais.
2. **Atualização contínua:** Ao registrar uma nova arena ou quadra via API, a aplicação atualiza o `defaultArenas.json` no disco de maneira atômica (`os.replace`), deixando-o pronto para ser versionado no Git.
3. **Isolamento de dados efêmeros:** Participantes, cookies, eventos de pontos e partidas arquivadas continuam sendo dados descartáveis no SQLite.

## Rationale

- Em desenvolvimento e em ambiente doméstico no Mini PC, o arquivo `placar.db` pode ser recriado com frequência para testes ou limpezas de partidas antigas.
- Digitar novamente todas as arenas e quadras a cada limpeza gera atrito desnecessário.
- Manter o arquivo na raiz do repositório permite que ele seja commitado e compartilhado via GitHub de forma transparente, sem violar a política de permissões ou expor credenciais no runtime.

## Options Considered

- **Backup completo do SQLite:** Rejeitado: preservaria participantes e partidas antigas que o Navigator explicitamente prefere descartar.
- **Commit automático via Git no runtime da API:** Rejeitado: geraria instabilidade na execução, exigiria credenciais Git dentro do contêiner Docker e violaria a política do Navigator de aprovar commits e pushes.
- **Seeds fixos hardcoded no código Python:** Rejeitado: tornaria a criação de novas arenas pela UI ineficaz na preservação durável.

## Consequences

- O arquivo `defaultArenas.json` passa a ser rastreado pelo Git.
- Novas arenas e quadras criadas na UI aparecem no `git status` para serem commitadas quando desejado.
- Ambientes de teste automatizado isolam a fixture via `conftest.py` para não sobrescrever os dados reais do projeto.
