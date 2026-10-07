# Guia de validação — CV8.DS4.US11 Conduzir o mata-mata

## Automatizado

- `uv run pytest` — 517 testes (inclui `tests/test_mata_mata.py`, mata-mata puro em `tests/test_conducao.py` e a migração 6→7).
- `cd web && npm run check && npm test && npm run test:e2e` — 77 testes e2e, com o fluxo do mata-mata em dois aparelhos e axe.

## Rota do Navigator (dois aparelhos)

Pré-requisito: a branch rodando (local: `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000` + `cd web && npm run build`), `OWNER_SECRET` no `.env`, dois aparelhos em `/` → Sessão com o segredo.

1. Marque 8 presentes, sorteie (alvo 10) e confirme; crie e vincule a quadra.
2. Jogue: Time 1 vence o Time 2 e depois o Time 3 (vira rei); o Time 4 sobra sozinho.
   - **Esperado nos dois aparelhos:** faixa "A fase de fila terminou. Time 4 abre o mata-mata contra Time 1…", botão **Iniciar mata-mata**; **Chamar partida** não aparece.
3. Toque em **Iniciar mata-mata**.
   - **Esperado:** "Próxima partida do mata-mata" com Time 4 × Time 1, nos dois aparelhos sem atualizar.
4. Chame, jogue até o fim (vença com o Time 1) e encerre.
   - **Esperado:** cartão "Campeões da rodada 1" com o Time 1, nos dois; a tela de sorteio volta.
5. Repita com 3 times (6 presentes): o Time 1 vence as duas e vira rei com a quadra vazia → o botão é **Coroar campeão** e já encerra a rodada.
6. Com 14 presentes (7 times, 2 reis), confirme a ordem: desafiante × 1º rei, o vencedor × 2º rei.
7. Recuse forjado: `curl -X POST /api/rodada/iniciar-mata-mata` sem segredo → 404; com segredo antes do fim da fila → 409.
8. Reinicie o servidor no meio do mata-mata: o confronto volta idêntico.

**Aprova:** tudo acima como esperado. **Reprova:** botão errado na fase, ordem dos rivais diferente da coroação, campeão só em um aparelho, ou sorteio não liberado.
