# Plano — CV3.DS1.US3 Desfazer o último ponto pelo relógio

Branch: `feature/cv3-ds1-us3-desfazer`, criada da `master` em `91b471e` (0.8.0).

Nível: User Story. Versão pretendida: `0.9.0` (minor, nova capacidade no pulso).

## Escopo

### Servidor
1. `POST /api/watch/comandos` aceita `acao: "desfazer"` além de `"ponto"`. O desfazer leva **um alvo**, e só um dos dois:
   - `alvo_seq`: o `seq` de um ponto confirmado que o relógio viu;
   - `alvo_comando`: o `id` de um lance anterior da fila do próprio relógio. O servidor o resolve pelo recibo (`watch_recibos.evento_seq`).
2. O desfazer só é aplicado se o alvo ainda for **o último ponto ativo** da partida. Se não for (outro ponto entrou depois, o alvo já foi desfeito, ou o lance-alvo foi recusado), o recibo é `RECUSADO` com a mensagem "O placar mudou; este desfazer não foi aplicado." Nenhum outro ponto é tocado.
3. As outras regras continuam valendo para o desfazer: quem está no controle, `controle_versao`, `partida_id`, idempotência por `id` e 409 para `id` repetido com conteúdo diferente (agora o alvo também faz parte do conteúdo).
4. `watch_recibos` ganha a coluna `alvo` (migração aditiva). O evento gravado é o `PONTO_DESFEITO` de sempre, com `ref_seq`, e aparece na linha do tempo com o autor "Eli (Relógio)". Desfazer o ponto de vitória reabre a partida pelo caminho que já existe.
5. `estado_partida` passa a enviar `equipes_ativas`, paralela a `eventos_ativos_seq`, para o relógio saber de que equipe é cada ponto confirmado.

### Relógio
6. **Pilha prevista:** pontos confirmados ativos, seguidos dos lances pendentes. Cada desfazer na fila tira o topo. O placar previsto sai dessa pilha.
7. **Botão desfazer:** faixa inferior inteira, "↶ Desfazer". Um toque, sem confirmação, como no site. Fica desabilitado quando a pilha prevista está vazia e some quando o controle não está no relógio. *(Ajustado no teste físico: a versão inicial era um círculo de 48 dp.)*
8. O toque grava na fila um comando `desfazer` cujo alvo é o topo da pilha: `alvo_comando` se o topo for um lance pendente, `alvo_seq` se for um ponto confirmado. Envio FIFO, como os pontos.
9. Desfazer continua disponível com a vitória prevista ou com a partida encerrada. Os botões de ponto seguem travados nesses casos.
10. **Retorno:** vibração diferente da do ponto, e o número desce com a animação invertida (sai para baixo). Com animações reduzidas, só troca o número.
11. **Recusa:** reaproveita a retenção da US2. A fila pausa, mostra o motivo e oferece o descarte confirmado. A revisão pelo telefone fica para a US4.

### Indicador de conexão (ajuste do Navigator no teste físico)
13. O texto "● Conectado · N pendentes" vira uma bolinha maior, no alto: verde conectado, amarela processando (enviando ou reconectando), vermelha sem conexão, com o número de pendentes dentro. O texto continua como descrição para leitor de tela.

### Vínculo sem campo de servidor (pedido do Navigator no Checkpoint 1)
12. A tela de vínculo mostra só "Gerar código". O app usa sempre o endereço compilado (`BuildConfig.SERVER_URL`, trocável na compilação por `-PserverUrl`). Um token guardado para outro endereço é descartado.

## Checkpoint 1
Aprovado pelo Navigator em 2026-09-23, com duas decisões:
- ponto + desfazer ficam registrados na linha do tempo mesmo quando o desfazer acontece antes do envio;
- o item 12 entra nesta HU. A tela "Retornar à quadra / Gerar novo código" e o vínculo exclusivo a uma quadra vão para a [US5](../cv3-ds1-us5-um-vinculo-por-vez/index.md).

## Aceitação
- **Dado** o controle no relógio e o placar 0×0, **quando** tocar A, B e desfazer, **então** todas as telas mostram 1×0. A linha do tempo mostra o ponto de B desfeito por "Eli (Relógio)".
- **Dada** a tela de vínculo, **então** não há campo de endereço, só "Gerar código".
- **Dado** um lance ainda pendente (sem rede), **quando** desfazer, **então** o placar previsto volta na hora. Ao reconectar, o servidor aplica o ponto e o desfazer uma vez cada, na ordem, sem ponto ou correção duplicados. Reenviar qualquer um dos dois não duplica nada.
- **Dados** A, A, desfazer, desfazer, **então** o resultado é 0×0 e cada desfazer tem o seu próprio alvo.
- **Dada** a pilha prevista vazia, **então** o botão desfazer fica desabilitado, e um comando forjado sem ponto ativo é recusado pelo servidor.
- **Dado** um desfazer cujo alvo não é mais o último ponto ativo, **então** o servidor recusa, nenhum ponto muda, e o relógio retém a fila com o motivo até o descarte explícito.
- **Dado** o ponto de vitória confirmado, **quando** desfazer pelo relógio, **então** a partida reabre em todas as telas e os botões de ponto voltam.
- **Quando** o admin toca "Assumir o controle" com um desfazer pendente, **então** o desfazer é recusado e fica retido, como os pontos.

## Decisões de desenho

- **Alvo explícito, não "desfazer o último":** o relógio pode estar atrasado. Um "desfazer o último" genérico apagaria um ponto que o Eli nunca viu. A combinação de `controle_versao` com o alvo garante que só o ponto visto seja desfeito.
- **Só o topo é desfazível:** mesma regra do site (desfazer ponto a ponto). Desfazer um ponto do meio da pilha fica fora.
- **Rejeitado: cancelar o lance pendente no próprio relógio, sem enviar.** Ele pode já estar a caminho do servidor, e a corrida levaria a um ponto aplicado sem correção. Além disso, o princípio "nada é apagado" pede o registro.
- **Rejeitado: segurar o toque ou confirmar antes de desfazer.** Contraria "corrigir é tão barato quanto marcar".
- **`equipes_ativas` no snapshot, em vez de o relógio ler a linha do tempo:** o relógio fica preso a um campo simples e testado, não ao formato de exibição.

## Fora de escopo
- envio em segundo plano, revisão de conflito pelo telefone e fila após reinício com mudança de partida (US4);
- desfazer um ponto que não esteja no topo;
- gestos e botões físicos.

## Validação
- **Automatizada:** pytest (alvo por seq e por comando, alvo desatualizado, sem ponto, idempotência e 409 com alvo diferente, reabertura após vitória, troca de controle, migração); Kotlin (pilha prevista com pontos e desfazeres intercalados, escolha do alvo, persistência da fila com o novo formato, fila antiga da 0.8.0 ainda legível); ruff, `npm test`, `npm run check` e build.
- **Física:** Watch real, telefone admin e um espectador. Sequência A, B, desfazer → 1×0 nas três telas. Em modo avião: A, desfazer, reabrir o app, reconectar → nenhum ponto e dois eventos. Vitória e desfazer → partida reaberta. Assumir o controle pelo telefone com um desfazer pendente → retenção no relógio. O roteiro detalhado vai para o `test-guide.md` no Passo 4.

## Riscos
- O botão no centro inferior pode receber toques acidentais durante o rally. Validar a ergonomia no aparelho. Se incomodar, a alternativa é afastá-lo da borda ou reduzi-lo, sem confirmação.
- A fila da 0.8.0 guardada no relógio não tem o campo `acao`. A leitura trata a ausência como `ponto`.
