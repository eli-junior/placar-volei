---
id: debt-apk-caminhos-nativos-sem-teste-automatico
status: Carried
kind: test
severity: low
source: CV7.US1
revisit_trigger: Mudança em `requisitarPadrao` ou `armazenamentoPadrao`, atualização do Capacitor, ou falha no aparelho que o e2e não pegou
closure_condition: Teste instrumentado (ou um stub do plugin que rode o mesmo código) cobrindo `CapacitorHttp.get` no `/health` e `Preferences` na quadra local, rodando fora do aparelho do Navigator
---

# Caminhos Nativos do APK sem Teste Automático

## Description

O teste de conexão (`CapacitorHttp`) e a persistência (`@capacitor/preferences`) só rodam no APK. O e2e usa o `fetch` e o `localStorage`, com o Capacitor simulado, e a paridade entre os dois caminhos depende de validar no aparelho. Foi assim que a folha do menu ⋯ saiu cortada pela barra do sistema: o navegador não tem essa barra.

## Carrying Reason

Teste instrumentado de Android exige emulador ou aparelho no CI, e o projeto valida o APK na máquina do Navigator. O custo não se paga para um APK de uso pessoal.

## Updates

- 2026-10-02 (CV7.TS3): cresceu. O plugin `PlacarRelogio`, o `RelogioListenerService`, o `CelularLink` e o `CelularListenerService` só rodam com o Play Services nos dois aparelhos. O bug de devolver o proxy do plugin de uma função `async` ("`.then()` is not implemented") só apareceu no aparelho. A parte pura (contrato, respostas casadas por id, recibos, ponte JS) tem teste automático; a validação do canal é o roteiro com `adb` e o disparador `DebugCelular`.

## Notes

O roteiro físico da história cobre o que o e2e não alcança. Ver `debt-apk-release-sem-assinatura` para a mesma limitação no CI.
