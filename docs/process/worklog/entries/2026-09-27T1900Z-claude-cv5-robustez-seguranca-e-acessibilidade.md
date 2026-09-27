---
date: 2026-09-27T19:00:00Z
author: Claude Code (Opus 5.5)
kind: milestone
related:
  - CV5
  - lobby-publico-e-pin-como-identificador
  - remocao-de-arenas-e-banco-limpo-no-versionamento
verification:
  - pytest (221 passed); ruff limpo
  - svelte-check, node --test e vite build (Node do Windows)
  - gradlew testDebugUnitTest assembleDebug assembleRelease lintDebug
  - testes em produção (0.20.0) e validação do Navigator em 2026-09-27
---

# CV5: robustez, segurança e acessibilidade (0.20.0)

Uma revisão com quatro especialistas (backend, Svelte, Wear OS e UX) virou o CV5, com 5 Delivery Stories e 13 histórias. O Navigator aprovou os planos e autorizou o automode. Cada história ficou na própria branch com status `Validated`, e todas foram juntadas na `integracao/cv5` para um teste único. Depois do aceite, a integração entrou na `master`.

Pontos que valem lembrar:

- O lobby público é funcionalidade, não vazamento: o PIN identifica a sala e não a protege.
- O banco de produção é apagado a cada start do contêiner, por escolha do Navigator. A persistência feita na TS2/TS3 continua valendo fora do compose.
- O `@ts-check` achou um bug real: o QR do "Compartilhar" nunca aparecia. A leitura do código também achou o backoff do web zerando a cada tentativa.
- O `checkJs` nos `.svelte` ficou como débito, porque as props de callback saem tipadas como `Function`.
