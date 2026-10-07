# Plano — CV8.DS3.US8 Escalar parceiro do time incompleto

Nível: User Story. Branch: `feature/cv8-ds3-us8-escalar-parceiro-do-time-incompleto`. Versão-alvo: **0.37.0** (minor; backend, web e APK por consistência; Wear inalterado).

## O que a história entrega

Com número ímpar de jogadores, o time incompleto (1 jogador, por último na fila) acaba entrando em quadra e hoje **trava a rodada** ("escolha o parceiro", bloqueio da US5). Esta história destrava: quando o time incompleto chega à quadra, o painel mostra a **lista de escalação** (RN-07) e o operador escolhe o parceiro. O escolhido **joga por um segundo time** (o dele anterior já tinha perdido) e as duas participações contam no **saldo** dele.

## Como funciona

**Quando e quem (CA1, CA2, CA3)**
- Só quando o time incompleto está **em quadra** (a vez dele) e **antes** de chamar a partida. Chamada em andamento → recusa.
- **Ímpar** (CA2): primeiro o grupo "ainda não jogaram"; se vazio, a lista de escalação. **Atrasado** (CA3): sempre a lista de escalação. A origem do time fica numa coluna nova `times.origem` (`impar` | `atrasado`); a US9 (atrasados) só precisa gravar `atrasado`.

**Lista de escalação (RN-07, CA4) — calculada na hora, no servidor**
- **Elegíveis:** jogadores **eliminados** da rodada (de times que perderam) que **não estão** hoje em nenhum time ativo.
- **Excluídos:** quem está **em quadra**; membros de **reis** aguardando o mata-mata; o próprio incompleto e **outros incompletos/atrasados**; quem já foi escalado e ainda joga por outro time.
- **Gênero (RN-01):** se o incompleto é **homem**, as opções **mulher** aparecem e o **homem só aparece se não houver nenhuma mulher elegível** (H+H só sem alternativa); se é mulher, qualquer um (M+M é livre). O servidor **recusa** uma escolha H+H havendo alternativa.
- **Ordem:** dentro do que é permitido, por **ordem de chegada** (premia a pontualidade, como no resto da CV8).
- **"Ainda não jogaram":** como o incompleto é o **último da fila**, quando chega a vez dele todos os times à frente já jogaram, então esse grupo é **vazio por construção** e na prática vale sempre a lista de escalação. O grupo fica no código (definido como "jogadores da rodada sem partida disputada que não estão em time ativo") para os casos de atrasado/substituição das US9/US10.

**Escolher (`POST /api/rodada/escalar-parceiro {jogador_id}`)**
- Revalida tudo na transação (rodada em andamento, incompleto em quadra, sem partida chamada, jogador na lista permitida) e grava o jogador no time (`time_jogadores`, com a nota e a chegada do momento e a marca `escalado = 1`); o time passa a **completo**. As duas participações dele existem como duas linhas em times diferentes.
- Duas escolhas simultâneas: só uma vale (a segunda já não encontra incompleto).

**Painel**
- Bloco **Escolher o parceiro do Time N** no lugar do motivo de bloqueio: lista com nome, gênero, nota e botão **Escalar**; se H+H só por falta de alternativa, o aviso diz isso; se não houver ninguém elegível, mostra "ninguém elegível" (caso raro; hoje só resta cancelar a rodada).
- **Eliminados** deixa de mostrar quem foi escalado enquanto joga pelo segundo time (volta a aparecer se esse time também perder). O time mostra "(escalado)" ao lado do nome.
- Bloco **Saldo da rodada** (CA5): por jogador, partidas e saldo (= pontos feitos − sofridos em cada time em que atuou, somando os dois times do escalado). É a base do reequilíbrio da US4.

## Dados (schema 6, migração aditiva)

- `times.origem TEXT NOT NULL DEFAULT 'impar'`.
- `time_jogadores.escalado INTEGER NOT NULL DEFAULT 0`.

## API

- `POST /api/rodada/escalar-parceiro`.
- `conducao.escalacao` (quando o incompleto está em quadra): `time` (fila), `jogador`, `origem`, `grupos` (cada um com `rotulo` e `jogadores` com `id`, `nome`, `genero`, `nota`, `evita_hh`), `aviso_hh`.
- `conducao.saldos`: lista por jogador (`id`, `nome`, `partidas`, `saldo`).
- O gate de **Chamar partida** passa a dizer "Escolha o parceiro do Time N antes de chamar a partida".

## Aceite (BDD)

- Given o time incompleto em quadra e nenhuma partida chamada, Then o painel mostra a lista de escalação e **Chamar partida** fica bloqueado até a escolha.
- Given a lista, Then só aparecem jogadores eliminados que não estão em quadra, nem em time rei, nem em outro incompleto.
- Given o incompleto homem e ao menos uma mulher elegível, Then só mulheres são oferecidas e escolher um homem é recusado; sem nenhuma mulher elegível, os homens aparecem.
- Given o incompleto mulher, Then homens e mulheres são oferecidos.
- Given que escolho o parceiro, Then o time fica completo, o escalado deixa de aparecer em "Eliminados" e **Chamar partida** habilita.
- Given o escalado, When os dois times dele jogam, Then o saldo dele soma as duas participações.
- Given uma partida já chamada, When tento escalar, Then é recusado.
- Given um time de origem `atrasado`, Then a lista é sempre a de escalação (sem o grupo "ainda não jogaram").
- Given dois aparelhos, Then a escolha aparece nos dois sem atualizar.
- Given o servidor reiniciado, Then a escalação continua gravada.

## Testes

- `tests/test_escalacao.py` (puro): exclusões, gênero (H com e sem mulher elegível, M livre), ordem por chegada, grupo "ainda não jogaram" vazio e com jogador livre, saldo somando duas participações, eliminado escalado fora de "eliminados".
- `tests/test_escalar_parceiro.py` (API + placar real): rodada ímpar até o incompleto entrar em quadra; lista; escolher; chamar; jogar; saldo; recusas (não elegível, H+H com alternativa, partida chamada, sem incompleto, origem atrasado); concorrência; migração 5→6.
- Playwright: fluxo ímpar completo na tela (escolher parceiro, chamar, jogar), dois aparelhos, axe.

## Alternativas rejeitadas

- **Deixar H+H como aviso, não bloqueio:** a RN-01 diz que o gênero prevalece.
- **Mover o escalado do time antigo para o novo:** perderia o histórico das duas partidas (e o saldo dobrado do CA5).
- **Escolher o parceiro automaticamente:** a RN-05 pede que o próprio jogador escolha.

## Fora do escopo

Registrar atrasados (US9); substituir quem saiu (US10); desfazer a escolha (a US7 desfaz partidas, não escalações); jogar o mata-mata (US11); sorteio das rodadas seguintes (US4, que passa a usar o saldo daqui).

## Pontos para o Navigator confirmar

1. **O grupo "ainda não jogaram" é sempre vazio na prática** (o incompleto é o último da fila), então a lista é sempre a de escalação. Fica no código para os atrasados e a substituição. Aceita?
2. **H+H com alternativa é recusado** (só aparece se não houver mulher elegível), em vez de apenas desaconselhado.
3. **Ordem da lista por ordem de chegada** dentro do que é permitido.
4. **O eliminado escalado sai de "Eliminados" enquanto joga** pelo segundo time.
5. **O painel passa a mostrar o saldo da rodada** (pontos feitos − sofridos, somando os dois times do escalado).
6. **A coluna `origem` entra agora** para a US9 já encontrar o caminho pronto.

## Riscos

- **Lista vazia:** se não houver ninguém elegível, a rodada fica parada no incompleto (só cancelando). Não deve ocorrer: o incompleto só entra depois de pelo menos uma partida, e o perdedor dela é elegível.
- **Saldo por jogador depende dos placares gravados:** corrigir um placar depois não o recalcula (a US7 desfaz a última partida inteira).
