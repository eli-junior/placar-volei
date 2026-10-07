---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-07
related:
  - CV8.DS3.US8
---

# CV8.DS3.US8 — parceiro do time incompleto entregue (0.37.0)

- **Entrega:** lista de escalação (RN-07) calculada no servidor, com gênero (RN-01) e ordem de chegada; `POST /api/rodada/escalar-parceiro` com validação na transação; escalado em dois times (histórico e saldo dobrado); eliminados sem o escalado enquanto ele joga; "Saldo da rodada" no painel; `times.origem` pronta para a US9. Destrava as rodadas de número ímpar.
- **Achado de produto:** o grupo "ainda não jogaram" da RN-05 é vazio por construção (o incompleto é o último da fila); a lista de escalação é a que vale. Registrado nas regras.
- **Achado de teste:** o teste da US5 sobre o bloqueio do incompleto mudou de texto ("Escolha o parceiro do Time 6…").
- **Evidência:** pytest 507 (24 novos), `npm test` 183, e2e 76 (axe incluído); validada pelo Navigator.
- **Dívidas abertas:** `rodada.py` concentra regras/painel/escalação, escalação sem como desfazer, rodada trava sem elegíveis; agravada: `Sessao.svelte` com 362 linhas (acima do gatilho).
