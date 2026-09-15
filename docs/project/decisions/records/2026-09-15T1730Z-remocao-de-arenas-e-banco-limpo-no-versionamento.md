---
status: Decided
raised: 2026-09-15
decided: 2026-09-15
deciders:
  - Navigator
  - Driver
supersedes:
  - 2026-09-14T1005Z-fixtures-declarativas-de-arenas.md
  - 2026-09-13T2005Z-arenas-como-agrupador-de-quadras.md
related:
  - 2026-09-14T1625Z-salas-por-codigo-pin-de-5-digitos.md
---

# Remoção Definitiva de Arenas/Fixtures e Garantia de Banco Limpo no Versionamento

## Question

Como garantir que novas versões da aplicação iniciem em estado completamente limpo (zero quadras ativas), eliminando de vez o resíduo do modelo legado de arenas e o auto-seeding de fixtures?

## Context

Na versão 0.2.0, o produto simplificou radicalmente a entrada dos usuários: adotou-se o modelo direto de "Criar Placar" e "Acompanhar" com código PIN numérico de 5 dígitos gerado sob demanda.

No entanto, a tabela `arenas` no SQLite, rotas `/api/arenas/*` e principalmente o mecanismo de fixtures declarativas (`fixtures/defaultArenas.json` e rotina `sincronizar_fixtures_para_db_sync`) continuaram no repositório como débito técnico. Ao subir uma versão nova, embora a aplicação apagasse o `placar.db` anterior, a rotina de inicialização recriava imediatamente 12 quadras ativas a partir da fixture, poluindo a instância.

## Decision

1. **Remoção Total de Arenas e Fixtures:**
   - Exclusão do arquivo de fixtures `fixtures/defaultArenas.json` e do módulo `app/fixtures.py`.
   - Exclusão da tabela `arenas` e do campo `arena_id` do schema SQLite em `app/db.py`.
   - Exclusão das rotas `/api/arenas/*` e de componentes órfãos no frontend.
2. **Garantia de Banco 100% Limpo:**
   - Na inicialização ou na detecção de nova versão (`app_meta.versao != settings.version`), o banco SQLite é recriado do zero estritamente vazio: 0 quadras, 0 participantes, 0 eventos.
   - Novas quadras só passam a existir quando alguém cria explicitamente um novo placar na interface.
3. **Blindagem de Rotas:**
   - A rota de fallback da SPA (`serve_spa`) retorna expressamente `HTTP 404 Not Found` para requisições com prefixo `/api/*` não tratadas pelo backend.

## Rationale

- O Placar Vôlei opera em peladas com salas efêmeras e dinâmicas; não há razão para manter quadras estáticas pré-criadas.
- O auto-seeding violava a expectativa do operador da instância de subir uma versão limpa para novos jogos.
- Eliminar mais de 1.600 linhas de código legado simplifica a arquitetura, reduz o tempo de boot e elimina potenciais regressões.

## Consequences

- Ao atualizar a versão da aplicação, todas as salas anteriores são descartadas e o banco nasce sem nenhuma quadra ativa.
- Rotas antigas `/api/arenas` deixam de existir e retornam 404.
- O débito técnico `debt-arenas-legadas` é encerrado e marcado como pago.
