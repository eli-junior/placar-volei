---
code: CV7.US1
level: User Story
status: Validated
status_reason: validada pelo Navigator no Galaxy Z Fold em 2026-10-02, com o servidor de produção fora do ar
updated: 2026-10-02
---

# CV7.US1 — Quadra local no celular

## Intent

Quando não há comunicação com o servidor, o APK ainda marca o placar: uma quadra local, guardada no aparelho, jogada do começo ao fim. É o plano B da quadra online, não um segundo modo concorrente.

## Scope

- **A conexão decide o modo.** A tela inicial testa o `/health` (rede nativa, `200` com `status: ok`). Servidor no ar: só a quadra online habilita. Sem ele: só a local. Testando: nenhuma. Um `502` do túnel com o backend fora conta como sem comunicação.
- **Uma quadra local por APK**, criada na primeira vez que for preciso e reaproveitada. Uma partida em andamento continua acessível mesmo que o servidor volte; encerrada, fica bloqueada enquanto ele responder. Apagar a quadra local fica no ⚙ ("Apagar quadra local", com confirmação).
- **Log guardado no aparelho** (`@capacitor/preferences`; `localStorage` fora do APK), com as regras da CV7.TS2. Cada comando grava antes de mudar a tela; se a gravação falha, o ponto não vale. Dados ilegíveis ficam guardados à parte e a pessoa decide ("Começar do zero"); erro de leitura do aparelho não é tratado como dado ruim.
- **Mesma sala de sempre** (`SalaQuadra` com `modoLocal`): marcar, desfazer, duplas e regras, tema do placar, inverter lados, linha do tempo, celebração e nova partida. Sem relógio (CV7.US2), compartilhar nem lista de presentes.
- **Áreas seguras do sistema** unificadas (`--sa-*`): no APK a tela vai por baixo da barra de navegação, e a folha de ações ficava cortada.

## Acceptance / Done Condition

Given o APK instalado e sem comunicação com o servidor
When abro o app e toco em Criar quadra local
Then a sala abre sem pedir rede e marco, desfaço, ajusto regras e vejo a linha do tempo
And fechando e reabrindo o app, Continuar quadra local mostra o mesmo placar
And com o servidor respondendo, a quadra online é a única criação habilitada

## Validation Route

`web/tests/quadraLocal.test.js` e `web/tests/casca.test.js` (gate dos modos, teste de conexão, armazenamento, recuperação); `web/e2e/local.spec.js` (modos, partida até o fim, reabrir, voltar, apagar, ilegível, axe nos dois temas, nenhuma chamada a `/api` nem WebSocket). No aparelho, o roteiro do Navigator.

## Out of Scope

Relógio e ponte Bluetooth (CV7.TS3, US2); espectadores e compartilhar; várias quadras locais e histórico na tela; envio ao servidor (CV7.US3); trocar de modo no meio da partida.

## Known Limits

- O Voltar do Android dentro da sala fecha o app; a quadra continua salva.
- A tela apagar sozinha com a sala aberta não foi observada no aparelho; decide o plano B da TS3.
- Os caminhos nativos (`CapacitorHttp`, `Preferences`) só têm validação no aparelho: `debt-apk-caminhos-nativos-sem-teste-automatico`.
