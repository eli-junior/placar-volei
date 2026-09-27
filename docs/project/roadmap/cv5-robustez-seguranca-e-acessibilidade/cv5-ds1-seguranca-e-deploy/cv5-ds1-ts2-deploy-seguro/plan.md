# Plano — CV5.DS1.TS2 Deploy seguro

- **Nível:** Technical Story · **Branch:** `feature/cv5-ds1-ts2-deploy-seguro` · **Versão:** patch

## Scope
1. `docker-compose.yml`: volume nomeado `placar-data:/data` (o `Dockerfile:51` já cria `/data` com dono `placar`, e o volume nomeado herda essa posse; bind `./data` exigiria `chown 1001`).
2. `OWNER_SECRET=${OWNER_SECRET:?defina OWNER_SECRET no .env}` no compose.
3. `app/config.py`: sem default útil para `owner_secret`; no startup, se vazio ou igual a `troque-este-segredo-em-producao` **e** `ENV=production`, o app loga o motivo e sai. Em dev/testes segue permitido.
4. `/health` sem o campo `db` (`app/main.py:137`).
5. `COOKIE_SECURE` (default `false`; compose `true`) aplicado aos dois `set_cookie` (`app/api.py:251,327`).
6. `docs/process/development-guide.md`: procedimento de atualização (`up -d --build` preserva dados; como fazer backup do volume).
7. Fecha `debt-banco-de-producao-sem-volume-persistente` como `Paid`.

## Acceptance
- Dada uma sala criada, quando rodo `docker compose up -d --build` sem mudar a versão, então a sala continua.
- Dado um `.env` sem `OWNER_SECRET`, então `docker compose up` falha com a mensagem.
- Então `/health` não mostra caminho e o cookie vem com `Secure` em produção.

## Design
Volume nomeado em vez de bind: dispensa ajuste de permissão no host. Recusa só em produção para não quebrar testes e dev local.

## Out of Scope
Preservar dados **entre versões**: o banco ainda é apagado a cada versão nova (tratado na `CV5.DS1.TS3`).

## Risks / Navigator
- O primeiro deploy com volume começa vazio (o banco atual está dentro do container). Aceitável: salas duram 1 h, mas o relógio precisará parear de novo uma vez.
- Acesso por `http://IP-da-LAN` com `COOKIE_SECURE=true` perde o cookie. Confirmar que o uso é só pelo túnel HTTPS.

## Validation
`uv run pytest -q`; no Mini PC: criar sala, `up -d --build`, conferir a sala; `curl -I` para ver `Secure`.
