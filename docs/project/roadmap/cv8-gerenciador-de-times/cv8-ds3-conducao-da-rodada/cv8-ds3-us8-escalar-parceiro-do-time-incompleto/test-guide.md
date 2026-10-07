# Rota de validação — CV8.DS3.US8 Escalar parceiro do time incompleto

## Preparação (local)

```bash
cd web && npm run build && cd ..
OWNER_SECRET=meu-segredo GERENCIADOR_DB_PATH=/tmp/gerenciador-teste.db uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Use **5 jogadores** (número ímpar), cadastrados e marcados presentes **nesta ordem de chegada**: Hugo Um (H, 60), Iris Dois (M, 61), Joao Tres (H, 62), Kely Quatro (M, 63), Luca Cinco (H, 64). O último a chegar (Luca) fica sozinho e vai por último na fila. Sorteie (alvo 10), confirme, **Criar quadra e vincular** e abra o placar em outra aba.

## Passos e observações

1. **Painel inicial:** → **Passa:** Time 3 aparece na fila como incompleto ("escolhe o parceiro na sua vez").
2. **1ª partida:** **Chamar partida**, marque 10 pontos para o time A no placar, **Encerrar partida** → o Time 1 segue em quadra e o **Time 3 (incompleto) entra**.
3. **Lista de escalação:** → **Passa:** aparece o bloco **Escolher o parceiro do Time 3** ("Luca Cinco está sem dupla…") com a lista **"Lista de escalação (eliminados)"**. Como Luca é **homem**, só aparecem as **mulheres** do Time 2 eliminado (uma ou duas, conforme o sorteio); nenhum jogador do Time 1 (em quadra) aparece. **Chamar partida** está desabilitado com "Escolha o parceiro do Time 3 antes de chamar a partida."
4. **Escolher:** toque **Escalar** numa delas → **Passa:** o bloco some, o Time 3 aparece completo com "· escalado" ao lado do nome dela, ela **sai de "Eliminados"** e **Chamar partida** habilita. Em outro aparelho a escolha aparece sozinha.
5. **Recusa de H+H:** (via API, ou numa rodada com um homem eliminado no mesmo caso) escolher um homem havendo mulher elegível é recusado ("formaria dupla H+H…").
6. **Só homens:** numa rodada de 5 homens, o incompleto vê os homens eliminados com o aviso "Só há homens elegíveis: a dupla será H+H, por falta de alternativa".
7. **Saldo (CA5):** chame a 2ª partida (Time 1 × Time 3), deixe o Time 3 vencer e encerre → **Passa:** "Saldo da rodada" mostra a escalada com **2 partidas** e o saldo somando o que ela perdeu pelo Time 2 e ganhou pelo Time 3.
8. **Volta aos eliminados:** se o Time 3 perder, a escalada volta a aparecer em "Eliminados".
9. **Incompleta mulher:** com o último a chegar sendo mulher, a lista mostra **homens e mulheres**.
10. **Persistência:** reinicie o servidor (também com `RESET_DB_ON_STARTUP=true`) → **Passa:** a escolha continua gravada.
11. **APK:** "Sessão" e "Jogadores" continuam ausentes.

**Falha:** jogador em quadra ou rei na lista, H+H oferecido com mulher elegível, escalado ainda em "Eliminados" enquanto joga, ou chamar a partida sem escolher.

## Evidência automatizada

`uv run pytest` (506; 23 novos: lista de escalação com gênero e grupos, saldo dobrado, escolha na rodada com placar real, recusas, concorrência, origem atrasado, volta aos eliminados, migração 5→6), `npm test` (183), `npm run check`, `npm run test:e2e` (76, com o fluxo do ímpar completo, dois aparelhos e axe no bloco).
