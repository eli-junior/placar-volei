# Plano — CV3.DS2.US3: nova partida rápida pelo relógio

Branch: `feature/cv3-ds2-us3-nova-partida-rapida-no-relogio`, criada da `master` em `ab2cedb` (0.11.0). Versão alvo: `0.12.0` (minor, nova capacidade).

## Direção do Navigator (2026-09-26)

Na pontuação final, um botão ao lado do desfazer começa uma nova partida nos mesmos moldes da atual, com um único toque.

## Escopo

1. **Servidor**: `POST /api/watch/comandos` aceita `acao: "nova_partida"`, com `partida_id` da partida encerrada. Reusa o `reiniciar` do site, sem parâmetros: mesmos times, jogadores, alvo, vantagem e teto.
2. **Permissão**: o `reiniciar` do site exige ADMIN, e o participante do relógio é ESPECTADOR com o controle delegado. O relógio pode começar a nova partida se estiver com o controle **e** o dono dele for ADMIN da quadra. O evento fica em nome do relógio (`Eli (Relógio)`) na linha do tempo.
3. **Idempotência**: o comando tem `id` e passa pelo `watch_recibos`, como ponto e desfazer. Um reenvio não cria uma terceira partida. Se o `partida_id` não é mais o atual, a partida nova já começou: recusa sem efeito.
4. **Relógio**: com a partida encerrada e o controle, a faixa inferior se divide em **↶ Desfazer** | **▶ Nova**. Um toque, sem confirmação, com vibração. O botão só fica ativo com conexão e com a fila vazia: a partida nova não entra na fila offline, porque os pontos seguintes dependeriam de um `partida_id` que ainda não existe.
5. Quando o snapshot da partida nova chega, o placar volta a 0 × 0 e a faixa volta a ser só **↶ Desfazer**.

## Aceite

- Dado o placar encerrado no relógio com o controle, quando toco em **▶ Nova**, então o relógio e o site mostram 0 × 0, com os mesmos times e a mesma regra, e posso marcar o primeiro ponto.
- E **↶ Desfazer** continua ao lado, desfazendo o ponto final como hoje, enquanto a nova partida não começa.
- Dado o relógio sem rede ou com lances pendentes, então **▶ Nova** aparece desativado.
- Dado que o dono do relógio não é ADMIN, então **▶ Nova** não aparece.
- Um toque duplo, ou um reenvio após falha de rede, cria uma única partida nova.

## Decisões

- Reusar o `reiniciar` do servidor, e não criar uma regra nova de "mesmos moldes": o site já faz exatamente isso.
- Envio direto, e não pela fila durável: evita pontos presos a uma partida que ainda não existe.
- Rejeitado: pedir confirmação. O Navigator pediu um único toque, e o **↶ Desfazer** continua disponível até a partida nova começar.

## Fora do escopo

Mudar times ou regras pelo relógio; começar nova partida com a partida em andamento; corrigir a entrada pela Home (`debt-erro-de-entrada-pela-home-fora-da-vista`).

## Riscos

- O snapshot do relógio precisa dizer se o dono é ADMIN. Se ainda não disser, entra um campo novo (`pode_nova_partida`) no estado do relógio.
- Faixa dividida no relógio redondo: cada metade fica menor. Validar o alvo de toque no Watch 8.
