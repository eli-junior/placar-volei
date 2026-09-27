# Plano — CV5.DS2.TS1 Armazenamento que se recupera

- **Nível:** Technical Story · **Branch:** `feature/cv5-ds2-ts1-armazenamento-que-se-recupera` · **Versão:** patch (APK)

## Scope
1. `CredentialStore.read()` (`CredentialStore.kt:32`) com `runCatching`: em falha (IV nulo, `AEADBadTagException`, chave invalidada), apaga o slot e devolve `null`. O `WatchModel` abre na tela de pareamento com o aviso "Vínculo perdido no relógio. Pareie de novo."
2. Token ativo em memória no `CredentialStore` (`cachedToken`), preenchido na primeira leitura e trocado em `saveToken`/`promotePending`/limpeza. Acaba o AES-GCM a cada requisição (`WatchModel.kt:208,414`).
3. `connectPresence` (`WatchModel.kt:381`) sai cedo com token nulo, sem abrir socket com `Bearer null`.
4. `CommandQueue.load()` (`CommandQueue.kt:67`): em falha de parse, renomeia para `fila-lances.json.corrupt-<timestamp>` e devolve `QueueState(corrupted = true)`. A `ScoreSync` expõe `lostQueue`; o placar mostra "Lances antigos ilegíveis. Confira o placar no telefone." até um toque para dispensar.

## Acceptance
- Dado um `fila-lances.json` truncado, quando o app abre, então o aviso aparece, o arquivo `.corrupt` fica guardado e o relógio segue marcando.
- Dada a chave do Keystore apagada (`adb shell` / teste instrumentado), quando o app abre, então vai para o pareamento, sem crash.
- Então nenhuma requisição sai com `Bearer null`.

## Design
Guardar o arquivo corrompido em vez de apagar permite perícia manual. Rejeitado: tentar recuperar parte da fila (JSON parcial não garante ordem nem idempotência).

## Out of Scope
Enviar o arquivo corrompido ao servidor; revisão de conflito (US4).

## Risks
Token em memória num ViewModel: se o processo morrer, relê do Keystore. Sem risco novo, porque o processo já tem acesso à chave.

## Validation
Testes JVM para `CommandQueue.load` corrompido e para o cache do `CredentialStore` (com um `Crypto` injetável); roteiro físico com arquivo corrompido via `adb push`.
