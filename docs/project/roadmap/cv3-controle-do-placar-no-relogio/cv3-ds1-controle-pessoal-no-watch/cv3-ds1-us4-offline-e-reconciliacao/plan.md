# Plano — CV3.DS1.US4: conflito da fila offline converge para o servidor

Branch: `feature/cv3-ds1-us4-revisao-no-telefone` (de `master` `d538f4c`). Versão alvo: **0.24.0**.

## Decisão do Navigator (2026-09-28)

A revisão pelo telefone foi abandonada. Na primeira versão deste plano, o conflito pausava a fila e o telefone escolhia entre reaplicar e descartar. O Navigator escolheu a **opção simples**: se o controle saiu do relógio enquanto ele estava offline, não há conflito a revisar. A fila é descartada, o relógio mostra o placar atual e avisa em um aviso de 3 s. A mesma regra vale para partida nova, placar mudado por fora e vínculo encerrado.

## Escopo (só relógio)

- `ScoreSync.discard(motivo)`: tira a fila inteira e deixa o aviso `N lances não enviados · motivo`, que não é gravado.
- **Snapshot com controle de outro participante** e fila não vazia: descarta com `controle com <apelido>`, ou `controle no telefone` se o apelido não for encontrado.
- **Recusa definitiva** (recibo `RECUSADO` ou 4xx sem recibo): descarta com `nova partida` ou `placar mudou`. As recusas passageiras (408/425/429) continuam segurando o lance na fila.
- **401**: descarta, e a tela de vínculo indisponível acrescenta "N lances não enviados."
- Fila pausada (`retido`) gravada por versão anterior: é descartada ao abrir, com o aviso.
- A tela de lances retidos com **Descartar**/**Confirmar descarte** sai. Em seu lugar entra o aviso, que some em 3 s ou ao toque e é anunciado ao leitor de tela.

O servidor não muda. A regra da 0.19.0 continua valendo: o controle devolvido ao relógio, sem lances de outros no meio, aceita a fila. Se outros marcaram no meio tempo, a versão estrita recusa e o relógio descarta.

## Aceitação

- Relógio offline com A, B, desfazer na fila; o admin passa o controle para Ana; ao reconectar, o relógio mostra por 3 s "3 lances não enviados · controle com Ana" e depois o placar do servidor, sem nenhum lance aplicado.
- Com partida nova, o aviso diz "nova partida" e nada entra na nova partida.
- Com o vínculo revogado, a tela de vínculo diz quantos lances não foram enviados.
- Sem conflito, a fila continua sendo entregue uma vez só (TS1).

## Fora de escopo

Revisão pelo telefone, reaplicação parcial e envio em segundo plano.
