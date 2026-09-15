---
code: CV2.DS1
level: Delivery Story
status: Active
status_reason: Em planejamento e desenvolvimento ativo
updated: 2026-09-15
related:
  - docs/project/briefing.md
  - docs/project/roadmap/cv2-experiencia-na-quadra-e-confiabilidade/index.md
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

## Acceptance / Done Condition

- Nenhum pacote de WebSocket contém a chave `codigo_mestre`.
- Toques rápidos consecutivos no +1 oferecem feedback visual imediato de envio e não são ignorados silenciosamente.
- Se o WebSocket desconectar, os botões de ponto indicam estado de espera/reconexão e não descartam toques às cegas.
- Erros 422 mostram textos explicativos na UI.

## Validation Route

- Conexão WebSocket como participante espectador e asserção de que `codigo_mestre` não existe no payload recebido.
- Testes automatizados pytest no backend e testes de integração de rota.
- Simulação de latência de rede no navegador para observar o comportamento e feedback visual dos botões de ponto.
