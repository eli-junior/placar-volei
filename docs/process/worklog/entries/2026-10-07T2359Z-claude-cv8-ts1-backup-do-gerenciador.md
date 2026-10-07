---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-07
related:
  - CV8.TS1
---

# CV8.TS1 — backup e restauração do gerenciador.db entregues (0.33.1)

- **Entrega:** `app/backup.py` — cópia pela API de backup do SQLite, verificada (`integrity_check` + tabelas esperadas) antes do nome final; retenção de 28; rotina no `lifespan` (na subida e a cada 6 h); CLI `agora`/`listar`/`restaurar` (com `--destino` para ensaio e `.antes-*` do banco substituído); pasta `./backups` do host no compose, fora do volume. Quita a dívida `sem-backup-do-volume-de-jogadores`.
- **Achado de fumaça real:** a cópia herdava o modo WAL e deixava `-wal`/`-shm` soltos; passou a ser gravada em modo `DELETE` (arquivo único).
- **Achado de revisão:** o `agora` apagava a sobra `.parcial` de uma cópia em andamento da rotina; agora só apaga sobras com mais de 1 h (teste dedicado).
- **Evidência:** pytest 316 (13 novos), fumaça com servidor real (cópias a cada 2 s, só `.db`, restauração devolve o jogador); validada pelo Navigator.
- **Dívidas abertas:** cópias na mesma máquina, falha de backup só no log, `.antes-*` acumulando.
