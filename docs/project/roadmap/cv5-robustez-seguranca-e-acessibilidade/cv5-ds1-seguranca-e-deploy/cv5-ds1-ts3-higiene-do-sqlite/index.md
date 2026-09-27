---
code: CV5.DS1.TS3
level: Technical Story
status: Validated
status_reason: automode aprovado pelo Navigator em 2026-09-27; testes automatizados verdes
human_validation: pending
updated: 2026-09-27
---

# CV5.DS1.TS3 — Higiene do SQLite e da memória

## Scope
- Validar `^\d{5}$` antes de criar lock de sala e limpar `_quadra_locks` na expiração (`app/eventos.py:41`, `app/main.py:145`).
- Limpeza de salas apaga também `watch_recibos` (`app/quadras.py:115`).
- Listagem sem rodar a limpeza e sem reprojetar o log de cada sala por GET (`app/quadras.py:337`).
- `PRAGMA busy_timeout`, WAL só no init, `synchronous=NORMAL` (`app/db.py:106`).
- **Decisão do Navigator:** migrar o schema em vez de apagar o banco a cada versão (`app/db.py:130`), preservando os recibos de idempotência.

## Acceptance
Conexões em `/ws/<id inválido>` não criam estado; depois da expiração não sobra linha da sala em nenhuma tabela.

## Plano

[plan.md](plan.md) — branch `feature/cv5-ds1-ts3-higiene-do-sqlite`.

## Revisão (Passo 5)

- **Feito:** `SCHEMA_VERSAO` derivado do DDL (sem número para esquecer); `busy_timeout`, `synchronous=NORMAL`, WAL só no init; limpeza apaga `watch_recibos` e descarta locks; `/ws` valida `^\d{5}$`; listagem sem limpeza, filtrando vencidas, com cache do placar por `(partida_id, seq)`.
- **Ajuste ao plano:** em vez de constante manual + teste de hash, o próprio hash é a versão.
- **Considerado e não feito:** expiração avisada pelo hub (ganho pequeno com 20 salas).
- **Atenção:** mudança feita só por `ALTER TABLE` no `init_db`, sem mexer no `SCHEMA_SQL`, não muda o hash; as migrações existentes já são idempotentes.
- **Débito novo:** nenhum. **Docs:** decisão de 2026-09-15 atualizada.
- **Validação humana pendente:** o primeiro deploy desta versão ainda recria o banco (não havia `schema` gravado); nos seguintes, salas sobrevivem ao `up -d --build`. `GET /api/quadras` com a Home aberta não deve atrasar pontos.
