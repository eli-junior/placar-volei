# Plano — CV8.DS4.US12 Persistir sessão

Nível: User Story. Branch: `feature/cv8-ds4-us12-persistir-sessao`. Versão-alvo: **0.39.0** (minor).

O gerenciador já era durável (`gerenciador.db` em volume próprio, sem apagar dados de rodada iniciada). Esta história endurece e **prova** o que o CA1 pede, sem schema nem rota novos.

## Entra

1. `PRAGMA synchronous=FULL` em toda conexão do gerenciador (`conectar`).
2. Teste de retomada: após cada partida, o mata-mata e o campeão, reabrir o banco (`init_gerenciador_sync`) devolve o mesmo estado.
3. Teste de contrato do registro para ranking: partidas com placar, vencedor, fase e tempos; times; jogadores com nota e chegada; campeão.
4. Teste de que cancelar a rodada e encerrar a sessão não apagam partidas.
5. Guia de desenvolvimento: o que é persistido e quando.

## Fora do escopo

Tela de histórico/ranking (CA2), exportação, desfazer (US7), reequilíbrio (US4).
