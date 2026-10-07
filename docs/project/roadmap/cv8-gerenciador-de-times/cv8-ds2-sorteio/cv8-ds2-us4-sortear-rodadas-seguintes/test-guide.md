# Guia de validação — CV8.DS2.US4

## Automatizado

`uv run pytest` (533, com `tests/test_reequilibrio.py`), `npm run check`, `npm run test:e2e` (77).

## Rota do Navigator

1. Jogue a rodada 1 com 10 presentes até o campeão, com placares desiguais. 2. Sorteie a rodada 2: notas com ajuste ("Ana (68 +8)"), aviso "Reequilibrada pelo saldo". 3. As duplas da rodada 1 não se repetem sem necessidade. 4. **Resortear** varia a combinação. 5. A nota cadastrada não muda. 6. Após cancelar uma rodada, o sorteio usa as notas cadastradas.

**Aprova:** tudo acima. **Reprova:** nota sem ajuste, dupla repetida sem necessidade, cadastro alterado.
