---
code: CV6.DS1.US8
level: User Story
status: Done
status_reason: validado e aceito pelo Navigator em 2026-09-28; entregue na 0.23.0
updated: 2026-09-28
---

# CV6.DS1.US8 — Admin libera a quadra

## Intent

Ao fim do jogo, o admin encerra a quadra na hora, sem esperar a expiração por inatividade.

## Scope

- `POST /api/quadras/{id}/liberar`: só ADMIN (403 para os demais, 404 se não existe). Apaga quadra, eventos, participantes, partidas e recibos do relógio pela mesma rotina da expiração.
- Todos os sockets recebem `SALA_EXPIRADA` com `motivo: liberada` e são fechados com 4404.
- Web: "Liberar quadra" no fim do ⚙ completo, só para o admin, com confirmação em dois passos. Quem liberou vê "Quadra liberada."; os demais, "A quadra foi liberada pelo administrador."

## Acceptance / Done Condition

Given sou admin e há um espectador conectado
When toco em Liberar quadra e confirmo em Liberar agora
Then os dois aparelhos voltam à tela inicial com suas mensagens
And o código da quadra deixa de funcionar
And o espectador nunca vê o botão

## Validation Route

`tests/test_liberar_quadra.py`, `web/e2e/liberar-e-selo.spec.js`; Navigator validou em aparelho.

## Out of Scope

Aviso especial no relógio (recebe o 404 de quadra expirada); histórico de quadras liberadas.
