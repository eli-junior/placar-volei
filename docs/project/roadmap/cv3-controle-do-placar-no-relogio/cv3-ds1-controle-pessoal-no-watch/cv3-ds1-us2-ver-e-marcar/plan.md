# Plano — CV3.DS1.US2 Ver o placar e marcar pontos no pulso

Branch: `feature/cv3-ds1-us2-ver-e-marcar`, criada da `master` em `bc32dec` (0.7.0).
Estado: Checkpoint 1 — aguardando o Navigator.

## Nível
User Story. Visível no relógio e nas telas web (o ponto marcado no pulso aparece para todos).

## Escopo

### Servidor
1. **Comando do relógio com recibo durável.** Nova rota `POST /api/watch/comandos`, autenticada por Bearer do dispositivo. Corpo: `id` (UUID gerado no relógio), `partida_id`, `controle_versao` e `equipe` (`A`/`B`).
2. **Tabela `watch_comandos`** (aditiva, `CREATE TABLE IF NOT EXISTS`): `device_id`, `comando_id`, `partida_id`, `acao`, `equipe`, `controle_versao`, `status` (`APLICADO`/`RECUSADO`), `detalhe`, `evento_seq`, `criado_em`. Chave primária `(device_id, comando_id)`. O recibo é gravado **na mesma transação** do evento.
3. **Idempotência:**
   - reenvio com o mesmo `id` e o mesmo conteúdo devolve o recibo original e o estado atual, sem novo evento;
   - o mesmo `id` com conteúdo diferente devolve 409 e não aplica nada;
   - recusas de negócio também geram recibo. Um reenvio recebe a mesma resposta, mesmo que o estado tenha mudado depois.
4. **Base do comando:** o comando só vale para a `partida_id` e a `controle_versao` que o relógio via ao tocar. Uma partida nova ou uma troca de controle geram recusa registrada. Um comando antigo nunca é aplicado a outra partida.
5. **Reuso da regra existente:** `executar_sync` passa a aceitar o autor por `participante_id`, além da sessão do navegador. Autorização, encerramento, `PARTIDA_ENCERRADA` e o broadcast `PLACAR_ATUALIZADO` são os mesmos do site. Não haverá um segundo caminho de pontuação.

### Relógio (Wear OS)
6. **Tela de placar**, depois do vínculo: duas metades grandes, uma por equipe (A à esquerda, B à direita). Cada metade mostra letra, nome curto, pontos e cor. A cor nunca é o único identificador. Tocar em qualquer lugar da metade marca o ponto.
7. **Fila durável:** o toque grava o comando em disco (`commit()`) **antes** do retorno visual. Depois vêm uma vibração curta e o placar previsto.
8. **Previsto vs. confirmado:** placar exibido = estado confirmado + comandos pendentes da mesma partida. Enquanto houver pendência, os números previstos aparecem com um marcador distinto e com a contagem "N pendentes". Sem pendências, o placar é o confirmado do servidor.
9. **Envio em ordem:** um único remetente FIFO, com uma requisição em voo por vez. Toques rápidos não são descartados nem agrupados. Em falha de rede, repete com espera crescente e mantém a fila.
10. **Estado em tempo real:** o relógio passa a ler `ESTADO_INICIAL` e `PLACAR_ATUALIZADO` do WebSocket que já usa para presença. Ao voltar ao app, consulta `/api/watch/state`.
11. **Encerramento:** os botões ficam bloqueados quando a partida confirmada está encerrada. Também ficam bloqueados quando o placar previsto já atinge a vitória: a regra `avaliar_vitoria` (alvo, vantagem, teto) é portada para Kotlin, e o servidor continua sendo a autoridade.
12. **Recusa:** a primeira recusa pausa a fila e mantém os comandos seguintes. O relógio mostra o motivo ("Partida encerrada", "Outro operador no controle", "Nova partida") e a ação **Descartar N lances**, com confirmação. Nada é descartado sem o Navigator ver. A revisão pelo telefone fica para a US4.
13. **Indicador de conexão:** "Conectado", "Sem conexão" ou "Reconectando".
14. **Tela apagada / modo ambiente:** o app não entra em modo ambiente. Com a tela apagada, a atividade pausa e nenhum toque é registrado. Ao voltar, recarrega o estado e a fila persistida.

## Aceitação (BDD)
- **Dado** relógio vinculado, partida ativa e eli no controle, **quando** tocar em A, A, B, **então** o relógio mostra 2×1 imediatamente como previsto, o espectador vê 2×1, o histórico tem três pontos e cada comando tem um recibo `APLICADO`.
- **Dado** um comando enviado cuja resposta se perdeu, **quando** o relógio reenviar o mesmo `id`, **então** o servidor devolve o recibo original e não cria um segundo evento.
- **Dado** o mesmo `id` com equipe diferente, **então** 409 e nenhum evento.
- **Dado** 5 toques rápidos, **então** o servidor registra 5 pontos, na ordem tocada.
- **Dado** o telefone bloqueado e o navegador em segundo plano, **quando** tocar no relógio, **então** o ponto é aplicado pela rede do relógio.
- **Dada** a partida encerrada confirmada, **então** os botões ficam indisponíveis. Um comando que chegue mesmo assim é recusado com recibo, e a fila pausa com o motivo visível.
- **Dada** uma partida nova iniciada no telefone com comandos pendentes da anterior, **então** esses comandos são recusados, não aplicados à nova partida, e aparecem para descarte explícito.
- **Dado** o app reaberto ou a tela reacendida, **então** o placar e a fila pendente reaparecem, sem toque registrado enquanto a tela estava apagada.

## Decisões de desenho
- **Rota própria do relógio + recibo, sem reaproveitar `/pontos` com Bearer.** Motivo: o recibo idempotente é exigência da DS (base para US3/US4). Colocá-lo na rota do site mudaria o contrato web sem necessidade. A regra de pontuação continua única (`executar_sync`).
- **Recusas registradas como recibo.** Assim o resultado de um `id` é determinístico: um reenvio depois de um desfazer que reabra a partida não aplica um ponto que já tinha sido recusado.
- **Evento `PONTO_MARCADO` inalterado.** O vínculo com o comando fica no recibo (`evento_seq`), sem risco para a projeção nem para a linha do tempo.
- **Previsão de vitória no relógio.** Evita que o toque depois do ponto de vitória vire uma recusa previsível. O custo é duplicar ~15 linhas de regra, cobertas por teste em Kotlin espelhando os casos do Python.
- **Fila em arquivo JSON com escrita atômica**, sem Room. A fila é curta e de um só usuário, e o Room traria dependência e código gerado desproporcionais. Pode ser reavaliado na US4.
- **Envio só com o app em primeiro plano.** O envio em segundo plano (WorkManager) e a reconciliação ficam para a US4. A US2 não promete operação offline completa.

Alternativas rejeitadas: desativar o botão até a confirmação (piora o jogo com latência de Bluetooth); agrupar toques rápidos (perde ordem e auditoria); aplicar a fila na partida atual depois de uma recusa (proibido pela DS).

## Fora de escopo
Desfazer (US3). Envio em segundo plano, revisão de conflito pelo telefone e reconciliação offline (US4). Inversão de lados no relógio, tiles, complicações e tela sempre ligada. Assumir o controle pelo relógio. Qualquer mudança no site.

## Versão
`0.8.0` (minor: nova capacidade de pontuar pelo pulso). Atenção: o servidor apaga o banco quando a versão muda. O deploy deve ser feito fora de uma partida, como na 0.7.0.

## Validação prevista
- `uv run pytest` com testes novos: aplicação, reenvio idempotente, `id` com conteúdo divergente, reenvio concorrente, ordem A/A/B, partida trocada, controle trocado, partida encerrada, dispositivo revogado, broadcast para o navegador.
- `ruff check`/`format --check`, `npm test`/`check`/`build` (sem mudança esperada no site).
- Android: testes da fila (persistência, ordem, remoção por recibo), da previsão e de `avaliar_vitoria`; `assembleDebug` e `lintDebug`.
- Roteiro físico (test-guide, no Passo 4): Watch + telefone admin + navegador espectador; A/A/B; toques rápidos; telefone bloqueado; luz externa; animações reduzidas; apagar e reacender a tela; encerrar a partida; nova partida com fila pendente (modo avião no relógio).

## Riscos e pontos para o Navigator
1. **Descarte no próprio relógio** (item 12): proposta para a US2 não travar sem saída. A decisão aprovada de revisar conflitos no telefone é mantida para a US4. Confirmar.
2. **Deploy apaga salas** ao subir a 0.8.0 (comportamento existente, dívida `banco-de-producao-sem-volume-persistente`).
3. Tamanho da tela do Watch 8 ainda não informado (40 ou 44 mm). O layout usará proporções da tela, mas a ergonomia só fecha no teste físico.
4. O snapshot do WebSocket inclui a linha do tempo inteira. Para uma partida de vôlei isso é pequeno, mas o relógio vai ignorar esse campo.
