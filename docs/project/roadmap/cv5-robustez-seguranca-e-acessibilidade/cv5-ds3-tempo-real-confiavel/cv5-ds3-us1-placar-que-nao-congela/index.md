---
code: CV5.DS3.US1
level: User Story
status: Validated
status_reason: automode aprovado pelo Navigator em 2026-09-27; testes automatizados verdes
human_validation: pending
updated: 2026-09-27
---

# CV5.DS3.US1 — Placar que não congela

## Scope
- Heartbeat ou timeout de inatividade no WebSocket; reconectar em `visibilitychange` e `online` (`App.svelte:67`).
- Zerar `ultimoSnapshot` no `ESTADO_INICIAL` para aceitar `seq` menor após reinício (`sync.js:14`).
- Ler JSON só com `res.ok` ou com fallback amigável (`App.svelte:137,153,206,232`).
- Mostrar "copiado" só quando a cópia der certo (`SalaQuadra.svelte:188`, `ModalCompartilhar.svelte:51`).

## Acceptance
- Dado um espectador com o celular bloqueado por 5 min, quando desbloqueia, então o placar se atualiza sozinho ou mostra que está reconectando.
- Dado um 502 do túnel, então a mensagem é legível, não "Unexpected token <".

## Plano

[plan.md](plan.md) — branch `feature/cv5-ds3-us1-placar-que-nao-congela`.

## Revisão (Passo 5)

- **Feito:** PING do `/ws` a cada 20 s; vigia de 45 s no `App.svelte` (`vigiar`/`derrubar`/`agendarReconexao`); `retomarConexao` em `visibilitychange` e `online`; `ESTADO_INICIAL` zera `ultimoSnapshot`; `lerJson`; `lib/areaDeTransferencia.js` com estado `'' | 'ok' | 'falhou'`.
- **Bug antigo corrigido:** `conectarWebSocket` chamava `desconectar()`, que zerava `wsTentativasReconexao`. Por isso o backoff nunca passava de ~1 s.
- **Testes:** backend 199 passaram (1 novo); web: `svelte-check` sem erros nem avisos, 69 testes `node --test` (3 novos) e build verdes. O e2e (Playwright) não rodou nesta sessão.
- **Versão:** minor (0.20.0), aplicada no fechamento conjunto do CV5.
- **Débito novo:** nenhum. A extração para `lib/conexao.js` fica na `CV5.DS5.TS1`.
- **Validação humana pendente:** celular bloqueado por 5 min volta atualizado em até 3 s; modo avião por 1 min e depois volta; `docker compose stop` com a sala aberta, seguido de uma ação, dá mensagem legível; copiar o código em `http://IP-da-LAN` (sem HTTPS) não mostra "Copiado!".
