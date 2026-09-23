# Plano — CV3.DS1.US2 Ver o placar e marcar pontos no pulso

Branch: `feature/cv3-ds1-us2-ver-e-marcar`, criada da `master` em `bc32dec` (0.7.0).
Estado: Checkpoint 1 — revisão 2, com os pedidos do Navigator de 2026-09-23 (ícone do relógio, chave "Controlar pelo Relógio", Nós/Eles e iniciais).

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
5. **Chave "Controlar pelo Relógio" da sala.** Nova coluna aditiva `quadras.controle_relogio` (0/1), exposta na allowlist pública. Nova ação `modo-relogio` (`POST /api/quadras/{id}/controle/relogio`, corpo `{ativo}`):
   - **ligar** exige participante habilitado com relógio vinculado e ativo;
   - **desligar** pode ser feito pelo dono do relógio ou por qualquer ADMIN, para recuperar a partida se o relógio ficar sem bateria;
   - toda mudança incrementa `controle_versao`, então comandos enfileirados sob o modo anterior são recusados em vez de aplicados;
   - toda mudança grava o evento `CONTROLE_RELOGIO_ALTERADO`, que aparece na linha do tempo ("Placar passou a ser controlado pelo relógio de eli" / "…voltou para o telefone");
   - revogar o relógio, desabilitar o acesso ou vincular outro relógio desliga a chave automaticamente.
6. **Com a chave ligada, o site não pontua.** `pontos` e `desfazer` vindos de sessão do navegador passam a ser recusados **no servidor** (409, "O placar está sendo controlado pelo relógio."). Reiniciar, configurar e gerir papéis continuam permitidos. Só o relógio pontua, e ele não depende de quem tem o `controle_id` do site. A base do comando continua sendo `partida_id` + `controle_versao`.
7. **Com a chave desligada, o relógio só mostra o placar.** O comando é recusado ("O controle está no telefone"), e o relógio desabilita os botões e mostra "Ative Controlar pelo Relógio no telefone".
8. **Reuso da regra existente:** `executar_sync` passa a aceitar o autor por `participante_id`, além da sessão do navegador. Autorização, encerramento, `PARTIDA_ENCERRADA` e o broadcast `PLACAR_ATUALIZADO` são os mesmos do site. Não haverá um segundo caminho de pontuação.

### Site
9. **Ícone de relógio** no cabeçalho, no lugar do texto "Relógio" (ícone `relogio`, traçado Lucide `watch`, no conjunto embutido de `icones.js`). Mantém o rótulo acessível.
10. **Filtro por nome:** ao tocar no ícone, se o apelido público não for `eli` (sem diferenciar maiúsculas nem espaços nas pontas: `Eli`, `ELI`, `eli`), aparece um aviso curto "Em breve…" em vez do modal. É só uma porta de interface: a permissão real continua sendo a habilitação no servidor (`watch_grants`).
11. **Chave "Controlar pelo Relógio"** nas configurações da sala (`ModalConfigurarPartida`), visível apenas quando o participante tem relógio vinculado (ou, para ADMIN, quando a chave está ligada, para poder desligar). Ligar/desligar atualiza todas as telas pelo broadcast.
12. **Placar somente leitura com a chave ligada:** os botões de ponto e desfazer somem para todos, e o placar mostra "Controlado pelo relógio de eli". A engrenagem de configurações continua disponível para quem já podia usá-la.

### Relógio (Wear OS)
13. **Tela de placar**, depois do vínculo: duas metades grandes, uma por equipe. Tocar em qualquer lugar da metade marca o ponto. A cor nunca é o único identificador.
    - **Rótulos "Nós" e "Eles"** no lugar de Equipe A / Equipe B: Nós = equipe A, à esquerda; Eles = equipe B, à direita.
    - **Com nomes personalizados, as iniciais**: com jogadores cadastrados, a primeira letra de cada jogador ("Eli Junior" + "Camila" → **EC**; "Rafa" + "Marvin" → **RM**); com só o nome da equipe, as iniciais das duas primeiras palavras ou, se for uma palavra, as duas primeiras letras. Se as iniciais das duas equipes ficarem iguais, volta a Nós/Eles.
    - O cálculo dos rótulos é função pura em Kotlin, com teste.
14. **Fila durável:** o toque grava o comando em disco (`commit()`) **antes** do retorno visual. Depois vêm uma vibração curta e o placar previsto.
15. **Previsto vs. confirmado:** placar exibido = estado confirmado + comandos pendentes da mesma partida. Enquanto houver pendência, os números previstos aparecem com um marcador distinto e com a contagem "N pendentes". Sem pendências, o placar é o confirmado do servidor.
16. **Envio em ordem:** um único remetente FIFO, com uma requisição em voo por vez. Toques rápidos não são descartados nem agrupados. Em falha de rede, repete com espera crescente e mantém a fila.
17. **Estado em tempo real:** o relógio passa a ler `ESTADO_INICIAL` e `PLACAR_ATUALIZADO` do WebSocket que já usa para presença. Ao voltar ao app, consulta `/api/watch/state`.
18. **Encerramento:** os botões ficam bloqueados quando a partida confirmada está encerrada. Também ficam bloqueados quando o placar previsto já atinge a vitória: a regra `avaliar_vitoria` (alvo, vantagem, teto) é portada para Kotlin, e o servidor continua sendo a autoridade.
19. **Recusa:** a primeira recusa pausa a fila e mantém os comandos seguintes. O relógio mostra o motivo ("Partida encerrada", "Outro operador no controle", "Nova partida") e a ação **Descartar N lances**, com confirmação. Nada é descartado sem o Navigator ver. A revisão pelo telefone fica para a US4.
20. **Indicador de conexão:** "Conectado", "Sem conexão" ou "Reconectando".
21. **Tela apagada / modo ambiente:** o app não entra em modo ambiente. Com a tela apagada, a atividade pausa e nenhum toque é registrado. Ao voltar, recarrega o estado e a fila persistida.

## Aceitação (BDD)
- **Dado** um participante com apelido `Rafa`, **quando** tocar no ícone do relógio, **então** vê "Em breve…" e nenhum modal de vínculo. Com `eli`, `Eli` ou `ELI` (inclusive vindo de `eli.relogio`), abre o modal.
- **Dado** o relógio vinculado, **quando** eli ligar "Controlar pelo Relógio", **então** todas as telas do site perdem os botões de ponto e desfazer, e mostram "Controlado pelo relógio de eli". As configurações continuam editáveis pelo ADMIN. Um `POST /pontos` forjado pelo navegador recebe 409.
- **Dada** a chave desligada, **então** o relógio mostra o placar com os botões indisponíveis e a orientação para ativar no telefone.
- **Dada** a chave ligada com lances pendentes no relógio, **quando** um ADMIN desligar a chave, **então** os lances pendentes são recusados (versão de controle mudou) e aparecem para descarte, sem entrar no placar.
- **Dada** a partida "Eli Junior / Camila" × "Rafa / Marvin", **então** o relógio mostra EC e RM. Com nomes padrão, mostra Nós e Eles.
- **Dado** relógio vinculado, partida ativa e "Controlar pelo Relógio" ligado, **quando** tocar em A, A, B, **então** o relógio mostra 2×1 imediatamente como previsto, o espectador vê 2×1, o histórico tem três pontos e cada comando tem um recibo `APLICADO`.
- **Dado** um comando enviado cuja resposta se perdeu, **quando** o relógio reenviar o mesmo `id`, **então** o servidor devolve o recibo original e não cria um segundo evento.
- **Dado** o mesmo `id` com equipe diferente, **então** 409 e nenhum evento.
- **Dado** 5 toques rápidos, **então** o servidor registra 5 pontos, na ordem tocada.
- **Dado** o telefone bloqueado e o navegador em segundo plano, **quando** tocar no relógio, **então** o ponto é aplicado pela rede do relógio.
- **Dada** a partida encerrada confirmada, **então** os botões ficam indisponíveis. Um comando que chegue mesmo assim é recusado com recibo, e a fila pausa com o motivo visível.
- **Dada** uma partida nova iniciada no telefone com comandos pendentes da anterior, **então** esses comandos são recusados, não aplicados à nova partida, e aparecem para descarte explícito.
- **Dado** o app reaberto ou a tela reacendida, **então** o placar e a fila pendente reaparecem, sem toque registrado enquanto a tela estava apagada.

## Decisões de desenho
- **A chave é estado da sala, validado no servidor**, não preferência do navegador. Esconder botão não é controle de acesso (guia de desenvolvimento). Por isso `pontos`/`desfazer` do site são recusados no backend quando a chave está ligada.
- **Com a chave ligada, o relógio não depende do `controle_id` do site.** Quem controla o placar é o relógio, e a troca de controle entre pessoas no site deixa de afetar a pontuação. A troca da chave incrementa `controle_versao`, então nenhum lance de antes da troca é aplicado depois dela.
- **Desligar é mais permissivo que ligar.** Qualquer ADMIN pode desligar, para não prender a partida a um relógio sem bateria. Ligar exige relógio vinculado.
- **"Em breve…" é filtro de interface**, deliberadamente: a segurança continua no `watch_grants`, e o filtro por nome pode sair quando o recurso abrir a outros usuários.
- **Rota própria do relógio + recibo, sem reaproveitar `/pontos` com Bearer.** Motivo: o recibo idempotente é exigência da DS (base para US3/US4). Colocá-lo na rota do site mudaria o contrato web sem necessidade. A regra de pontuação continua única (`executar_sync`).
- **Recusas registradas como recibo.** Assim o resultado de um `id` é determinístico: um reenvio depois de um desfazer que reabra a partida não aplica um ponto que já tinha sido recusado.
- **Evento `PONTO_MARCADO` inalterado.** O vínculo com o comando fica no recibo (`evento_seq`), sem risco para a projeção nem para a linha do tempo.
- **Previsão de vitória no relógio.** Evita que o toque depois do ponto de vitória vire uma recusa previsível. O custo é duplicar ~15 linhas de regra, cobertas por teste em Kotlin espelhando os casos do Python.
- **Fila em arquivo JSON com escrita atômica**, sem Room. A fila é curta e de um só usuário, e o Room traria dependência e código gerado desproporcionais. Pode ser reavaliado na US4.
- **Envio só com o app em primeiro plano.** O envio em segundo plano (WorkManager) e a reconciliação ficam para a US4. A US2 não promete operação offline completa.

Alternativas rejeitadas: desativar o botão até a confirmação (piora o jogo com latência de Bluetooth); agrupar toques rápidos (perde ordem e auditoria); aplicar a fila na partida atual depois de uma recusa (proibido pela DS).

## Fora de escopo
Desfazer pelo relógio (US3; com a chave ligada, desfazer fica indisponível até a US3, a menos que se desligue a chave e desfaça pelo site). Envio em segundo plano, revisão de conflito pelo telefone e reconciliação offline (US4). Inversão de lados no relógio, tiles, complicações e tela sempre ligada. Assumir o controle pelo relógio. Escolher no relógio qual equipe é "Nós". Relógios para outros usuários (o "Em breve…" só sinaliza).

## Versão
`0.8.0` (minor: nova capacidade de pontuar pelo pulso). Atenção: o servidor apaga o banco quando a versão muda. O deploy deve ser feito fora de uma partida, como na 0.7.0.

## Validação prevista
- `uv run pytest` com testes novos: aplicação, reenvio idempotente, `id` com conteúdo divergente, reenvio concorrente, ordem A/A/B, partida trocada, controle trocado, partida encerrada, dispositivo revogado, broadcast para o navegador.
- Testes novos da chave: ligar sem relógio (recusa), desligar por ADMIN, versão incrementada, `pontos`/`desfazer` do navegador recusados com a chave ligada, configurar/reiniciar permitidos, revogação desliga a chave, evento na linha do tempo.
- `ruff check`/`format --check`; web `npm test` (novos: filtro do nome eli, ícone `relogio`), `npm run check`, `npm run build`.
- Android: testes da fila (persistência, ordem, remoção por recibo), da previsão e de `avaliar_vitoria`; `assembleDebug` e `lintDebug`.
- Roteiro físico (test-guide, no Passo 4): Watch + telefone admin + navegador espectador + um segundo participante não-eli ("Em breve…"); ligar a chave e conferir o site somente leitura; A/A/B; toques rápidos; telefone bloqueado; luz externa; animações reduzidas; apagar e reacender a tela; encerrar a partida; nova partida com fila pendente (modo avião no relógio).

## Riscos e pontos para o Navigator
1. **Nós = equipe A.** Adotado pela ordem do exemplo do Navigator (Eli Junior e Camila × Rafa e Marvin): quem configura a partida põe a própria dupla como equipe A. Confirmar.
2. **Estado inicial da chave:** proposta **desligada** ao vincular; eli liga nas configurações quando for jogar. A alternativa é ligar automaticamente ao vincular.
3. **Descarte no próprio relógio** (item 19): proposta para a US2 não travar sem saída. A decisão aprovada de revisar conflitos no telefone é mantida para a US4. Confirmar.
4. **Deploy apaga salas** ao subir a 0.8.0 (comportamento existente, dívida `banco-de-producao-sem-volume-persistente`).
5. Tamanho da tela do Watch 8 ainda não informado (40 ou 44 mm). O layout usará proporções da tela, mas a ergonomia só fecha no teste físico.
6. O snapshot do WebSocket inclui a linha do tempo inteira. Para uma partida de vôlei isso é pequeno, mas o relógio vai ignorar esse campo.
