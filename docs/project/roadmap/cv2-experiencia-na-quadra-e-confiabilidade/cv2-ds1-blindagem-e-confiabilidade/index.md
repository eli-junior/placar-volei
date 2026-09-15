---
code: CV2.DS1
level: Delivery Story
status: Validated
status_reason: escopo completo implementado e coberto por testes automatizados (98 passed, ruff e svelte-check limpos); aguardando validação manual multi-dispositivo do Navigator
updated: 2026-09-15
related:
  - docs/project/briefing.md
  - docs/project/roadmap/cv2-experiencia-na-quadra-e-confiabilidade/index.md
  - CV2.DS1.TS1
  - CV2.DS1.TS2
  - CV2.DS1.US1
  - CV2.DS1.US2
---

# CV2.DS1 — Blindagem e Confiabilidade do Placar em Tempo Real

## Intent

Garantir que a comunicação em tempo real seja estritamente segura e que o registro de pontos seja resiliente a redes instáveis e toques repetidos, eliminando descartes silenciosos e vazamentos de credenciais.

## Scope

1. **Blindagem do WebSocket (C1):** Garantir que `codigo_mestre` nunca seja transmitido via WebSocket em `ESTADO_INICIAL` ou `PLACAR_ATUALIZADO`.
2. **Capacidade Real & Prevenção de Fantasmas (C2):** O limite de 20 pessoas por sala passa a considerar apenas participantes com conexão ativa (ou expirar inativos rapidamente).
3. **Feedback e Integridade de Toques no +1 (C3):**
   - Indicação visual imediata de processamento no botão de ponto (`aria-busy="true"` ou estado de pulso).
   - Bloqueio/desabilitação visual explícita de botões de marcação quando o WebSocket estiver desconectado, com indicador claro de reconexão.
   - Prevenção de perda silenciosa de toques rápidos em conexões com latência.
4. **Normalização de Erros da API (A7):** Tratamento de respostas de validação FastAPI (422) no backend e frontend para exibir descrições compreensíveis em vez de `"[object Object]"`.

## Itens Entregues

| Código | Nível | Escopo do relatório | Pasta |
| --- | --- | --- | --- |
| `CV2.DS1.TS1` | Technical Story | C1 | `cv2-ds1-ts1-blindagem-do-websocket/` |
| `CV2.DS1.TS2` | Technical Story | C2 | `cv2-ds1-ts2-capacidade-por-presenca-efetiva/` |
| `CV2.DS1.US1` | User Story | C3 | `cv2-ds1-us1-integridade-de-toques-no-mais-um/` |
| `CV2.DS1.US2` | User Story | A7 | `cv2-ds1-us2-erros-compreensiveis-na-interface/` |

**Por que essa distribuição de códigos.** C1 e C2 são Technical Stories porque nenhuma superfície observável muda: o placar e o fluxo de entrada continuam iguais na tela, e o que muda é o contrato interno de projeção (C1) e a regra de capacidade (C2) — ambos verificáveis por teste e por inspeção, não por uso. C3 e A7 são User Stories porque a diferença está na tela de quem arbitra: o botão que responde ao toque e a frase que explica o erro. A ordem `TS1, TS2, US1, US2` segue a ordem do escopo original da Delivery Story (C1, C2, C3, A7).

## Acceptance / Done Condition

- Nenhum pacote de WebSocket contém a chave `codigo_mestre`.
- Toques rápidos consecutivos no +1 oferecem feedback visual imediato de envio e não são ignorados silenciosamente.
- Se o WebSocket desconectar, os botões de ponto indicam estado de espera/reconexão e não descartam toques às cegas.
- Erros 422 mostram textos explicativos na UI.

## Validation Route

Cada item entregue tem seu próprio `test-guide.md` com roteiro detalhado, condição de aprovação e condição de falha. A sequência recomendada para o Navigator:

1. `cv2-ds1-ts1-blindagem-do-websocket/test-guide.md` — inspeção dos frames do WebSocket no DevTools (2 clientes).
2. `cv2-ds1-ts2-capacidade-por-presenca-efetiva/test-guide.md` — limite baixado por `.env`, 3 clientes, abas fechadas e janela de presença.
3. `cv2-ds1-us1-integridade-de-toques-no-mais-um/test-guide.md` — cinco toques em `Slow 3G` e modo avião por 30 segundos.
4. `cv2-ds1-us2-erros-compreensiveis-na-interface/test-guide.md` — `curl` sobre o formato do 422 e mensagem na tela.

Verificação automatizada consolidada:

```bash
cd web && npm run check && npm test && npm run build && cd ..
uv run pytest -q
uv run ruff check . && uv run ruff format --check .
```

## Out of Scope

- Rotação do `codigo_mestre` de salas já existentes.
- Fila offline persistente de toques dados com o socket caído (recusa explícita, não aceitação otimista).
- Realce do campo culpado no formulário a partir do novo campo `erros` do 422 — o dado existe, o tratamento visual pertence à `CV2.DS3`.
- Ergonomia de arbitragem, design system e PWA, que são as Delivery Stories seguintes do CV2.

## Notes

Esta Delivery Story quita três débitos do ledger: `debt-codigo-mestre-no-websocket` (severidade alta, segurança), `debt-lotacao-fantasma` e `debt-integridade-de-toques-e-erros-422`. O fechamento formal dos itens em `docs/project/debt/items/` fica com o orquestrador na integração.

A decisão de desenho menos óbvia do bloco está em `cv2-ds1-ts2-capacidade-por-presenca-efetiva/plan.md`: a presença é lida na borda assíncrona e injetada como valor na transação síncrona, em vez de a transação chamar o hub, evitando tanto deadlock quanto dependência da persistência para o transporte.
