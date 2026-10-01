#!/bin/bash
# build-apk.sh — Gera o APK do celular (CV7.TS1).
#
# Uso:  PLACAR_SERVIDOR=placar.seudominio.com scripts/build-apk.sh [debug|release]
#
# Precisa de Node, JDK 21 e Android SDK (ANDROID_HOME). O servidor entra no
# `allowNavigation` do WebView e vira o padrão da tela inicial do app.
# Release usa a keystore do Navigator via variáveis do Gradle; ela nunca
# entra no repositório.

set -euo pipefail

TIPO="${1:-debug}"
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"

if [ -z "${PLACAR_SERVIDOR:-}" ]; then
  echo "Defina PLACAR_SERVIDOR (ex.: placar.seudominio.com)." >&2
  exit 1
fi

cd "$RAIZ/web"
npm ci
VITE_PLACAR_SERVIDOR="$PLACAR_SERVIDOR" npm run build
npx cap sync android

cd "$RAIZ/android"
if [ "$TIPO" = "release" ]; then
  ./gradlew assembleRelease
  ls -1 app/build/outputs/apk/release/*.apk
else
  ./gradlew assembleDebug
  ls -1 app/build/outputs/apk/debug/*.apk
fi
