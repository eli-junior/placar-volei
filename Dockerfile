# syntax=docker/dockerfile:1

# --------------------------------------------------------------------------
# Estágio 1 — Compilação do Frontend Svelte 5 (Node existe apenas aqui)
# --------------------------------------------------------------------------
FROM node:22-bookworm-slim AS web-builder

WORKDIR /src

COPY web/package.json web/package-lock.json ./web/
RUN cd web && npm ci

COPY web/ ./web/
RUN mkdir -p app/static \
 && cd web \
 && npm run build \
 && test -f /src/app/static/index.html

# --------------------------------------------------------------------------
# Estágio 2 — Dependências Python com uv
# --------------------------------------------------------------------------
FROM python:3.12-slim AS python-builder

COPY --from=ghcr.io/astral-sh/uv:0.8.17 /uv /uvx /bin/

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/srv/.venv

WORKDIR /srv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# --------------------------------------------------------------------------
# Estágio 3 — Imagem Final de Execução (Runtime)
# --------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/srv/.venv/bin:${PATH}" \
    HOST=0.0.0.0 \
    PORT=8000 \
    DB_PATH=/data/placar.db

# Usuário não-root e diretórios de aplicação e dados
RUN groupadd --system --gid 1001 placar \
 && useradd --system --uid 1001 --gid placar --home-dir /srv --no-create-home placar \
 && mkdir -p /srv /data \
 && chown -R placar:placar /srv /data

WORKDIR /srv

# Dependências Python compiladas
COPY --from=python-builder --chown=placar:placar /srv/.venv /srv/.venv

# Código da aplicação
COPY --chown=placar:placar app/ /srv/app/

# Fixture padrão de arenas e quadras para reinicialização do banco
COPY --chown=placar:placar defaultArenas.json /srv/defaultArenas.json

# Estáticos compilados do frontend (a única coisa trazida do estágio Node)
COPY --from=web-builder --chown=placar:placar /src/app/static/ /srv/app/static/

USER placar

VOLUME ["/data"]

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:' + sys.argv[1] + '/health', timeout=4).status == 200 else 1)", "8000"]

CMD ["sh", "-c", "exec uvicorn app.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000}"]
