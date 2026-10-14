# Atalhos do Placar Vôlei. `make` (ou `make help`) lista os alvos.
# Os comandos são os do docs/process/development-guide.md e do CI.

COMPOSE ?= docker compose
SERVICO ?= placar
PORT    ?= 8000
APK     ?= debug

.DEFAULT_GOAL := help
.PHONY: help install dev web-dev web-build test test-py test-web check lint format \
        e2e e2e-setup verify fixtures apk \
        up down restart recreate build logs ps shell health \
        backup backup-listar restaurar resetar-notas

help: ## Lista os alvos
	@awk 'BEGIN {FS = ":.*## "} \
	  /^## / {printf "\n\033[1m%s\033[0m\n", substr($$0, 4)} \
	  /^[a-zA-Z_-]+:.*## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

## Local

install: ## Instala as dependências do backend (uv) e do frontend (npm ci)
	uv sync
	cd web && npm ci

dev: ## Sobe o backend com reload (porta PORT, padrão 8000)
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port $(PORT)

web-dev: ## Sobe o dev server do Vite (proxy para o backend)
	cd web && npm run dev

web-build: ## Compila o frontend para app/static
	cd web && npm run build

test: test-web test-py ## Testes unitários do frontend e do backend

test-py: ## pytest
	uv run pytest -q

test-web: ## Testes unitários do frontend (node --test)
	cd web && npm test

check: ## svelte-check
	cd web && npm run check

lint: ## ruff check + ruff format --check (como no CI)
	uv run ruff check app tests
	uv run ruff format --check app tests

format: ## Formata o Python com ruff
	uv run ruff format app tests

e2e-setup: ## Instala o Chromium do Playwright (uma vez)
	cd web && npx playwright install chromium

e2e: ## Playwright + axe (build incluído)
	cd web && npm run test:e2e

verify: ## Verificação completa, na ordem do CI
	cd web && npm test && npm run check && npm run build
	uv run pytest -q
	$(MAKE) lint
	$(MAKE) e2e

fixtures: ## Regera as fixtures de paridade Python↔JS
	uv run python -m tests.paridade_fixtures

apk: ## APK do celular: make apk [APK=release] (exige PLACAR_SERVIDOR e ANDROID_HOME)
	scripts/build-apk.sh $(APK)

## Contêiner (docker compose)

up: ## Compila e sobe como no Mini PC
	$(COMPOSE) up -d --build

down: ## Para e remove o contêiner (mantém o volume do gerenciador)
	$(COMPOSE) down

restart: ## Reinicia o contêiner (apaga as quadras: banco efêmero)
	$(COMPOSE) restart $(SERVICO)

recreate: ## Recompila e recria o contêiner do zero
	$(COMPOSE) up -d --build --force-recreate

build: ## Só compila a imagem
	$(COMPOSE) build

logs: ## Acompanha o log
	$(COMPOSE) logs -f --tail=200 $(SERVICO)

ps: ## Estado do contêiner
	$(COMPOSE) ps

shell: ## Abre um shell no contêiner
	$(COMPOSE) exec $(SERVICO) sh

health: ## Consulta o /health do contêiner
	@curl -fsS http://localhost:$(PORT)/health && echo

backup: ## Backup imediato do gerenciador.db
	$(COMPOSE) exec $(SERVICO) python -m app.backup agora

backup-listar: ## Lista os backups
	$(COMPOSE) exec $(SERVICO) python -m app.backup listar

restaurar: ## Restaura um backup: make restaurar ARQUIVO=<arquivo>.db (para e sobe o app)
	@test -n "$(ARQUIVO)" || { echo "Uso: make restaurar ARQUIVO=<arquivo>.db"; exit 1; }
	$(COMPOSE) stop $(SERVICO)
	$(COMPOSE) run --rm $(SERVICO) python -m app.backup restaurar /backups/$(notdir $(ARQUIVO))
	$(COMPOSE) up -d $(SERVICO)

resetar-notas: ## Põe a nota de todos os jogadores em 60 (faz backup antes; pede confirmação)
	@printf "Resetar a nota de TODOS os jogadores para 60 no contêiner? [s/N] " && read r && [ "$$r" = s ]
	$(COMPOSE) exec $(SERVICO) python -m app.backup agora
	$(COMPOSE) exec $(SERVICO) python -m app.nota_viva resetar --confirmar
