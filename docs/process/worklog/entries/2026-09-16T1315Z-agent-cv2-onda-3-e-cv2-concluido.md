---
date: 2026-09-16T13:15:00Z
author: Antigravity (Driver)
kind: milestone
related:
  - CV2
  - CV2.DS3
  - debt-acessibilidade-e-overflow
verification:
  - uv run pytest (114 passed)
  - npm --prefix web test (21 passed)
  - npm --prefix web run check (0 errors, 0 warnings)
  - uv run ruff check . (all checks passed)
  - uv run ruff format --check . (154 files already formatted)
  - Validado manualmente na interface web pelo Navigator
---

# Conclusão da Onda 3 do CV2: Layouts Fluidos, Home ao Vivo, Acessibilidade WCAG e Fechamento Total do CV2

## What changed

Concluímos a implementação e validação completa da Onda 3 (`CV2.DS3`), finalizando 100% da entrega de Capability Value 2 (CV2) e quitando o último débito técnico remanescente do projeto (`debt-acessibilidade-e-overflow`):

1. **Responsividade Fluida e Proteção Global contra Overflow (`CV2.DS3.US1`)**:
   - `web/src/app.css` reforçado com `overflow-x: hidden; max-width: 100vw;`.
   - Grid de duas colunas fluidas para desktop (≥960px) em `HomePlacar.svelte`, posicionando o cartão de ação ao lado da lista de quadras ativas.
   - Zero rolagem horizontal indesejada em toda a faixa de 360px a 1440px.

2. **Home com Placares Ao Vivo e Entrada em 1 Toque (`CV2.DS3.US2`, `CV2.DS3.US3`)**:
   - Projeção leve síncrona do resumo da partida ativa (`pontos_a`, `pontos_b`, nomes dos times e status) em `GET /api/quadras` (`app/quadras.py`).
   - Cards de quadras na Home com badge pulsante `AO VIVO` e placar parcial em tempo real.
   - Entrada em 1 toque: ao clicar no card de uma sala ativa, se o usuário já possui apelido salvo, entra direto como espectador sem formulários redundantes.

3. **Placar do Espectador com Escala em Retrato (`CV2.DS3.US4`)**:
   - Proporções e container queries aprimoradas em `PlacarManual.svelte`, permitindo que os cartões e números gigantes aproveitem até ~40% da altura da tela móvel em retrato.

4. **Acessibilidade WCAG 2.2 e Alvos de Toque (`CV2.DS3.US5`)**:
   - Reabilitação de zoom de até 200% (`user-scalable` desbloqueado em `web/index.html` conforme WCAG 1.4.4).
   - Padronização de alvos de toque mínimos de 44×44px em todos os componentes (`HomePlacar`, `Placar`, `PlacarManual`, `SalaQuadra`) conforme WCAG 2.5.8.
   - Narração acessível dinâmica com classe `.sr-only` e `role="status" aria-live="polite"` em `Placar.svelte` narrando pontos e vitória em tempo real para leitores de tela.

5. **Quitação de Débito Técnico**:
   - `debt-acessibilidade-e-overflow` marcado como `status: Paid` no Technical Debt Ledger.
   - **Zero débitos técnicos remanescentes** no projeto.

6. **Roadmap**:
   - `CV2.DS3` marcado como `Done`.
   - `CV2` marcado como `Done` (100% concluído).

## Why it matters

Com a conclusão do CV2, o Placar de Vôlei atinge o mais alto patamar de usabilidade, ergonomia e confiabilidade:
- Pode ser usado sob sol intenso, com celular deitado ou em pé, sem telas apagando ou toques perdidos;
- Apresenta placares em tempo real para torcedores diretamente na tela inicial com entrada em 1 toque;
- É plenamente acessível para pessoas com baixa visão (zoom até 200%) e usuários de leitores de tela (`aria-live`);
- Oferece alvos de toque confortáveis sem acionamentos acidentais.

## Verification

- `uv run pytest`: 114 testes passando (100%).
- `npm --prefix web test`: 21 testes unitários passando.
- `npm --prefix web run check`: 0 erros e 0 warnings.
- `uv run ruff check .` e `uv run ruff format --check .`: Clean.
