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
- O time incompleto (ímpar) continua por último (RN-05); fica como pendência na US24.

## Alternativas rejeitadas

- **O membro mais descansado decide** (como a chegada na RN-13): um jogador descansado puxaria para a frente o parceiro que acabou de jogar.
- **O membro que jogou por último decide:** pune o parceiro descansado.
- **Formar as duplas pelo descanso:** brigaria com o equilíbrio pela nota e com a RN-01.
- **Ordenar por `encerrada_em`:** a numeração da rodada e da partida é sequencial e não depende do relógio.

## Consequências

`app/reequilibrio.py` (`ultima_partida`) calcula o descanso; `app/sorteio.py` (`sortear(..., descanso=...)`) o usa só no `sorted` da fila. Sem schema novo: o descanso usado não fica gravado na rodada.
