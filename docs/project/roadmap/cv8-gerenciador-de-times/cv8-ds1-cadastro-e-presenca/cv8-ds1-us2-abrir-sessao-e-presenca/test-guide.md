# Rota de validação — CV8.DS1.US2 Abrir sessão e marcar presença

## Preparação (local)

```bash
cd web && npm run build && cd ..
OWNER_SECRET=meu-segredo GERENCIADOR_DB_PATH=/tmp/gerenciador-teste.db uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Abra `http://localhost:8000`. Cadastre antes 4 ou 5 jogadores em **Jogadores** (nome e sobrenome, gênero), ou use o cadastro rápido no passo 7. Para testar com dois aparelhos, abra a mesma URL no celular (rede local).

## Passos e observações

1. Na Home toque em **Sessão**, entre com `meu-segredo` → **Observa:** "Nenhuma sessão aberta" e o botão **Abrir sessão**.
2. Abra a sessão → **Observa:** "Presentes (0)" e "Faltam 4 para poder sortear (mínimo 4)"; os jogadores ativos aparecem em **Ausentes**.
3. Toque **Presente** em três jogadores, na ordem Ana, Bia, Caio → **Passa:** a lista mostra 1º Ana, 2º Bia, 3º Caio; o aviso muda para "Faltam 1".
4. Use **↓** na Ana e **↑** no Caio → **Passa:** a ordem muda (Bia, Caio, Ana); os botões dos extremos ficam desabilitados. Recarregue a página → a ordem se mantém.
5. **Desmarcar** a Bia e marcá-la de novo → **Passa:** ela vai para o fim (Caio, Ana, Bia) e as posições são renumeradas 1º, 2º, 3º.
6. Marque o quarto jogador → **Passa:** o aviso vira "Já dá para sortear".
7. **Cadastro rápido:** cadastre "Duda" sem sobrenome → erro "nome e sobrenome"; cadastre "Duda Lima" (Mulher, nota vazia) → **Passa:** ela entra presente no fim, com nota 60.
8. Com a sessão aberta, tente abrir outra (pela API ou em outro aparelho) → **Passa:** recusa "já existe uma sessão aberta".
9. Em **Jogadores**, inative um jogador presente → **Passa:** ele some da presença e as posições se recompactam; reativar não o recoloca.
10. Reinicie o servidor (também com `RESET_DB_ON_STARTUP=true`) → **Passa:** a sessão aberta, as presenças e a ordem continuam.
11. **Encerrar sessão** (com confirmação) → **Passa:** volta para "Nenhuma sessão aberta"; abrir outra começa vazia.
12. **APK:** os botões "Sessão" e "Jogadores" não aparecem na Home dentro do app.

**Falha:** posições repetidas ou fora de ordem, duas sessões abertas, ou presença que volta sozinha.

## Evidência automatizada

`uv run pytest` (303; 13 novos da US2, com abertura e marcação concorrentes), `npm test` (175), `npm run check`, `npm run test:e2e` (63, com axe na tela da sessão).
