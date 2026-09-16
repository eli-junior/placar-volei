---
code: CV2.DS3
level: Delivery Story
status: Done
status_reason: Entregue integralmente na Onda 3 com layouts fluidos, Home ao vivo, entrada 1 toque, WCAG 2.2 e quitação de débito técnico
updated: 2026-09-16
related:
  - docs/project/briefing.md
  - docs/project/roadmap/cv2-experiencia-na-quadra-e-confiabilidade/index.md
---

# CV2.DS3 — Sistema Visual, Layouts Fluidos e Acessibilidade WCAG

## Intent

Estabelecer um sistema de design consistente e previsível, corrigindo vazamentos de layout e garantindo que o torcedor encontre e acompanhe sua quadra com facilidade em qualquer tamanho de tela.

## Scope

- **US1 — Eliminação de Overflow Mobile e Tablet (A2, A3):** Ajuste de `.equipes-grid` com CSS Grid auto-fit fluido e simplificação do header da sala no mobile para erradicar qualquer rolagem horizontal indesejada (`scrollWidth <= innerWidth`).
- **US2 — Redesenho da Home \"Entrar Primeiro\" e 2 Colunas Desktop (M8, §11.1-11.3):** Acesso prioritário a espectadores (campo de PIN destacado no topo com auto-preenchimento), lista \"Ao vivo agora\" exibindo placares parciais e layout de 2 colunas fluidas em telas largas (≥960px).
- **US3 — Entrada com 1 Toque a Partir da Lista de Quadras (A10, M3):** Toque em qualquer card da lista abre direto o modal \"Entrar na quadra\" com código fixado, apelido unificado e foco imediato no botão.
- **US4 — Placar do Espectador com Container Queries (M20, §11.6):** No celular em retrato, empilhar times verticalmente para renderizar números gigantes (40% da altura da tela); na paisagem ou telas largas, manter lado a lado. Opções secundárias em barra inferior.
- **TS1 — Consolidação de Tokens e Desacoplamento Semântico de Cores (A9, §8, §9, §10):** Redução de 40 fontes para escala de 8 degraus; 17 raios para 4; 20 sombras para 3. Cores Ciano e Laranja passam a ser de uso exclusivo dos Times A e B (ações do sistema e foco passam para neutros e amarelo marca). Anel de foco `:focus-visible` global.
- **US5 — Acessibilidade WCAG 2.2 (M1, M4-M7, M17):** Habilitação de zoom (`user-scalable`), alvos de toque mínimos de 44×44px, semântica ARIA para tabs/radios e anúncio live do placar com o nome dos times.

## Acceptance / Done Condition

- Zero rolagem horizontal em viewports de 360px a 1440px.
- Navegação completa por teclado revela anel de foco visível em todos os elementos interativos.
- Espectador em pé no celular visualiza placar com números ocupando a quase totalidade do palco.
- Nenhuma cor de time (ciano/laranja) é reutilizada em botões genéricos do sistema.

## Validation Route

- Teste automatizado com axe-core nas rotas principais e verificação de contraste de cores.
- Inspeção de layouts nas resoluções 360×740, 375×812, 768×1024, 1024×768 e 1440×900.
- Teste de navegação exclusivamente via teclado (Tab / Shift-Tab / Enter / Espaço).
