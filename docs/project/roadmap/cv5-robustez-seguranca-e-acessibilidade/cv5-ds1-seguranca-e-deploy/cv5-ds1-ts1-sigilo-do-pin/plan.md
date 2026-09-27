# Plano — CV5.DS1.TS1 Sigilo do PIN e limite por cliente real

- **Nível:** Technical Story · **Branch:** `feature/cv5-ds1-ts1-sigilo-do-pin` · **Versão:** patch (0.19.1)

## Achado que muda o escopo
A Home ao vivo (`HomePlacar.svelte:56`) usa `GET /api/quadras` para listar as salas e entrar com um toque. O lobby é funcionalidade entregue (CV2/CV4), não vazamento acidental: esconder o `id` quebra a Home.

**Recomendação:** manter o lobby, registrar a decisão "o PIN identifica a sala, não a protege" e endurecer o resto. Salas privadas (fora do lobby) viram follow-up se o Navigator quiser.

## Scope
1. `app/rede.py` (novo): `ip_do_cliente(request)` usa `CF-Connecting-IP` só quando `TRUST_CLOUDFLARE=true`; senão `request.client.host`. Nunca `X-Forwarded-For`.
2. `autenticar_owner` (`app/api.py:631`) e `start_pairing` (`app/watch.py:238`) passam a usar `ip_do_cliente`.
3. `approval_limit` com chave dupla: participante **e** `ip:quadra` (`app/watch.py:399-471`).
4. `POST /quadras/{id}/entrar`: `RateLimiter` por IP para 404 (20 falhas/10 min → 429 com `Retry-After`).
5. PIN com `secrets.randbelow` (`app/quadras.py:87`).
6. `x-session-id`/cookie aceitos só como UUID; outro valor gera sessão nova (`app/api.py:215`).
7. `docker-compose.yml`: `TRUST_CLOUDFLARE=${TRUST_CLOUDFLARE:-true}`; `.env.example` documentado.
8. Decisão em `docs/project/decisions/records/` sobre o lobby público.

## Acceptance
- Dado o owner errando o segredo 5 vezes, quando troca `X-Forwarded-For` a cada tentativa, então recebe 429 do mesmo jeito.
- Dado `TRUST_CLOUDFLARE=true`, quando dois clientes chegam com `CF-Connecting-IP` diferentes, então têm limites separados.
- Dado um cliente errando 20 PINs, então o 21º recebe 429; um PIN certo de outro IP entra.
- Dado `x-session-id: abc`, então o servidor ignora e cria uma sessão UUID.

## Design
- `CF-Connecting-IP` é sobrescrito pelo Cloudflare, então é confiável atrás do túnel; exposto direto, a flag desligada evita forja. Rejeitado: `--proxy-headers` do uvicorn (confia em XFF, que o Cloudflare repassa do cliente).
- Limite de `/entrar` só conta 404: jogadores legítimos erram pouco, e o lobby já mostra as salas.

## Out of Scope
Salas privadas fora do lobby; limite persistido entre reinícios (continua em memória).

## Risks / Navigator
- **Decisão:** confirmar lobby público (recomendado) ou pedir salas privadas.
- Se o Mini PC também for acessado pela LAN sem túnel, `CF-Connecting-IP` falta e cai no IP da conexão: correto.

## Validation
`uv run pytest -q`, testes novos em `tests/test_rate_limit_ip.py`; `curl` com headers forjados contra o container.

## Ajustes na implementação
- Sessão: em vez de exigir UUID (quebraria os clientes e testes que usam ids próprios), o valor precisa casar `[A-Za-z0-9_-]{1,64}`; fora disso vira sessão UUID nova. Resolve o risco real (valor arbitrário e sem limite).
- A aprovação do relógio só aceita o participante habilitado (na prática, o "Eli" admin da sala), então a chave `ip:quadra` é defesa extra, não o bloqueio principal.
