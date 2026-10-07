# Rota de validação — CV8.DS1.US1 Cadastrar jogadores

## Preparação (local)

```bash
cd web && npm run build && cd ..
OWNER_SECRET=meu-segredo GERENCIADOR_DB_PATH=/tmp/gerenciador-teste.db uv run uvicorn app.main:app --port 8000
```

Abra `http://localhost:8000`.

## Passos e observações

1. Na Home, toque em **Jogadores**. Digite um segredo errado → **Observa:** alerta "Segredo recusado"; nada da lista aparece. **Passa:** o alerta aparece. **Falha:** a lista abre.
2. Digite `meu-segredo` → **Observa:** formulário "Novo jogador" e lista vazia ("Nenhum jogador ativo").
3. Cadastre "Ana" (Mulher) → **Observa:** Ana na lista de ativos com "Mulher".
4. Cadastre "ana", depois "Ána" → **Observa:** erro "já está em uso"; a lista continua com uma Ana só.
5. Cadastre sem nome, depois sem gênero → **Observa:** erro apontando o campo, foco nele; nada gravado.
6. Edite Ana para Homem; renomeie para o nome de outro ativo → **Observa:** salva o gênero; o nome repetido é recusado.
7. Inative Ana → **Observa:** ela vai para "Inativos"; cadastrar outra "Ana" agora funciona; reativar a primeira é recusado (nome em uso).
8. Recarregue a página → **Observa:** entra sem pedir o segredo. "Esquecer segredo neste aparelho" volta ao pedido.
9. **Persistência:** pare o servidor (Ctrl+C), suba de novo com `RESET_DB_ON_STARTUP=true` → **Passa:** os jogadores continuam; as quadras, não.
10. **APK:** instale o APK 0.31.0 → **Passa:** não há botão "Jogadores" na tela inicial do app nem na quadra online aberta pelo app.

## No Mini PC (após deploy)

`docker compose up -d --build`; cadastre um jogador; `docker compose up -d --force-recreate`; **Passa:** o jogador continua (volume `gerenciador-dados`). `docker volume ls` deve listá-lo.

## Evidência automatizada

`uv run pytest` (274, incluindo os 12 da US1), `npm test` (169), `npm run check`, `npm run test:e2e` (56, com 5 novos e axe da tela).
