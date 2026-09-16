---
date: 2026-09-16T12:35:00Z
author: Antigravity (Driver)
kind: milestone
related:
  - CV2.DS2
  - CV2.DS4
  - debt-modais-ad-hoc-e-reconexao
  - debt-apelidos-e-transferencia-de-controle
  - debt-tokens-e-cores-acopladas
verification:
  - uv run pytest (113 passed)
  - npm --prefix web test (21 passed)
  - npm --prefix web run check (0 errors, 0 warnings)
  - uv run ruff check . (all checks passed)
  - uv run ruff format --check . (152 files already formatted)
  - Validado manualmente na interface web pelo Navigator
---

# Conclusão da Onda 2 do CV2: Ergonomia, Modais Nativos, QR Code, Celebração e Configuração In-Game

## What changed

Concluímos a implementação e validação completa da Onda 2 da Capability Value 2 (CV2):

1. **Ergonomia e Modos de Visualização (`CV2.DS2`)**:
   - **Modo Paisagem Otimizado (US1)**: Layout horizontal sem rolagem vertical desnecessária com divisão 50/50 entre equipes e botão de desfazer sempre acessível.
   - **Zona do Polegar no Retrato (US2)**: Botões grandes e confortáveis agrupados no terço inferior da tela móvel com feedback háptico e estado `aria-busy`.
   - **Screen Wake Lock (US3)**: Prevenção de bloqueio de tela via `navigator.wakeLock` enquanto a partida estiver ativa, com reativação automática em `visibilitychange`.
   - **Modo Sol de Alto Contraste (US4)**: Alternância dinâmica com atributo `data-tema="sol"` no cabeçalho da quadra e da Home, otimizando visibilidade sob luz solar direta sem efeito de glow.
   - **Governança de Controle e Apelidos Únicos (US5, US6)**: Bloqueio de repasse de controle para participantes offline, auto-retorno ao admin após 15s de ausência do operador e unicidade de apelidos por sala com validação case-insensitive.
   - **Reconexão Resiliente (TS1)**: Cliente WebSocket com backoff exponencial e jitter aleatório.

2. **Celebração, Modais Nativos e Compartilhamento (`CV2.DS4`)**:
   - **Diálogo Nativo (`<dialog>`)**: Componente `Dialogo.svelte` com foco gerenciado, tecla Escape e fechamento no clique do backdrop, adotado por todos os modais.
   - **QR Code SVG Puro e Web Share**: Geração local de QR Code SVG sem CDNs (`qrcode.js`), botão de cópia de link e integração com `navigator.share`.
   - **Celebração de Vitória**: Tela comemorativa com troféu pulsante, cores do campeão e atalhos rápidos.
   - **PWA & Fontes Locais**: Manifesto Web PWA, ícones adaptativos e fontes locais WOFF2 latin (Inter e Teko).

3. **Onboarding Ultralight e Ciclo de Múltiplas Partidas (Solicitação do Navigator)**:
   - Formulário de criação na Home ultralight (apenas apelido e nome opcional).
   - Configuração de duplas e regras pós-criação in-game e no reinício de partidas na mesma sala via `POST /api/quadras/{id}/configurar` e `POST /api/quadras/{id}/reiniciar`.

4. **Technical Debt Ledger**:
   - Quitação de `debt-modais-ad-hoc-e-reconexao`, `debt-apelidos-e-transferencia-de-controle`, `debt-tokens-e-cores-acopladas`, `debt-codigo-mestre-no-websocket`, `debt-lotacao-fantasma` e `debt-integridade-de-toques-e-erros-422`.

## Why it matters

O Placar agora atinge excelência real de operação à beira da quadra:
- O criador não perde tempo preenchendo duplas antes de entrar na quadra;
- A mesma sala é reutilizada para toda a sessão de jogos, com troca de jogadores entre rodadas sem desconectar os espectadores;
- O celular não apaga a tela durante a partida e pode ser operado facilmente na horizontal ou com uma mão;
- O visual sob o sol é nítido e sem reflexos;
- A base de código eliminou modais ad-hoc, dependências de QR code e vazamentos de controle.

## Verification

- `uv run pytest`: 113 testes passando (0 falhas).
- `npm --prefix web test`: 21 testes unitários do frontend passando.
- `npm --prefix web run check`: 0 erros e 0 warnings no Svelte.
- `uv run ruff check .` e `uv run ruff format --check .`: 100% de conformidade.
- Validação interativa conduzida e aprovada pelo Navigator.
