---
id: apk-capacitor-e-quadra-local
status: Decided
raised: 2026-10-01
decided: 2026-10-01
deciders:
  - Eli (Navigator)
  - Claude Code (Driver)
related:
  - CV7
---

# APK Android por Capacitor e Quadra Local no Celular

## Question

Como levar o placar a um APK Android que funcione com ou sem internet e mantenha o relógio sincronizado quando o Mini PC não está ao alcance?

## Decision

- **Casca:** Capacitor em volta da web Svelte atual. Kotlin só na ponte com o relógio (Wearable Data Layer).
- **Modo por quadra:** *quadra online* (servidor, como hoje) ou *quadra local* (o celular guarda o log e é a fonte da verdade). Não se troca de modo no meio da partida.
- **Online no APK:** o servidor é fixo no build (`PLACAR_SERVIDOR`), sem campo editável; a tela testa `/health` e só então o WebView navega para a URL do servidor (mesma origem). Cookies `SameSite=lax`, URLs relativas e WebSocket seguem iguais; nenhuma mudança de backend.
- **Local no APK:** interface embarcada; log de eventos append-only no aparelho; projeção e regras portadas para JS com testes de paridade contra o Python (`adr-0001` vale também no celular).
- **Relógio offline:** transporte "Celular" pelo Data Layer (Bluetooth), com a mesma fila, `base_seq` e descarte com aviso do transporte "Servidor".
- **Identificador:** celular e relógio passam a usar `br.com.placarvolei` e a mesma chave de assinatura (exigência do Data Layer). A troca no relógio exige reinstalar e revincular.
- **Envio do histórico local ao servidor:** fica para depois (CV7.US3, fora desta rodada).

## Rationale

- Reaproveita toda a interface validada em quadra; o custo novo fica no que só o nativo faz.
- Navegar para o servidor no modo online evita sessão cross-site (cookie de terceiro no WebView) e qualquer CORS no FastAPI.
- Modo fixo por quadra evita fundir dois logs que divergiram, o que ameaçaria a confiança no placar.

## Options Considered

- App nativo Kotlin/Compose: reescreveria a interface e duplicaria manutenção.
- PWA/TWA: não acessa o Data Layer; não sincroniza com o relógio sem servidor.
- APK com interface embarcada falando com o servidor por `CapacitorHttp`: exigiria rever cookies e WebSocket cross-site; rejeitado por risco.

## Consequences

- A quadra local não tem espectadores remotos.
- Regras de pontuação passam a existir em Python e JS; a paridade é teste obrigatório.
- A keystore do APK fica só com o Navigator; nunca entra no repositório.
- APK e testes físicos são feitos na máquina do Navigator (Android SDK), como no Wear.
- Instalar com `adb install --user 0`: sem isso o Samsung duplica o app no perfil Dual App.
- Trocar de servidor exige novo build do APK (decisão do Navigator em 2026-10-01).

## Review Trigger

Pedido para continuar offline uma partida começada online, ou para espectadores na quadra local.
