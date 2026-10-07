# CV8 — Glossário e regras de negócio

Escopo do MVP: Web + nomes das duplas no relógio; somente formato dupla.

## Glossário

| Termo | Definição |
|---|---|
| **Sessão** | Um dia de jogo. Agrupa rodadas. |
| **Rodada** | Ciclo sorteio → partidas da fila → mata-mata → campeão. |
| **Time** | Entidade de 1 ou 2 jogadores dentro de uma rodada. Vitórias pertencem ao time, não ao jogador. |
| **Fila** | Ordem de entrada dos times ainda não estreados na rodada. |
| **Rei** | Time que completou 2 vitórias seguidas na rodada. |
| **Eliminado** | Jogador cujo time perdeu uma partida na rodada. |
| **Time incompleto** | Time de 1 jogador (ímpar ou atrasado) que escolhe o parceiro na sua vez. |
| **Mata-mata** | Fase final da rodada entre o vencedor da última partida da fila e os reis. |
| **Nota** | Nível do jogador, de 1 (mais iniciante) a 100 (mais profissional). Padrão 60 quando não informada. |
| **Ordem de chegada** | Ordem em que a presença do jogador foi marcada na sessão. |
| **Saldo** | Pontos feitos − pontos sofridos pelo(s) time(s) em que o jogador atuou. |

## Regras

**RN-01 — Composição de gênero.** Preferência: evitar dupla H+H; só ocorre H+H se houver mais homens que mulheres (apenas no excedente). M+M permitido sem restrição. Em conflito com equilíbrio de saldo ou repetição de dupla, gênero prevalece.

**RN-02 — Fluxo da rodada (rei da quadra).** Os 2 primeiros times da fila jogam (na primeira rodada da sessão, a fila segue a RN-13). O perdedor sai da rodada (jogadores viram eliminados). O vencedor permanece e enfrenta o próximo da fila. Com 2 vitórias seguidas o time vira rei, sai da quadra e aguarda o mata-mata; os 2 próximos da fila entram. Reis não voltam à fila. Se um time ficar sozinho na quadra sem adversário na fila, a fase de fila termina.

**RN-03 — Fechamento da fila.** Termina quando a fila esvazia. O vencedor da última partida da fila (entrante ou quem estava na quadra) vai ao mata-mata.

**RN-04 — Mata-mata.** O vencedor da última partida enfrenta os reis em ordem cronológica de coroação, começando pelo primeiro. Quem vence segue contra o próximo rei; o último vencedor é o campeão. Sem reis, o vencedor da última partida da fila é o campeão direto. Após o início do mata-mata, nenhum jogador/time entra mais.

**RN-05 — Jogador ímpar.** No sorteio ímpar, o jogador sem par forma um time incompleto por último na fila. Na sua vez, escolhe parceiro entre quem ainda não jogou na rodada; se não houver ninguém, usa a lista de escalação (RN-07).

**RN-06 — Atrasados no meio da rodada.** Cada atrasado é registrado sozinho, como time incompleto, no fim da fila. Escolhe parceiro só na sua vez, pela lista de escalação (RN-07). Dois atrasados nunca formam dupla entre si. Bloqueado após início do mata-mata → entra só na próxima rodada.

**RN-07 — Lista de escalação.** Calculada no momento da vez do time incompleto. Elegíveis: jogadores eliminados da rodada. Excluídos: quem está em quadra; membros de reis aguardando mata-mata; outros times incompletos/atrasados. Ordenação/destaque respeitando RN-01 (opções que evitam H+H primeiro; H+H só se não houver alternativa). O escalado joga por um segundo time; as duas partidas contam no saldo dele.

**RN-08 — Substituição por saída no meio da rodada.** Se um jogador de time ativo sai, o substituto é (1) o jogador ímpar (time incompleto aguardando) ou (2) alguém da lista de escalação, respeitando RN-01. O time mantém vitórias e posição.

**RN-09 — Placar por partida.** Alvo 10 ou 12 pontos, definido por rodada no sorteio. Vantagem de 2, set único. Ao chamar a partida, o placar ao vivo é carregado automaticamente com as duplas. Encerramento manual (operador confirma). Só é possível desfazer a última partida encerrada.

**RN-10 — Reequilíbrio entre rodadas.** Ranking individual por saldo acumulado na sessão (na primeira rodada, pela nota — RN-14). Pareamento em serpentina (1º com último, 2º com penúltimo...). Prioridade: RN-01 > evitar repetir duplas da sessão (preferência) > serpentina pura.

**RN-11 — Rodada mínima.** Mínimo de 4 jogadores presentes para sortear.

**RN-12 — Operação.** Qualquer dispositivo conectado pode operar (sincronia via WebSocket, igual ao placar atual).

**RN-13 — Ordem de chegada (só na primeira rodada da sessão).** Os times são ordenados na fila pela **menor ordem de chegada entre seus jogadores**. Assim, os times de quem chegou em 1º e em 2º jogam a primeira partida; se os dois estiverem no mesmo time, entra o time de quem chegou em 3º, e assim por diante. Objetivo: incentivar a chegada no horário. Da segunda rodada em diante vale a regra normal da fila (US-04). *Em aberto:* o jogador ímpar (RN-05) continua por último na fila mesmo que tenha chegado cedo?

**RN-14 — Nota e sorteio equilibrado.** A nota (1 a 100, padrão 60) substitui o sorteio aleatório puro na primeira rodada: as duplas saem **equilibradas pela nota** (serpentina, como na RN-10), sem aleatoriedade, respeitando a RN-01 (gênero prevalece sobre a nota). *Em aberto:* o saldo da sessão ajusta a nota, ou nota e saldo ficam separados nas rodadas seguintes?
