---
code: CV7.US2
level: User Story
status: Validated
status_reason: validada pelo Navigator no Galaxy Z Fold e no Galaxy Watch SM-L330 em 2026-10-02
updated: 2026-10-02
---

# CV7.US2 — Relógio controla a quadra local

## Intent

Com a quadra local aberta no celular, o relógio marca o placar nela, com a mesma tela, a mesma fila offline e o mesmo desfazer de sempre, sem internet e sem escolher nada.

## Scope

- **O celular decide o modo** e o relógio o segue (escolha do Navigator, 2026-10-02): enquanto a sala local está aberta no celular, o relógio mostra a quadra local; fora disso é o servidor, como antes. Com o relógio vinculado a uma quadra do servidor e a sala local aberta, a local ganha.
- **Sinal do celular:** o estado publicado leva `sala_aberta` e um `t` que muda a cada publicação; a ponte o republica a cada 20 s (sinal de vida) e ao fechar a sala. O relógio que abre pergunta o estado por `ping`, sem esperar o sinal. Sem notícia por 90 s (medidos no relógio do relógio) a sala conta como fechada.
- **`PlacarFonte`:** a `ScoreScreen` depende da interface, implementada pelo `WatchModel` (servidor) e pela `CelularSessao` (quadra local). Placar, fila durável, desfazer previsto, aro de conexão, retorno ao pontuar e aviso de descarte são os mesmos; a tela ganha a tag **LOCAL**.
- **`CelularSessao`:** `ScoreSync` com fila própria (`fila-celular.json`, separada da do servidor) sobre o `CelularLink` da CV7.TS3; envio em ordem, recibo por id, nova partida pelo celular (direto, como no servidor).
- **Tela acesa (plano B):** com a tela do celular apagada o sinal para (o JS congela). Com lances na fila o relógio mantém a quadra local com o anel vermelho até a fila esvaziar ou o celular fechar a sala; sem lances ele volta ao servidor.

## Acceptance / Done Condition

Given a quadra local aberta no celular, sem comunicação com o servidor, e o relógio pareado
When abro o app do relógio
Then ele mostra o placar da quadra local, marco e desfaço pontos com o mesmo placar e a mesma fila offline, e o celular reflete cada lance
And o que marco no celular aparece no relógio
And com o celular fora de alcance ou com a tela apagada o relógio segue marcando, e os lances entram em ordem, uma vez só, quando o celular voltar
And com a sala local fechada no celular o relógio volta a ser o de sempre

## Validation Route

`CelularSessaoTest.kt` (modo, sinal de vida, fila, descarte, nova partida), `ponteRelogio.test.js` (sinal de vida, ping, sala fechada). No aparelho (Z Fold + Galaxy Watch SM-L330, debug): relógio entra sozinho na quadra local, toques nos dois sentidos, desfazer, saída e volta da sala, e queda do app do celular devolvendo o relógio ao servidor.

## Out of Scope

Várias quadras locais; espectadores na quadra local; trocar de modo no meio de uma partida; o plano C (regras em Java); release assinado.

## Known Limits

- `debt-quadra-local-so-atende-relogio-com-tela-acesa`: com a tela do celular apagada, sem lances na fila o relógio volta ao servidor ~3,5 min depois.
- `debt-relogio-local-sem-servico-em-primeiro-plano`: o modo local do relógio não roda sob o serviço em primeiro plano.
- `debt-apk-caminhos-nativos-sem-teste-automatico`: a escolha de modo na `MainActivity` só se valida no aparelho.
