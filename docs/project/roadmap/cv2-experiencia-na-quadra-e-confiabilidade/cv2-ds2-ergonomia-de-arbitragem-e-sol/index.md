---
code: CV2.DS2
level: Delivery Story
status: Validated
status_reason: Implementado na Onda 2 e validado pelo Navigator em 2026-09-16
updated: 2026-09-16
related:
  - docs/project/briefing.md
  - docs/project/roadmap/cv2-experiencia-na-quadra-e-confiabilidade/index.md
---

# CV2.DS2 — Ergonomia de Arbitragem e Visibilidade Extrema

## Intent

O árbitro segura o aparelho com uma mão ou na horizontal sob sol escaldante de quadra e apita a partida sem atritos ergonômicos, sem a tela bloquear e com visibilidade nítida.

## Scope

- **US1 — Modo Quadra em Paisagem (A1, §11.5):** Detecção automática de orientação horizontal para admin/controlador, exibindo tela cheia dividida em 2 metades gigantes para toque nos botões de ponto sem rolagem, botão desfazer fixo e ocultação de elementos secundários.
- **US2 — Zona do Polegar no Retrato (11.4):** Posicionamento fixo dos botões de marcação e desfazimento no rodapé da tela (`sticky bottom`), com números no topo e ações secundárias agrupadas em menu compacto.
- **US3 — Screen Wake Lock (A6):** Integração com a API `navigator.wakeLock` para impedir que o celular ou tablet apague a tela por inatividade durante a partida.
- **US4 — Tema \"Modo Sol\" de Alto Contraste (A8, §9.4):** Fundo claro, números pretos em 21:1 de contraste, sem gradientes escuros e sem sombras neon/glow que geram borrões no reflexo solar.
- **US5 — Governança de Controle e Prevenção de Perda (A4):** Separação de permissão versus transferência ativa, bloqueio de repasse para participantes offline e auto-retorno do controle para o admin após 15s de ausência do controlador.
- **US6 — Unicidade de Apelidos (A5):** Prevenção de apelidos duplicados na mesma quadra, evitando personificação de participantes.
- **TS1 — Reconexão do WebSocket com Backoff (M16):** Backoff exponencial com jitter e indicação visual discreta de restabelecimento.

## Acceptance / Done Condition

- Árbitro opera com celular deitado marcando pontos em tela cheia sem nenhuma barra de rolagem.
- A tela permanece ligada durante toda a partida.
- O tema Sol permite leitura clara do placar sob luz solar direta sem efeito de ofuscamento.
- O controle da partida não é transferido acidentalmente para quem está desconectado.

## Validation Route

- Teste de viewport horizontal em aparelho móvel (812×375).
- Teste sob iluminação solar forte alternando entre Modo Noite e Modo Sol.
- Simulação de inatividade de 3 minutos para verificação do Wake Lock.
- Cenário de desconexão de controlador para verificar o auto-retorno ao admin.
