---
code: CV7
level: Value
status: Active
status_reason: planejada em 2026-10-01; TS1 em andamento
updated: 2026-10-01
---

# CV7 — Placar como APK Android, online ou offline

## Intent

O placar roda como app Android. Com internet, usa a quadra do servidor como hoje. Sem internet, o celular guarda a partida e o relógio continua marcando por Bluetooth. Decisão: `apk-capacitor-e-quadra-local`.

## Entregas

- **CV7.TS1 — Casca Capacitor:** APK `br.com.placarvolei` que abre a quadra online do servidor configurado. Sem comportamento novo.
- **CV7.TS2 — Regras e projeção em JS:** porte com testes de paridade contra fixtures geradas pelo Python.
- **CV7.US1 — Quadra local no celular:** criar e jogar sem internet (marcar, desfazer, faixa, linha do tempo, nova partida), log persistido no aparelho.
- **CV7.TS3 — Ponte Data Layer:** plugin nativo no celular; transporte "Celular" no relógio; troca do `applicationId` do relógio.
- **CV7.US2 — Relógio controla a quadra local offline:** mesma fila, `base_seq` e descarte com aviso.
- **CV7.US3 — Enviar histórico local ao servidor:** fora desta rodada (Navigator, 2026-10-01).

## Acceptance / Done Condition

Em modo avião (Bluetooth ligado), celular e relógio marcam e desfazem pontos na mesma quadra local e mostram o mesmo placar; com internet, o APK abre e opera uma quadra online igual ao navegador.

## Fora do escopo

Trocar de modo no meio da partida; espectadores remotos na quadra local; iOS.
