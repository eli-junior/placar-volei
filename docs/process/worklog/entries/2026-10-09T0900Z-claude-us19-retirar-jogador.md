---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-09
related:
  - CV8.DS7.US19
  - CV8.DS7.TS3
  - time-vazio-e-pular-viram-ajustes-da-fila
---

# US19 + TS3: retirar jogador no meio da rodada (0.48.0)

- **Problema:** com a rodada ativa o jogador que foi embora não saía; a única saída era cancelar a rodada (QA F2).
- **Entrega:** TS3 (`ajustes_fila`, `derivar` com ajustes) e US19 (`POST /api/rodada/retirar` e `/pular-time`, vaga preenchida na vez de entrar, inclusive no mata-mata, **Retirar da rodada** e **Pular o Time N** na tela).
- **Decisão:** o time vazio e o "pular" são ajustes datados na derivação, não edições do estado (registro `time-vazio-e-pular-viram-ajustes-da-fila`).
- **Ambiente:** um worker do e2e deu SIGSEGV numa rodada e o mesmo teste passou ao reexecutar (instabilidade da máquina).
- **Validação:** feita pelo Navigator em 2026-10-09.
