---
code: CV7.TS3
level: Technical Story
status: Validated
status_reason: validada pelo Navigator no Galaxy Z Fold e no Galaxy Watch SM-L330 em 2026-10-02, com o disparador debug do relógio
updated: 2026-10-02
---

# CV7.TS3 — Ponte Data Layer entre o celular e o relógio

## Intent

O relógio fala com a quadra local do celular pelo Bluetooth (Wearable Data Layer), com o mesmo contrato do servidor, para a CV7.US2 só ter de montar a experiência no relógio.

## Scope

- **Contrato** (caminhos `/placar/local/…`, capabilities `placar_celular` e `placar_relogio`):
  - Relógio → celular: mensagem `comando` com o corpo de `POST /api/watch/comandos`.
  - Celular → relógio: mensagem `recibo` com `{id, status, recibo, estado}` (ou `{id, status, detail}`); o `id` casa a resposta com o lance.
  - Placar passivo: DataItem `estado`, publicado a cada mudança (também as do celular), sem a linha do tempo (limite de ~100 KB). O relógio recebe o último ao reconectar.
- **Celular:** `QuadraLocal.aplicarComandoRelogio` (recibos gravados com o log, reenvio sem duplicar, lance de partida antiga recusado, desfazer por `alvo_seq` ou `alvo_comando`, nova partida só depois do fim); ponte JS `ponteRelogio.js`; plugin Capacitor `PlacarRelogio` e `RelogioListenerService` (Java), ligados enquanto a sala local está aberta.
- **Relógio:** `applicationId` passa a `br.com.placarvolei` (exigência do Data Layer: mesmo id e mesma assinatura); `CelularLink`, `RespostasEsperadas` e `CelularListenerService`; disparador `DebugCelular` só na build debug.
- **Plano B** (Navigator, 2026-10-02): o JS do WebView para ~2 min depois de a tela apagar, mesmo com serviço em primeiro plano e wake lock parcial (spike). A quadra local mantém a tela acesa e a fila offline do relógio guarda os lances quando o celular não responde.
- O relógio e o celular operam juntos: na quadra local não há passagem de controle (o relógio é o participante `relogio-local`, com o controle sempre dele).

## Acceptance / Done Condition

Given a quadra local aberta no celular e o relógio pareado
When o relógio envia um ponto pelo Data Layer
Then o celular aplica o ponto na quadra local, responde com o recibo e o estado, e publica o estado novo
And o relógio recebe e mostra o mesmo placar
And o mesmo comando reenviado não conta duas vezes
And um comando de partida antiga é recusado com aviso

## Validation Route

`web/tests/comandoRelogio.test.js`, `web/tests/ponteRelogio.test.js`, `CelularProtocoloTest.kt`. No aparelho, o disparador debug do relógio:

```bash
DBG="-n br.com.placarvolei/br.com.placarvolei.watch.DebugCelular"
adb -s <relógio> shell am broadcast $DBG -a br.com.placarvolei.watch.DEBUG_ESTADO
adb -s <relógio> shell am broadcast $DBG -a br.com.placarvolei.watch.DEBUG_PONTO --es equipe A
adb -s <relógio> shell am broadcast $DBG -a br.com.placarvolei.watch.DEBUG_DESFAZER
adb -s <relógio> logcat -d -s CelularDebug
```

Resultado de 2026-10-02: ponto A, A, B e desfazer aplicados (recibos `APLICADO`); com o celular fora da sala o lance ficou na fila do relógio (`SEM_REDE`) e, reaberta a sala, entrou uma vez só.

## Out of Scope

A escolha do modo no relógio (local ou servidor) e as telas dele (CV7.US2); várias quadras locais; release assinado.

## Known Limits

- Com a tela do celular apagada o relógio fica sem resposta: `debt-quadra-local-so-atende-relogio-com-tela-acesa`.
- O canal só se valida no aparelho: `debt-apk-caminhos-nativos-sem-teste-automatico`. O release exige a mesma keystore nos dois apps: `debt-apk-release-sem-assinatura`.
- Trocar o `applicationId` do relógio exige desinstalar o app antigo (`…watch`) e revincular as quadras do servidor.
