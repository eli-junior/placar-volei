# Plano — CV5.DS1.TS3 Higiene do SQLite e da memória

- **Nível:** Technical Story · **Branch:** `feature/cv5-ds1-ts3-higiene-do-sqlite` · **Versão:** patch

## Scope
1. `/ws/{quadra_id}` recusa (close 4404) id fora de `^\d{5}$` antes de `get_quadra_lock` (`app/main.py:145`).
2. `limpar_quadras_expiradas` descarta os locks das salas removidas (`app/eventos.py:41`) e apaga `watch_recibos` e `watch_grants` da sala (`app/quadras.py:115`).
3. `listar_quadras` não chama mais a limpeza (a rotina periódica já faz) e lê o placar da última partida com uma consulta só, sem reprojetar evento por evento a cada GET; se o projetor for necessário, cache por `(partida_id, seq)`.
4. `get_db`: `PRAGMA busy_timeout=5000` por conexão; `journal_mode=WAL` só no `init_db`; `synchronous=NORMAL`.
5. **Versão do schema separada da versão do app** (`app/db.py:130`): `app_meta` guarda `schema_versao` (constante em `db.py`); o banco só é apagado quando o schema muda. Releases sem mudança de tabela preservam salas e recibos.

## Acceptance
- Dado `/ws/abc`, então a conexão fecha e `_quadra_locks` não cresce.
- Dada uma sala expirada com relógio, então nenhuma tabela guarda linha dela.
- Dado um deploy de versão nova sem mudar o schema, então salas e recibos continuam.
- Dada uma mudança de schema, então o banco é recriado como hoje, com log.

## Design
Rejeitado: sistema de migrações (Alembic) — pesado para salas de 1 h; o `schema_versao` resolve o caso comum. Atualizar o registro `2026-09-15T1730Z-remocao-de-arenas-e-banco-limpo-no-versionamento`.

## Out of Scope
Pool de conexões; migração com preservação quando o schema muda.

## Risks / Navigator
- **Decisão:** aprovar "apagar só quando o schema muda" (recomendado).
- Esquecer de subir `schema_versao` numa mudança de tabela quebra o startup; mitigação: teste que compara o hash do DDL com a constante.

## Validation
`uv run pytest -q` com testes de expiração, lock e versão; medir `GET /api/quadras` com 20 salas antes/depois.
