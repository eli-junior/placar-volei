# Plano de Implementação — CV1.DS1.TS3

## Contexto

O banco de dados SQLite de desenvolvimento ou produção pode ser descartado ou reiniciado a qualquer momento. Para não perder os nomes das arenas e quadras que foram configuradas, uma fixture JSON versionada (`defaultArenas.json`) mantém esse estado mestre.

## Passos Realizados

1. **Criação de `defaultArenas.json`:**
   - Criado na raiz do projeto com as arenas e quadras existentes ("T9 Beach Club" e "Tio Cleo").
2. **Configuração (`app/config.py`):**
   - Adicionada a propriedade `default_arenas_file: str = "defaultArenas.json"`.
3. **Módulo `app/fixtures.py`:**
   - Implementadas funções para carregamento seguro, salvamento atômico em arquivo temporário e substituição (`os.replace`).
   - Implementada sincronização idempotente `sincronizar_fixtures_para_db_sync`.
   - Implementadas funções `adicionar_arena_fixture_sync` e `adicionar_quadra_fixture_sync`.
4. **Acoplamento no ciclo de vida e operações (`app/db.py`, `app/quadras.py`):**
   - `init_db_sync` invoca `sincronizar_fixtures_para_db_sync`.
   - `criar_arena_sync` chama `adicionar_arena_fixture_sync`.
   - `criar_quadra_sync` chama `adicionar_quadra_fixture_sync`.
   - Refatoração de `get_db` em `app/db.py` com `@contextmanager` para fechamento garantido de conexão (liberando locks no Windows e prevenindo vazamentos).
5. **Ambiente de Testes (`tests/conftest.py`, `tests/test_fixtures.py`):**
   - Criado `tests/conftest.py` para isolar `settings.default_arenas_file` durante os testes automatizados em arquivo temporário.
   - Criados 7 testes cobrindo carga, salvamento, normalização, idempotência, sincronização na API e ciclo de vida com deleção do banco de dados.
6. **Deploy Docker (`Dockerfile`):**
   - Adicionado `COPY defaultArenas.json /srv/defaultArenas.json` no estágio runtime.
