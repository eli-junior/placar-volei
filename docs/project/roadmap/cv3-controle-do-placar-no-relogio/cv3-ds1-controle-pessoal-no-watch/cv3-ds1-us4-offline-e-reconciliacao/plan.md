# Plano — CV3.DS1.US4: revisão de conflito pelo telefone

Branch: `feature/cv3-ds1-us4-revisao-no-telefone` (de `master` `d538f4c`). Versão alvo: **0.24.0** (minor: capacidade nova no telefone, na API e no relógio).

## Ponto de partida

A TS1 (0.19.0) já entrega a fila durável, `base_seq`, o reenvio idempotente e a pausa: um lance recusado vira `held` no relógio, a fila para e o único caminho é **Descartar** no próprio relógio, sem listar os lances. O servidor não sabe que há lances parados.

## Escopo

1. **Relógio informa a pendência.** Ao pausar (`held`), o relógio envia a fila inteira ao servidor: `PUT /api/watch/pendencia` com `{motivo, partida_id, lances[]}`. Idempotente; reenviado a cada reconexão enquanto houver pausa.
2. **Servidor guarda e avisa.** Tabela `watch_pendencias` (uma por dispositivo, substituída a cada envio). O snapshot da sala leva, só para o dono do relógio e para ADMIN, um resumo: quantos lances, motivo, e se a partida ainda é a mesma.
3. **Telefone revisa.** Na sala, faixa "Relógio com N lances parados · Revisar". O painel lista os lances em ordem (`+1 Dupla A`, `↶ desfazer ponto da Dupla B`...), o motivo e duas ações:
   - **Reaplicar**: o servidor aplica os lances na ordem, sobre o placar atual, em nome do relógio (autor = participante do relógio), com a autoridade de quem revisa. Só disponível se a partida é a mesma; desfazer cujo alvo não existe mais é pulado e aparece no resultado.
   - **Descartar**: confirmação que repete a lista dos lances que serão abandonados.
4. **Relógio obedece a decisão.** A resolução vai no estado (`pendencia_resolvida: {id, decisao}`); o relógio limpa a fila e o `held`, e volta a operar. O descarte local no relógio continua existindo.
5. **Revogação.** Token revogado ou expirado não envia pendência (não há como autenticar). O relógio mantém a tela atual: lances retidos com descarte explícito e a mensagem "Vínculo revogado. Estes lances não foram enviados." Nunca descarta sozinho.

## Aceitação (BDD)

- Dado o relógio offline com A, B, A e desfazer na fila, quando outro operador pontua e o relógio reconecta, então a fila pausa, o telefone mostra "3 lances parados" com a lista, e nada foi aplicado.
- Quando o Navigator toca **Reaplicar**, então os lances entram no placar na ordem, uma única vez, em todos os clientes, e o relógio volta a operar sem fila.
- Quando toca **Descartar**, então a confirmação lista os lances abandonados; após confirmar, o placar não muda e o relógio volta a operar sem fila.
- Com nova partida iniciada, **Reaplicar** não aparece; só Descartar.
- Com o vínculo revogado, o relógio não perde os lances em silêncio: mostra-os como não enviados com descarte explícito.
- Reaplicar duas vezes (toque duplo ou reenvio) produz efeito uma vez só.
- Participante sem papel ADMIN (nem dono do relógio) recebe 403 ao forjar reaplicar/descartar.

## Decisões de desenho

- **Revisão no servidor, não por canal direto telefone↔relógio**: telefone e relógio já falam com o servidor; sem Bluetooth/Data Layer novo. Rejeitado: revisão só no relógio (tela pequena, e a regra aprovada pede o telefone).
- **Reaplicar executa no servidor** a partir da lista guardada, em vez de o relógio reenviar com versão forçada: uma transação, sob o lock da quadra, idempotente pelo id da pendência. Rejeitado: "liberar" o relógio a reenviar (duas fontes de verdade e corrida com o operador atual).
- **Quem pode revisar**: o dono do relógio (Eli) ou ADMIN da sala. Reaplicar não exige estar no controle; é uma decisão explícita de quem administra.
- **Autor dos eventos reaplicados**: o participante do relógio, para o histórico mostrar a origem real.

## Fora de escopo

- Envio com o app em segundo plano.
- Edição lance a lance (reaplicar só alguns). Tudo ou nada nesta US.
- Pendência de relógio revogado revisada pelo telefone.

## Riscos / pontos para o Navigator

- **Reaplicar sobre placar que andou** pode passar do fim de set; proposta: aplicar até a vitória e pular o resto, mostrando o que foi pulado.
- Resumo da pendência no snapshot precisa entrar na allowlist pública (CV2.DS1.TS1) só para quem pode revisar.

## Validação

Automatizada: pytest (pendência, reaplicar, descartar, idempotência, 403 forjado, partida trocada); testes da `ScoreSync` com servidor falso; vitest do painel; e2e do painel.

Física: relógio + telefone + terceiro cliente. Modo avião 30 s, marcar A, B, A, desfazer; outro operador pontua; reconectar; revisar no telefone (reaplicar num ciclo, descartar noutro, trocar partida noutro); revogar com fila parada.
