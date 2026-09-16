---
code: CV2
level: Value
status: Active
status_reason: Ondas 1 (CV2.DS1, CV2.DS3.TS1) e 2 (CV2.DS2, CV2.DS4) implementadas e validadas; Onda 3 em planejamento
updated: 2026-09-16
related:
  - docs/project/briefing.md
  - docs/product/principles.md
---

# CV2 — Excelência na Quadra e Confiabilidade do Placar

## Intent

O Placar de Vôlei atinge confiabilidade absoluta em condições reais de quadra (4G instável, luz solar direta, celular deitado), garantindo que toques nunca sejam perdidos silenciosamente, credenciais não vazem e a usabilidade de árbitros e torcedores seja ágil e sem atrito.

## Scope

- **DS1 (Blindagem & Confiabilidade):** Remoção de `codigo_mestre` no WebSocket, proteção contra lotação fantasma, prevenção de toques perdidos com feedback imediato no +1 e normalização de erros 422 da API.
- **DS2 (Ergonomia na Beira da Quadra):** Modo Quadra em paisagem (tela dividida para marcação rápida), barra de ações na zona do polegar, Screen Wake Lock (manter tela acesa) e tema claro \"Modo Sol\" de alto contraste sem reflexos de glow.
- **DS3 (Design System & Responsividade):** Consolidação de tokens tipográficos e raios, desacoplamento de cores dos times versus ações do sistema, eliminação de overflow no mobile/tablet e redesign da Home para busca e entrada rápida.
- **DS4 (Celebração, UX & Microcopy):** Tela de vitória memorável com cores do campeão, modais padronizados com `<dialog>`, ícones SVG Lucide, microcopy natural de quadra e suporte a compartilhamento e PWA.

## Acceptance / Done Condition

O árbitro conduz uma partida sob sol direto com o celular na horizontal marcando pontos com toques rápidos em rede instável, sem telas apagando, sem toques descartados e com torcedores acompanhando sem quebras de layout.

## Validation Route

Simulação em rede 4G com latência e jitter; teste visual sob alta luminosidade; inspeção de pacotes WebSocket para garantir ausência de credenciais; validação em viewports mobile (375x812, 812x375), tablet e desktop.

## Notes

Delivery Stories:
- `DS1`: Blindagem e integridade em tempo real.
- `DS2`: Ergonomia de arbitragem e visibilidade extrema.
- `DS3`: Sistema visual, layouts fluidos e acessibilidade WCAG.
- `DS4`: Celebração, microcopy e compartilhamento.
