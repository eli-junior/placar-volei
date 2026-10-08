---
author: Claude Opus 5.5 (Driver)
date: 2026-10-08
related:
  - CV8.DS7.US16
  - docs/qa/2026-10-08-auditoria-producao.md
  - docs/qa/2026-10-08-furos-de-logica-joguinho.md
---

# Auditoria do QA vira a CV8.DS7; anular partida chamada (0.46.2)

- **Sintoma (produção):** joguinho de ontem com partida chamada na Quadra 29397, que não existia mais depois do restart. Encerrar, trocar quadra e encerrar o joguinho estavam todos bloqueados; só restava cancelar a rodada, e nem isso destravava o vínculo.
- **Conferência no código:** os achados P1–P4 e F1–F3 se confirmaram. O P5 tem outra causa: um 429 não apaga o segredo, qualquer 404 apaga (US17). O P7 não vale para o clone do WSL.
- **Correção:** "Anular partida" (decisão do Navigator: só anular, sem placar manual por ora); cancelar apaga a chamada; a trava do vínculo olha só a rodada em andamento.
- **Lição:** toda trava de estado precisa de uma saída que não dependa de outro sistema (o placar efêmero). A causa de fundo (quadra efêmera × joguinho durável) segue na TS2.
