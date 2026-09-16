---
id: debt-integridade-de-toques-e-erros-422
status: Paid
kind: reliability
severity: medium
source: CV1.DS1.US2
revisit_trigger: Relato de ponto marcado que não apareceu no placar, ou mensagem de erro ilegível na UI
closure_condition: Botão de ponto com estado de envio explícito, bloqueio visível quando o WebSocket cai e erros 422 exibidos como texto compreensível
---

# Toques Descartados em Silêncio e Erros 422 Ilegíveis

## Description

Dois sintomas com a mesma raiz: a UI não representa o estado de transporte da ação.

1. **Toques perdidos (C3):** o botão `+1` não sinaliza processamento. Em rede instável, toques rápidos consecutivos podem ser descartados sem nenhum retorno visual, e com o WebSocket desconectado os botões continuam clicáveis, marcando às cegas.
2. **Erros ilegíveis (A7):** respostas de validação do FastAPI (HTTP 422) chegam como objeto estruturado (`detail` é uma lista de dicionários) e são renderizadas como `"[object Object]"` na interface, sem qualquer descrição útil.

À beira da quadra, os dois casos produzem a mesma perda de confiança: o árbitro não sabe se o ponto entrou.

## Carrying Reason

O fluxo otimista do placar foi construído na `CV1.DS1.US2` assumindo rede local estável no Mini PC. O uso real em 4G de quadra expôs a lacuna.

## Revisit Trigger

Qualquer mudança no caminho de envio de comandos do frontend ou no tratamento de exceções da API.

## Closure Condition

`aria-busy` ou estado de pulso no botão de ponto durante o envio, desabilitação explícita com indicador de reconexão quando o socket cai, e handler de `RequestValidationError` no backend normalizando 422 para mensagem legível consumida pelo frontend.

## Notes

Pago por `CV2.DS1` (escopos C3 e A7).
