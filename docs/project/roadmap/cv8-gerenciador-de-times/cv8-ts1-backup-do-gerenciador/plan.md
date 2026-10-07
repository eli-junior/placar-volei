# Plano — CV8.TS1 Backup do `gerenciador.db`

Nível: Technical Story (quita a dívida `sem-backup-do-volume-de-jogadores`). Branch: `feature/cv8-ts1-backup-do-gerenciador`. Versão-alvo: **0.33.1** (patch: sem mudança visível na interface; backend, web e APK em 0.33.1 por consistência; Wear inalterado).

## Escopo

**Módulo `app/backup.py`**
- `fazer_backup()`: abre o `gerenciador.db` e usa a API de backup do SQLite (`Connection.backup`), que gera uma cópia consistente com o app em uso e o WAL ativo. Grava em `gerenciador-AAAAMMDDTHHMMSSZ.db.parcial` dentro da pasta de backup, roda `PRAGMA integrity_check` **na cópia**, confere que as tabelas esperadas existem e só então renomeia para `.db` (renomear é atômico). Cópia que falha é apagada, logada como erro, e **nunca substitui nem faz podar** as anteriores.
- **Retenção:** depois de uma cópia boa, mantém as `N` mais recentes e apaga o resto. Padrão `N = 28`.
- **Disparo automático:** uma tarefa no `lifespan` (como a rotina de limpeza das quadras) faz um backup logo depois do `init` e repete a cada `H` horas. Padrão `H = 6` (28 cópias ≈ 7 dias). Com a pasta não configurada, não faz nada e avisa uma vez no log. Falha do backup nunca derruba o app.
- **Sob demanda (CLI):** `python -m app.backup agora` (cópia imediata) e `python -m app.backup listar`.
- **Restauração (CLI):** `python -m app.backup restaurar <arquivo> [--destino <caminho>]`. Verifica a integridade da cópia antes, grava num arquivo temporário pela API de backup (sem trazer `-wal`/`-shm` velhos), guarda o arquivo atual como `<destino>.antes-AAAAMMDDTHHMMSSZ` e só então troca. **O app precisa estar parado** (o procedimento diz isso e o comando avisa). `--destino` permite ensaiar a restauração fora do banco real.

**Configuração** (`.env.example` e compose): `GERENCIADOR_BACKUP_DIR` (vazio = desligado), `GERENCIADOR_BACKUP_INTERVALO_HORAS` (6), `GERENCIADOR_BACKUP_MANTER` (28).

**Compose:** pasta do host montada como bind mount `./backups:/backups` (fora do volume `gerenciador-dados`), com `GERENCIADOR_BACKUP_DIR=/backups`. Por ser pasta do host, o Navigator pode copiá-la para onde quiser; `backups/` entra no `.gitignore`. O contêiner roda como uid 1001, então a pasta precisa ser gravável por ele (`mkdir backups && sudo chown 1001:1001 backups` no Mini PC, uma vez); sem isso o backup falha com mensagem clara no log, sem derrubar nada.

**Documentação:** procedimento de backup e de restauração no `development-guide.md`, incluindo o ensaio de restauração.

## Aceite (BDD)

- Given jogadores, notas, fotos e uma sessão no `gerenciador.db`, When o backup roda com o app gravando, Then surge uma cópia íntegra na pasta de backup, fora do volume.
- Given 30 cópias com retenção 28, When uma nova cópia é feita, Then sobram as 28 mais recentes.
- Given que a cópia falha (disco cheio, pasta sem permissão, arquivo corrompido), When o backup roda, Then o erro vai para o log, as cópias anteriores ficam intactas e o app segue no ar.
- Given uma cópia, When restauro num banco novo, Then voltam todos os jogadores, notas, fotos, sessões e presenças.
- Given uma cópia corrompida, When tento restaurar, Then é recusado e o banco atual não é tocado.

## Testes

- pytest: cópia consistente com escrita concorrente, integridade, retenção (e que falha não poda), pasta desligada/sem permissão, nome único por segundo, restauração completa (jogador, foto, sessão), recusa de cópia corrompida, `.antes` preservado, `--destino`, rotina do `lifespan` (intervalo curto injetado).
- Verificação manual guiada (Mini PC): ver a rota de validação.

## Alternativas rejeitadas

- **Contêiner separado ou `cron` do host:** uma peça móvel a mais para um backup que o próprio app já sabe fazer com a API do SQLite.
- **Copiar o arquivo `.db` com `cp`:** com WAL ativo a cópia pode sair inconsistente.
- **Segundo volume nomeado como destino:** protege de apagar o primeiro, mas continua preso ao Docker; a pasta do host é copiável e visível.
- **Envio para a nuvem agora:** fora do escopo; a pasta do host facilita um `rclone`/`rsync` depois.
- **Backup só quando o banco muda:** exigiria detectar mudança com WAL; a cópia é pequena, então copiar sempre é mais simples e seguro.

## Fora do escopo

Backup do banco efêmero das quadras; envio para a nuvem; interface para listar ou restaurar pela tela; criptografia das cópias (guardam rostos: a pasta do host deve ter o mesmo cuidado do volume).

## Pontos para o Navigator confirmar

1. **Bind mount `./backups` no host** (e o `chown 1001:1001` único no Mini PC) em vez de um segundo volume Docker.
2. **Padrões 6 h / 28 cópias** (≈ 7 dias). Ajustáveis por variável de ambiente.

## Riscos

- Sem o `chown`, o backup não grava: o log avisa, mas só vale se alguém olhar. A rota de validação inclui conferir a pasta depois do primeiro ciclo.
- Restaurar com o app rodando pode corromper a troca; por isso o procedimento manda parar o app e o comando avisa.
