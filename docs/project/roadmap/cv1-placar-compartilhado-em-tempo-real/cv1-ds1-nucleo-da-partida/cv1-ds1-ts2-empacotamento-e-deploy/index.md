---
code: CV1.DS1.TS2
level: Technical Story
status: Done
status_reason: Dockerfile multi-estágio e docker-compose.yml criados e configurados com volume para SQLite
updated: 2026-09-14
related:
  - CV1.DS1.TS1
  - 2026-09-13T1425Z-stack-do-frontend
---

# CV1.DS1.TS2 — Empacotamento e deploy no Mini PC

## Intent

A aplicação sobe no Mini PC com um comando e fica acessível de fora por Cloudflare Tunnel, sem passo manual no meio.

## Scope

`Dockerfile` multi-estágio (estágio Node compila o frontend Svelte, estágio Python recebe apenas os estáticos), `docker-compose.yml` com volume persistente para o arquivo SQLite, `.env.example` completo, healthcheck e notas de operação — subir, atualizar, fazer backup do banco.

## Acceptance / Done Condition

Given o repositório clonado no Mini PC com o `.env` preenchido
When o operador executa `docker compose up -d --build`
Then a aplicação responde na porta configurada
And a imagem final não contém Node nem `node_modules`
And o arquivo SQLite persiste em volume, sobrevivendo a `docker compose down` seguido de `up`
And a URL do Cloudflare Tunnel serve a aplicação de fora da rede local.

## Validation Route

Build limpo no Mini PC. `docker image inspect` e `docker run --rm <imagem> which node` confirmando ausência de Node. Ciclo `down`/`up` conferindo que o placar de uma partida em andamento sobrevive. Acesso pela URL do túnel a partir de rede móvel, fora do Wi-Fi de casa.

## Out of Scope

CI, publicação de imagem em registry, backup automatizado.

## Notes

Pode ser puxada depois da TS1 e antes da primeira validação multi-dispositivo em quadra real — validar `US2` de celular exige a aplicação acessível fora do localhost.
