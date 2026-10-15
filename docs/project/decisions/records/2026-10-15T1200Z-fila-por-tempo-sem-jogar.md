---
status: Accepted
date: 2026-10-15
related:
  - CV8.DS2.US23
  - CV8.DS2.US24
---

# Fila das rodadas seguintes por tempo sem jogar

## Contexto

A fila de toda rodada seguia só a ordem de chegada (RN-13). Um time que abria uma rodada podia fechá-la na seguinte e ficar tempo demais parado; a reclamação veio dos jogadores.

## Decisão (Navigator, 2026-10-15)

- **Duas etapas, nessa ordem.** Primeiro o sorteio forma as duplas (ou trios) como sempre: gênero (RN-01, RN-16), equilíbrio pela nota atual em serpentina, evitar repetir dupla (RN-10). Só depois, com os times prontos, a fila é ordenada. O descanso **nunca** muda a combinação.
- **Descanso do jogador:** o número (1, 2, 3… em ordem cronológica) da última partida encerrada que ele jogou na sessão; quem ainda não jogou vale 0.
- **Ordem da fila:** primeiro o time com a menor **média** do descanso dos seus jogadores (há mais tempo esperando); a menor ordem de chegada desempata (RN-13). Na 1ª rodada todos valem 0 e vale só a chegada.
- **Rodada cancelada conta:** suas partidas encerradas entram no descanso (o cansaço é físico), ao contrário das duplas anteriores e da nota.
- **Quem jogou cada partida** vem de `ajustes_nota` (gravado no encerramento); sem esse registro (notas resetadas), dos times da partida.
- O time incompleto (ímpar) continua por último (RN-05).

## Ímpar (US24; Navigator, 2026-10-15)

- O ímpar (ou a sobra do trio) é escolhido **antes** de formar os times, entre os que não aumentam o número de duplas H+H (ou de trios de um sexo só): o gênero prevalece, em todas as rodadas. Entre eles, **quem jogou por último**; no empate, **o último a chegar**. Na 1ª rodada vale só a chegada, com o mesmo filtro de gênero.
- O time incompleto fica **sempre no fim da fila**: quem jogou por último é quem pode esperar mais, e o ímpar deixa de ser sempre a mesma pessoa.
- Rejeitadas: o mais descansado de ímpar (entraria cedo, sem eliminados para ser parceiro); o incompleto na fila pela ordem de descanso (o Navigator preferiu sempre no fim); não repetir o ímpar na sessão; o descanso prevalecer sobre o gênero (uma dupla H+H a mais).

## Alternativas rejeitadas

- **O membro mais descansado decide** (como a chegada na RN-13): um jogador descansado puxaria para a frente o parceiro que acabou de jogar.
- **O membro que jogou por último decide:** pune o parceiro descansado.
- **Formar as duplas pelo descanso:** brigaria com o equilíbrio pela nota e com a RN-01.
- **Ordenar por `encerrada_em`:** a numeração da rodada e da partida é sequencial e não depende do relógio.

## Consequências

`app/reequilibrio.py` (`ultima_partida`) calcula o descanso; `app/sorteio.py` (`sortear(..., descanso=...)`) o usa no `sorted` da fila e na escolha do ímpar (`_sobra`, com `_violacoes_genero`). Sem schema novo: o descanso usado não fica gravado na rodada.
