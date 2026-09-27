---
code: CV5.DS2.TS1
level: Technical Story
status: Done
status_reason: aceito pelo Navigator em 2026-09-27 (teste conjunto da integracao/cv5)
human_validation: accepted
updated: 2026-09-27
---

# CV5.DS2.TS1 — Armazenamento que se recupera

## Scope
- `CredentialStore.read()` com `runCatching`: chave inválida apaga o vínculo e pede novo pareamento (`CredentialStore.kt:20`).
- Fila corrompida vira `.corrupt` com aviso na tela, em vez de fila vazia (`CommandQueue.kt:67`).
- Token em memória no `CredentialStore`, invalidado ao salvar ou promover (`WatchModel.kt:208,414`).
- WebSocket não abre com `Bearer null` (`WatchModel.kt:381`).

## Acceptance
- Dado um arquivo de fila corrompido, quando o app abre, então avisa que há lances ilegíveis e não finge fila vazia.
- Dada uma chave do Keystore invalidada, então o app abre na tela de pareamento, sem crash.

## Plano

[plan.md](plan.md) — branch `feature/cv5-ds2-ts1-armazenamento-que-se-recupera`.

## Revisão (Passo 5)

- **Feito:** `CredentialStore.read` com recuperação e `lostLink`; token em cache; `connectPresence` sem `Bearer null`; `CommandQueue.load` guarda `.corrupt-*` e marca `corrupted`; aviso "Lances antigos ilegíveis" no placar.
- **Testes:** 46 testes JVM (2 novos), build de debug e lint verdes (12 avisos, os mesmos da `master`).
- **Considerado e não feito:** teste JVM do `CredentialStore` (depende do AndroidKeyStore; ficaria só com mock). Coberto pelo roteiro físico.
- **Débito novo:** nenhum.
- **Validação humana pendente:** `adb shell run-as br.com.placarvolei.watch sh -c 'echo "{x" > files/fila-lances.json'` e abrir o app → aviso e placar seguem; `adb shell pm clear` não serve (apaga tudo) — para o Keystore, basta confirmar que o app abre normalmente após atualizar o APK.
