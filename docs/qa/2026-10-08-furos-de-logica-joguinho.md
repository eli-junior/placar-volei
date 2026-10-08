# Furos de lógica do Joguinho — visão do usuário

Data: 2026-10-08 · Produção: https://placar.elijunior.click/sessao (versão 0.46.1)
Escopo: só auditoria. Nenhum código, dado ou configuração foi alterado.
Complementa `2026-10-08-auditoria-producao.md` (infra, rota, segredo).

**Legenda de confiança**
- **Tela**: vi acontecendo no site em produção (screenshots em `evidencias/`).
- **Código**: li a regra no servidor e a conclusão decorre dela, mas não executei (o segredo do dono foi recusado depois do bloqueio por tentativas, e várias ações seriam destrutivas).

## Princípio violado

Uma sessão/rodada deve poder **sempre** ser encerrada por quem a opera, em qualquer estado. Hoje há estados em que nenhuma ação da tela leva a um estado válido.

---

## F1 — Não consigo encerrar o jogo (o caso real)

**Cenário:** abri um joguinho ontem, chamei a partida e não terminei.

| Passo que tento | Resultado | Confiança |
|---|---|---|
| Encerrar partida | Botão desabilitado: "A quadra vinculada não está disponível" | Tela |
| Encerrar sessão | Recusado: "Descarte a proposta ou cancele a rodada antes de encerrar a sessão" | Tela |
| Vincular outra quadra / criar quadra | Os controles nem aparecem enquanto há partida chamada | Tela + Código |
| Desvincular quadra | Idem; o servidor também recusa ("encerre-a antes de trocar o vínculo") | Código |
| Cancelar rodada | Único caminho; perde a rodada inteira | Tela (botão existe), Código |

**Furos de lógica por trás:**
1. **Encerrar depende 100% do placar da quadra.** O resultado só é lido do placar; se a quadra sumiu, a partida não tem como fechar.
2. **Não existe "encerrar sem placar"**: sem W.O., sem "partida interrompida", sem lançar resultado manual, sem "anular partida chamada" (voltar os times à fila).
3. **Mesmo com a quadra viva, só encerra quando o placar atingiu o fim** (erro "A partida ainda não terminou no placar"). Um jogo parado no meio (o seu caso de ontem) não pode ser fechado por ninguém.
4. **A mensagem manda "vincular de novo", mas a ação está bloqueada** pela própria partida chamada. A instrução é impossível de cumprir (deadlock circular).
5. **Não há expiração nem aviso de sessão velha.** A sessão aberta ontem continua "aberta" hoje; só pode haver uma sessão aberta por vez, então ela bloqueia abrir uma nova.
6. **Provável: Cancelar rodada não limpa a partida "chamada".** O cancelamento só marca a rodada como cancelada; a checagem que bloqueia vincular/desvincular olha qualquer partida chamada da sessão, não só a da rodada ativa. Se for isso, depois de cancelar a quadra ainda ficaria sem poder ser trocada. **Confiança: Código, precisa de teste.**

**Comportamento esperado (como usuário):**
- Botão sempre disponível: "Encerrar partida sem placar" (anula ou lança resultado manual) e "Encerrar jogo" (descarta tudo, com confirmação).
- Se a quadra sumir, a tela deve oferecer revincular ou anular, não esconder os controles.

## F2 — Não consigo tirar um jogador da lista de presentes

**Cenário:** o jogador foi embora e não deve ser escalado no próximo jogo.

| Situação | O que acontece | Confiança |
|---|---|---|
| Rodada ativa (proposta ou em andamento) | "Desmarcar" fica cinza em todos os presentes. "Presença travada: há uma rodada em andamento" | Tela |
| Mesmo aviso explica só no fim da página | Os botões cinza não dizem o porquê onde o usuário olha | Tela |
| Inativar o cadastro do jogador | Recusado: "está numa rodada ativa e não pode ser inativado" | Código |
| Substituir (a saída prevista) | Recusado se houver partida chamada: "encerre-a antes de substituir". Só aceita substituto da fila ou de eliminados | Código |
| Sair sem substituto | Não existe; time fica incompleto ou a rodada tem que ser cancelada | Código |

**Furos de lógica:**
1. **Para tirar alguém, é preciso antes encerrar a partida chamada; e para encerrar, é preciso a quadra** (F1). Os dois bloqueios se encadeiam: no estado atual, nenhuma saída de jogador é possível.
2. **Quem sai no meio da rodada exige substituto.** Se ninguém está disponível (fila vazia, ninguém eliminado), não há como retirar a pessoa.
3. **Os times são fixos desde a proposta** ("fila fixa"). Retirar alguém para o "próximo jogo" da mesma rodada só funciona via substituição; não há "marcar como ausente a partir do próximo jogo".
4. **Marcar ausente e cancelar são os dois únicos extremos**: ou muda tudo (cancelar rodada) ou nada (travado).

**Comportamento esperado:** "Retirar jogador" disponível a qualquer momento exceto durante a partida em quadra; ele vira ausente e, se estava num time, o time segue incompleto ou usa substituto quando houver, sem exigir cancelar a rodada.

## F3 — Quadra desaparece sem o Joguinho saber

- O banco das quadras é apagado a cada start do container (`RESET_DB_ON_STARTUP=true`), e a quadra também tem validade (`QUADRA_TTL_SECONDS=3600`, uma hora).
- O Joguinho guarda o código da quadra e a partida chamada em banco durável.
- **Furo:** nada reconcilia os dois lados. Um intervalo de mais de 1 h, um deploy ou um reboot no meio da rodada deixa a partida chamada apontando para uma quadra que não existe (Tela: Quadra 29397 indisponível; API `GET /api/quadras` vazia). Confiança: Tela + Código/Compose.
- **Esperado:** ao detectar quadra indisponível, o Joguinho oferece recriar a quadra com as mesmas duplas, ou anular a chamada.

## F4 — Mensagens que não ajudam a sair

| Onde | Mensagem | Problema |
|---|---|---|
| Painel da quadra | "indisponível — vincule de novo" | Não há como vincular (F1.4) |
| Botão Encerrar partida | desabilitado | O motivo está em texto pequeno abaixo e não oferece alternativa |
| Presentes | botões "Desmarcar" cinza | O motivo fica no fim da página |
| Encerrar sessão | "Descarte a proposta ou cancele a rodada" | Ensina a única saída destrutiva sem avisar que perde a rodada |

## F5 — Outros pontos de lógica a validar

1. **Cancelar rodada é irreversível e sem pré-visualização do que se perde** (placares encerrados, reis, fila). Não executei.
2. **O Joguinho exige o segredo do dono para tudo.** Quem opera na quadra sem o segredo não consegue nem encerrar. Um 429 ou 404 mascarado tira o acesso e apaga o segredo salvo (ver P5 do outro relatório).
3. **Sessão aberta por tempo indeterminado** não aparece como "de ontem" no topo.

---

## Cenários de regressão sugeridos (para quando formos corrigir)

1. Chamar partida → reiniciar o app → deve ser possível anular ou recriar a quadra, sem cancelar a rodada.
2. Chamar partida → deixar o placar no meio → "encerrar sem placar" funciona.
3. Rodada em andamento sem partida chamada → retirar jogador sem substituto.
4. Rodada em andamento com partida chamada → retirar jogador (o que deve acontecer?). **Decisão de produto.**
5. Cancelar rodada com partida chamada → depois, vincular outra quadra funciona.
6. Sessão aberta no dia anterior → aviso e opção de encerrar/continuar.
7. Quadra expirada por TTL no meio da rodada.

## Decisões de produto necessárias

- O que significa "partida abandonada": anula, W.O., ou registra o placar parcial?
- Retirar jogador no meio da rodada: com ou sem substituto obrigatório?
- Quanto tempo a quadra deve viver quando há rodada em andamento (hoje 1 h)?
- O banco das quadras continua efêmero quando existe rodada ativa?

## Não testado

Qualquer ação de escrita no Joguinho (cancelar, substituir, marcar ausente, encerrar sessão, criar partida) e os fluxos da quadra em si. Posso executar o roteiro acima no ambiente de produção se você me passar o segredo do dono na sua sessão do navegador e autorizar cada passo destrutivo, ou preferir rodar contra uma cópia local.
