---
id: time-vazio-e-pular-viram-ajustes-da-fila
status: Decided
raised: 2026-10-08
decided: 2026-10-08
deciders:
  - Eli (Navigator)
  - Claude Sonnet 5.5 (Driver)
related:
  - CV8.DS7.US19
  - CV8.DS7.TS3
---

# Time vazio e "pular" viram ajustes da fila, não edições do estado

## Question

Retirar o último jogador de um time (o time deixa de existir) e pular um time sem elegível mudam a fila. Como gravar isso se a condução (`derivar`) reconstrói quadra, fila e reis a partir do sorteio e dos resultados?

## Decision

Tabela `ajustes_fila` (schema 11, aditiva) com `apos_partidas`, `tipo` (`remover` | `pular`) e `time_id`. `derivar` aplica cada ajuste logo depois da partida de número `apos_partidas` (fila e mata-mata contadas juntas). "Pular" manda o time para o fim da fila (ou do rol de rivais). *Retirar* e *Substituir* (US10) convivem. "Desfazer a última partida" reaponta os ajustes posteriores para a partida anterior.

## Rationale

Apagar a linha do time ou reordenar `fila` só no estado final quebra o replay: os resultados já gravados citam times que "não estavam em quadra". Com o ajuste datado, a história continua batendo e o estado de agora sai da mesma função pura. Sem ajustes, a saída é idêntica à de antes (teste de equivalência).

## Consequences

- Retirar não é reversível por si; o jogador volta como atrasado (US9).
- "Pular" só é oferecido (e só é aceito pela API) quando muda a próxima partida; no rei/campeão do mata-mata não faz efeito.
- Qualquer nova mudança de fila no meio da rodada deve entrar como novo tipo de ajuste, não como edição direta.
