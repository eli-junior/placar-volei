# Rota de validação — CV8.DS3.US6 Encerrar partida e aplicar rei da quadra

## Preparação (local)

```bash
cd web && npm run build && cd ..
OWNER_SECRET=meu-segredo GERENCIADOR_DB_PATH=/tmp/gerenciador-teste.db uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Use **8 jogadores** (a tabela da US3) para ter 4 times, ou **10** para ter 5. Abra a **Sessão**, marque a presença, **sorteie** (alvo 10 é mais rápido), **confirme**, **Criar quadra e vincular** e abra o link **Abrir o placar** em outra aba (ou outro aparelho). Dica: se tiver dois aparelhos, deixe o gerenciador em um e o placar no outro.

## Passos e observações

1. **Partida 1:** **Chamar partida** → o placar mostra as duas duplas. No gerenciador o botão vira **Encerrar partida** (desabilitado) com "Em jogo no placar (0 × 0)".
2. **Placar ao vivo:** marque pontos no placar → **Passa:** o gerenciador mostra "Placar: 4 × 0 — em jogo" **sem atualizar**. **Encerrar partida** continua desabilitado.
3. **Recusa em jogo:** pela API ou forçando o clique (ele está desabilitado) o servidor recusa com o placar parcial; nada é gravado.
4. **Terminar a partida (10 × 3, por exemplo):** → **Passa:** "terminou — Time 1 venceu" e **Encerrar partida** habilita sozinho. Toque → **Passa:** aparece "Partidas encerradas (1)" com "Time 1 10 × 3 Time 2 — Time 1 venceu"; o Time 2 vira **eliminado** (seus 2 jogadores em "Eliminados"); o Time 1 fica em quadra com "1 vitória seguida" e a próxima partida é **Time 1 × Time 3**. Em outro aparelho a fila andou sozinha.
5. **Partida 2 com 2ª vitória do Time 1:** chame, termine com o Time 1 vencendo → **Passa:** "Reis (1)" com "1º rei · Time 1"; o Time 1 sai da quadra e entram **os dois próximos da fila** (Times 4 e 5 com 10 jogadores; com 8 jogadores a fila fica mais curta).
6. **Fim da fila:** com 6 jogadores (3 times): o Time 1 vence o 2; o Time 3 vence o Time 1 → **Passa:** faixa "A fase de fila terminou. Próxima fase: mata-mata — Time 3 segue" e **Chamar partida** não aparece habilitado (o mata-mata é a US11).
7. **Partida trocada no placar:** chame uma partida, jogue até o fim e, antes de encerrar, use "nova partida" no placar → **Passa:** **Encerrar partida** fica desabilitado com "O placar está com outra partida…" e a API recusa ("trocada").
8. **Quadra indisponível:** reinicie o servidor com uma partida chamada → **Passa:** a rodada e a partida chamada continuam; o painel diz que a quadra não está disponível; o resultado não pode ser lido (cancele a rodada ou vincule outra quadra para as próximas).
9. **Cancelar com partidas:** **Cancelar rodada** → **Passa:** o aviso diz "já tem N partida(s) registrada(s)… ficam gravadas"; confirme e a presença volta a ser editável.
10. **Persistência:** com partidas encerradas, reinicie (também com `RESET_DB_ON_STARTUP=true`) → **Passa:** histórico, reis e eliminados continuam.
11. **APK:** os botões "Sessão" e "Jogadores" continuam ausentes.

**Falha:** fila que não anda, rei coroado com uma vitória só, eliminado que volta, placar que não atualiza o painel, ou encerrar uma partida que ainda está em jogo.

## Evidência automatizada

`uv run pytest` (483, depois de enxugar as composições do teste de gênero do sorteio; 15 novos desta história: encerrar com placar real em todas as situações — em jogo, vencedor A e B, sequência até rei e fim da fila, partida trocada, quadra sumida, concorrência —, e o aviso do placar ao painel), `npm test` (182), `npm run check`, `npm run test:e2e` (75, com um fluxo completo: placar ao vivo, encerrar, rei, fim da fila, dois aparelhos e axe).
