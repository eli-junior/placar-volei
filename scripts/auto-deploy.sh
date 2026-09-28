#!/bin/bash
# auto-deploy.sh — Verifica se a branch atual do placar-volei recebeu push
# novo em origin e, se sim, atualiza e recria o container.
#
# Rodado a cada minuto via placar-auto-deploy.timer (systemd). Segue o
# procedimento documentado: git fetch --prune + git pull --ff-only +
# docker compose up -d --build --force-recreate (o --force-recreate é
# necessário para garantir container novo, e portanto banco SQLite limpo).
#
# Funciona em qualquer branch em que o repo esteja no momento (master ou
# uma branch de feature em validação) — não força volta para master.

set -uo pipefail

REPO_DIR="/home/eli/apps/placar-volei"
LOG_FILE="/home/eli/logs/placar-auto-deploy.log"
LOCK_FILE="/tmp/placar-auto-deploy.lock"
ENV_FILE="/home/eli/ecossistema_claude/.env"
CHAT_ID_FILE="/home/eli/ecossistema_claude/owner_chat_id.txt"

mkdir -p "$HOME/logs"

# Evita duas execuções sobrepostas (um build pode passar de 1 minuto)
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  exit 0
fi

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >>"$LOG_FILE"; }

notify() {
  local msg="$1" token chat_id
  [ -f "$ENV_FILE" ] || return 0
  token=$(grep -m1 '^TELEGRAM_BOT_TOKEN=' "$ENV_FILE" | cut -d= -f2-)
  chat_id=$(cat "$CHAT_ID_FILE" 2>/dev/null)
  [ -z "$token" ] && return 0
  [ -z "$chat_id" ] && return 0
  curl -s -X POST "https://api.telegram.org/bot${token}/sendMessage" \
    -d chat_id="${chat_id}" -d parse_mode="Markdown" --data-urlencode text="$msg" \
    >/dev/null 2>&1
}

cd "$REPO_DIR" || { log "ERRO: diretório $REPO_DIR não encontrado"; exit 1; }

BRANCH=$(git branch --show-current)
if [ -z "$BRANCH" ]; then
  log "ERRO: HEAD destacado (detached) — sem branch para acompanhar, abortando"
  exit 1
fi

if ! git fetch --prune origin "$BRANCH" >>"$LOG_FILE" 2>&1; then
  log "ERRO: git fetch falhou (branch $BRANCH)"
  exit 1
fi

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse "origin/$BRANCH" 2>/dev/null || true)

if [ -z "$REMOTE" ]; then
  log "AVISO: origin/$BRANCH não existe — nada a comparar"
  exit 0
fi

if [ "$LOCAL" = "$REMOTE" ]; then
  exit 0
fi

log "Mudança detectada em '$BRANCH': $LOCAL -> $REMOTE"

if ! git pull --ff-only origin "$BRANCH" >>"$LOG_FILE" 2>&1; then
  log "ERRO: git pull --ff-only falhou (possível divergência/force-push) — deploy abortado"
  notify "⚠️ *Placar Vôlei*: novo commit em \`$BRANCH\` mas o \`pull --ff-only\` falhou. Verifique o Mini PC."
  exit 1
fi

NEW_HASH=$(git rev-parse --short HEAD)

if docker compose up -d --build --force-recreate >>"$LOG_FILE" 2>&1; then
  log "Deploy OK — branch '$BRANCH' em $NEW_HASH"
  notify "🚀 *Placar Vôlei* atualizado — \`$BRANCH\` @ \`$NEW_HASH\`"
else
  log "ERRO: docker compose up falhou após o pull (branch '$BRANCH' @ $NEW_HASH)"
  notify "❌ *Placar Vôlei*: pull ok mas \`docker compose up\` falhou em \`$BRANCH\`. Verifique o Mini PC."
  exit 1
fi
