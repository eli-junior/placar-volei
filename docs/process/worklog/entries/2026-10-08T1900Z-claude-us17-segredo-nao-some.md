---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-08
related:
  - CV8.DS7.US17
  - recusa-do-segredo-e-bloqueio-sem-apagar
---

# US17: o segredo do dono só some quando o servidor o recusa (0.46.4)

- **Causa:** o QA culpou o 429; no código, quem apagava o segredo era qualquer 404 (o cliente não lia o corpo) e o 4401 do WebSocket, que também fechava no bloqueio. Sondagem sem cabeçalho ainda gastava as tentativas do IP.
- **Entrega:** `recusado` no cliente (404 sem `erros`), 4429 para o bloqueio no WebSocket, `Retry-After` na mensagem do 429 e sem-segredo fora da conta do bloqueio.
- **Lição:** o e2e roda contra o build estático; chamar `playwright` direto testa o front antigo, use `npm run test:e2e`.
- **Validação:** feita pelo Navigator em 2026-10-08.
