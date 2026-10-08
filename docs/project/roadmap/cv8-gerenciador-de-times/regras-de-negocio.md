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

**RN-04 — Mata-mata.** O vencedor da última partida enfrenta os reis em ordem cronológica de coroação, começando pelo primeiro. Quem vence segue contra o próximo rei; o último vencedor é o campeão. Sem reis, o vencedor da última partida da fila é o campeão direto. Após o início do mata-mata, nenhum jogador/time entra mais. **Fixado na US11 (Navigator, 2026-10-07):** o início é **manual** (o operador confirma); cada confronto é **partida única** (ganhou ficou, perdeu saiu, sem a regra das 2 vitórias); se a quadra esvaziou porque o último vencedor virou rei com a fila vazia, **esse time é o desafiante** e enfrenta os demais reis na ordem de coroação (sem outros reis, é o campeão direto); ao fim, a rodada se encerra com o campeão registrado e o sorteio seguinte é liberado.

**RN-05 — Jogador ímpar.** No sorteio ímpar, o jogador sem par — **o último a chegar** (Navigator, 2026-10-07) — forma um time incompleto por último na fila. Na sua vez, escolhe parceiro entre quem ainda não jogou na rodada; se não houver ninguém, usa a lista de escalação (RN-07). *Na prática o primeiro grupo é sempre vazio:* o incompleto é o último da fila, então todos à frente dele já jogaram quando chega a vez dele (Navigator, 2026-10-07); a lista de escalação é a que vale.

**RN-06 — Atrasados no meio da rodada.** Cada atrasado é registrado sozinho, como time incompleto, no fim da fila. Escolhe parceiro só na sua vez, pela lista de escalação (RN-07). Dois atrasados nunca formam dupla entre si. Bloqueado após início do mata-mata → entra só na próxima rodada.

**RN-07 — Lista de escalação.** Calculada no momento da vez do time incompleto. Elegíveis: jogadores eliminados da rodada. Excluídos: quem está em quadra; membros de reis aguardando mata-mata; outros times incompletos/atrasados. Ordenação/destaque respeitando RN-01 (opções que evitam H+H primeiro; H+H só se não houver alternativa). O escalado joga por um segundo time; as duas partidas contam no saldo dele. **Regras fixadas na US8:** o incompleto **homem** só vê as mulheres elegíveis e o homem só aparece se não houver nenhuma (o servidor recusa H+H havendo alternativa); a lista segue a **ordem de chegada**; o escalado **sai de "Eliminados" enquanto joga** pelo segundo time e volta se esse time também perder; a escolha só vale com o incompleto em quadra e antes de chamar a partida; a nota e a chegada gravadas são as do sorteio.

**RN-08 — Substituição por saída no meio da rodada.** Se um jogador de time ativo sai, o substituto é (1) o jogador ímpar (time incompleto aguardando) ou (2) alguém da lista de escalação, respeitando RN-01. O time mantém vitórias e posição.

**RN-09 — Placar por partida.** Alvo 10 ou 12 pontos, definido por rodada no sorteio. Vantagem de 2, set único. Ao chamar a partida, o placar ao vivo é carregado automaticamente com as duplas. Encerramento manual (operador confirma): só se encerra uma partida que **terminou pelas regras do placar** (alvo com vantagem de 2); o gerenciador lê o placar final da quadra vinculada e grava o resultado, sem encerramento antecipado. Só é possível desfazer a última partida encerrada.

**RN-10 — Reequilíbrio entre rodadas.** Ranking individual por saldo acumulado na sessão (na primeira rodada, pela nota — RN-14). Pareamento em serpentina (1º com último, 2º com penúltimo...). Prioridade: RN-01 > evitar repetir duplas da sessão (preferência) > serpentina pura.

**RN-11 — Rodada mínima.** Mínimo de 4 jogadores presentes para sortear.

**RN-12 — Operação.** Qualquer aparelho que **conheça o segredo do dono** pode operar o gerenciador, e todos os aparelhos abertos na tela da sessão veem as mudanças sozinhos (WebSocket `/ws/gerenciador`, segredo na primeira mensagem).

**RN-13 — Ordem de chegada (todas as rodadas da sessão; Navigator, 2026-10-07, US4).** Os times são ordenados na fila pela **menor ordem de chegada entre seus jogadores**. Assim, os times de quem chegou em 1º e em 2º jogam a primeira partida; se os dois estiverem no mesmo time, entra o time de quem chegou em 3º, e assim por diante. Objetivo: incentivar a chegada no horário. Da segunda rodada em diante vale a regra normal da fila (US-04). O jogador ímpar (RN-05) **continua por último** na fila mesmo que tenha chegado cedo (Navigator, 2026-10-07).

**RN-15 — Fila de chegada editável.** Ao ser registrado como presente, o jogador entra automaticamente **no fim** da ordem de chegada (inclusive ao desmarcar e marcar de novo). O operador pode **reordenar** a fila de chegada manualmente a qualquer momento antes do sorteio da primeira rodada. **Com rodada em proposta ou em andamento, a presença fica travada** (marcar, desmarcar, reordenar, cadastro rápido); descartar a proposta ou cancelar a rodada a destrava. Inativar um jogador que está na rodada é recusado.

**RN-14 — Nota e sorteio equilibrado.** A nota (1 a 100, padrão 60) substitui o sorteio aleatório puro na primeira rodada: as duplas saem **equilibradas pela nota** (serpentina, como na RN-10), sem aleatoriedade, respeitando a RN-01 (gênero prevalece sobre a nota). **Resortear** percorre outras combinações igualmente equilibradas — amplitude (maior soma − menor soma) até 3 pontos pior que a melhor — e volta ao início ao esgotá-las; o sorteio é determinístico e reproduzível. **Decidido (Navigator, 2026-10-07):** o saldo da sessão **ajusta a nota** nas rodadas seguintes. **Fórmula (decidida pelo Driver por delegação do Navigator, 2026-10-07; ajustável):** `nota_efetiva = clamp(nota_base + clamp(round(2 × saldo ÷ partidas_jogadas), −15, +15), 1, 100)`. O saldo é por partida (não cresce só por jogar mais) e o ajuste é limitado a ±15, para a nota cadastrada continuar mandando. **Vale só na sessão:** a `nota_base` da base de jogadores não muda; o operador a edita quando quiser. Sem partidas jogadas, `nota_efetiva = nota_base`.

**RN-16 — Formato trio (US15; Navigator, 2026-10-08).** A rodada é de duplas **ou** de trios, escolhido no sorteio e gravado na rodada (`formato`). No trio: mínimo de 6 presentes; a sobra (`N mod 3`) forma um time incompleto por último na fila — 1 jogador escolhe 2 parceiros, 2 jogadores escolhem 1 — pela lista de escalação (RN-07), um por vez, e o time só joga completo. Com homens e mulheres presentes, **nenhum trio fecha só de um sexo** (o gênero prevalece sobre a nota); se faltar um dos sexos para isso, o sorteio minimiza os trios de um sexo, e a escalação só os aceita sem alternativa. Se todos são do mesmo sexo, a regra não se aplica. Placar, fila, rei da quadra, mata-mata, desfazer, substituição e atrasado seguem iguais.
