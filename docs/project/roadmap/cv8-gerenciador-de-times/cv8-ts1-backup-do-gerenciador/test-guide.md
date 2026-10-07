# Rota de validação — CV8.TS1 Backup do `gerenciador.db`

## 1. Local (rápido)

```bash
OWNER_SECRET=meu-segredo GERENCIADOR_DB_PATH=/tmp/g.db GERENCIADOR_BACKUP_DIR=/tmp/backups-teste \
  GERENCIADOR_BACKUP_INTERVALO_HORAS=0.001 uv run uvicorn app.main:app --port 8000
```

1. Cadastre um jogador com foto em `/jogadores` (segredo `meu-segredo`).
2. Em outro terminal: `ls -l /tmp/backups-teste` → **Passa:** surgem arquivos `gerenciador-<data>.db` a cada ~4 s, e **só** arquivos `.db` (sem `.parcial`, `-wal` ou `-shm`). **Falha:** sobras `.parcial`/`-wal`/`-shm`.
3. `sqlite3 /tmp/backups-teste/<mais recente> "select nome, nota from jogadores"` → **Passa:** o jogador aparece.
4. Pare o servidor e rode `uv run python -m app.backup restaurar /tmp/backups-teste/<mais recente> --destino /tmp/ensaio.db` → **Passa:** imprime o caminho; `sqlite3 /tmp/ensaio.db "select count(*) from jogador_fotos"` devolve 1.
5. Corrompa uma cópia (`echo lixo > /tmp/ruim.db`) e tente restaurar → **Passa:** "Erro: ... não é um banco SQLite legível", código de saída 1, nada criado.
6. Suba o app com `GERENCIADOR_BACKUP_DIR` vazio → **Passa:** aviso "Backup do gerenciador desligado" no log e o app funciona normalmente.

## 2. Mini PC (depois do deploy)

1. `mkdir backups && sudo chown 1001:1001 backups` (uma vez) e `docker compose up -d --build`.
2. `ls -l backups` → **Passa:** já existe uma cópia (feita na subida). Sem ela, `docker compose logs placar | grep -i backup` mostra o motivo (provável `Permission denied`).
3. Cadastre um jogador de teste, rode `docker compose exec placar python -m app.backup agora` e `listar` → **Passa:** a cópia nova aparece.
4. **Ensaio de restauração fora do banco real:** `docker compose run --rm placar python -m app.backup restaurar /backups/<arquivo>.db --destino /tmp/ensaio.db` → **Passa:** imprime o caminho sem erro.
5. (Opcional, só com sua autorização) restauração de verdade: `docker compose stop placar`, restaurar sem `--destino`, `docker compose up -d placar` → **Passa:** os jogadores continuam e o banco antigo ficou como `.antes-<data>` no volume.

## Evidência automatizada

`uv run pytest` (316; 13 novos da TS1: consistência com escrita concorrente, retenção, falha que não poda, restauração completa com foto e sessão, recusa de cópia corrompida, rotina e linha de comando). Fumaça real com o servidor: cópias a cada 2 s, só `.db`, restauração devolve o jogador.
