# Plano — CV5.DS3.US1 Placar que não congela

- **Nível:** User Story · **Branch:** `feature/cv5-ds3-us1-placar-que-nao-congela` · **Versão:** minor (0.20.0, comportamento visível)

## Scope
1. **Batimento do servidor:** o laço de 5 s do `/ws` (`app/main.py:192`) envia `{"tipo":"PING"}` a cada 20 s. O relógio ignora tipos desconhecidos (`WatchModel.kt:392`), então nada muda para ele.
2. **Vigia no web:** em `App.svelte`, cada mensagem reinicia um timer de 45 s; se estourar, `socket.close()` e o backoff atual reconecta. `wsConectado` fica falso na hora e a tela mostra que está reconectando.
3. **Volta do segundo plano:** em `visibilitychange` (visível) e `online`, se o socket não estiver `OPEN`, reconecta na hora e zera o backoff.
4. `ESTADO_INICIAL` sempre substitui o estado (zera `ultimoSnapshot` antes de aplicar, `sync.js:14`).
5. `lerJson(res)` em `sync.js`: tenta `res.json()`, e em falha devolve `null`; as quatro chamadas em `App.svelte` passam a usar e mostram a mensagem amigável num 502.
6. Cópia: `await navigator.clipboard.writeText` com try/catch em `SalaQuadra.svelte:188` e `ModalCompartilhar.svelte:51`; "copiado" só em sucesso, "Não foi possível copiar, o código é 48291" em falha.

## Acceptance
- Dado um espectador com o celular bloqueado por 5 min, quando desbloqueia, então em até 3 s o placar está atual ou a tela diz "Reconectando…".
- Dada a rede cortada sem fechar o TCP (DevTools offline), então em até 45 s a tela mostra que perdeu a conexão.
- Dado um 502 do túnel ao entrar, então a mensagem é "Não foi possível entrar na sala.", nunca "Unexpected token".
- Dado um navegador que nega a área de transferência, então não aparece "copiado".

## Design
Ping do servidor, não do cliente: o servidor já tem o laço de 5 s e o relógio não precisa mudar. Rejeitado: `ping` do protocolo WebSocket (o navegador não expõe).

## Out of Scope
Extrair a conexão para `lib/conexao.js` (`CV5.DS5.TS1`).

## Validation
`web: npm run check && npm test && npm run build` (via Node do Windows); `uv run pytest -q`; roteiro manual com DevTools offline, celular bloqueado e 502 simulado parando o container.
