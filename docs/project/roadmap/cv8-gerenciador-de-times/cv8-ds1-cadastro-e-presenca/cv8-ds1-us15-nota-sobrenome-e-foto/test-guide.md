# Rota de validação — CV8.DS1.US15 Nota, sobrenome e foto

## Preparação (local)

```bash
cd web && npm run build && cd ..
OWNER_SECRET=meu-segredo GERENCIADOR_DB_PATH=/tmp/gerenciador-teste.db uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Para testar a câmera no celular é preciso HTTPS (o túnel do Mini PC) ou o endereço `localhost`; use o computador para o resto. Abra `/jogadores` e entre com `meu-segredo`.

## Passos e observações

1. **Nome com 2 palavras:** cadastre "Ana" (Mulher) → **Passa:** erro "Nome deve ter nome e sobrenome"; nada gravado. Cadastre "Ana Souza" → entra na lista.
2. **Nota padrão:** deixe a nota vazia → **Passa:** a lista mostra "Mulher · nota 60".
3. **Nota informada e inválida:** 87 grava; 0, 101 e 7,5 → **Passa:** erro no campo "Nota" e nada gravado. Editar a nota para 95 atualiza a lista.
4. **Foto no cadastro:** toque em **Tirar foto** (no celular abre a câmera traseira; no computador, o seletor de arquivo) → **Observa:** pré-visualização redonda. Salve → **Passa:** a miniatura aparece na lista; recarregue a página e ela continua.
5. **Trocar e remover foto:** edite o jogador, **Trocar foto**, salve; depois **Remover foto**, salve → **Passa:** voltam as iniciais (ex.: "AS").
6. **Jogadores da 0.31.0:** com um banco antigo (jogadores de uma palavra só), eles continuam listados com nota 60; ao editar, o sistema pede o sobrenome. Reativar um inativo antigo funciona sem reescrever o nome.
7. **Persistência:** suba o servidor com `RESET_DB_ON_STARTUP=true` → **Passa:** jogadores, notas e fotos continuam.
8. **Segredo:** sem o `x-owner-secret`, `GET /api/jogadores/<id>/foto` responde 404; a foto não abre por URL solta.
9. **APK:** a tela de jogadores segue oculta.

## Evidência automatizada

`uv run pytest` (290; 16 novos da US15), `npm test` (172), `npm run check`, `npm run test:e2e` (58, com axe da tela).
