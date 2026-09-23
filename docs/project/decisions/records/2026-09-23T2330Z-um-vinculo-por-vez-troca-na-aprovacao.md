---
id: um-vinculo-por-vez-troca-na-aprovacao
status: Decided
raised: 2026-09-23
decided: 2026-09-23
deciders:
  - Eli (Navigator)
  - Claude Opus 5.5 (Driver)
supersedes:
related:
  - CV3.DS1.US5
  - relogio-como-participante-com-controle-delegado
---

# Um Vínculo por Vez: o Relógio Troca de Quadra Só Quando o Código Novo é Aprovado

## Question

Até a 0.9.0, o relógio entrava direto na quadra ao abrir o app, e um código aprovado em outra quadra deixava o vínculo antigo ativo. Como trocar de quadra pelo próprio relógio, sem depender do telefone para revogar antes, e sem perder o vínculo atual se o Eli desistir?

## Decision

- O código novo usa um **token novo** e informa o token do vínculo que ele substitui (`POST /api/watch/pairing` com `substitui`). O servidor guarda só a referência (`watch_devices.substitui_id`).
- O vínculo antigo cai **na aprovação** do código novo, na mesma transação: o "Eli (Relógio)" sai da quadra antiga pelo caminho da revogação pelo telefone, e o controle volta ao dono ("relógio foi para outra quadra" na linha do tempo).
- A quadra antiga é alterada sem pegar o lock dela; o `BEGIN IMMEDIATE` do SQLite serializa as escritas, e um lance atrasado do vínculo antigo recebe 401.
- Desistir cancela o código no servidor (`DELETE /api/watch/pairing`). Sem rede, o cancelamento fica marcado e é refeito. Se a aprovação chegar antes do cancelamento, o relógio adota o vínculo novo.
- A fila da quadra antiga é descartada só na aprovação, depois de um aviso com o número de lances, confirmado ao pedir o código.
- A escolha **Retornar / Parear outra quadra** aparece quando a atividade é recriada (app reaberto), nunca quando a tela só apagou.

## Rationale

- Um token só obrigaria a desligar o vínculo antigo ao gerar o código; desistir deixaria o relógio sem vínculo.
- Sem o cancelamento, qualquer pessoa na quadra nova poderia aprovar o código abandonado nos cinco minutos seguintes e derrubar a quadra atual.
- Pegar os locks das duas quadras abriria deadlock entre duas trocas cruzadas; o SQLite já dá a atomicidade necessária.
- Perguntar a cada vez que a tela acende atrapalharia o jogo.

## Options Considered

- Reaproveitar o token atual para o código novo: rejeitado (desistir perderia o vínculo).
- Deixar o código abandonado expirar sozinho: rejeitado (janela de cinco minutos para derrubar o vínculo).
- Menu de troca no meio do placar: não pedido; a saída é reabrir o app.

## Consequences

- Cada "Parear outra quadra" gasta uma tentativa do limite de criação de código por IP (`debt-limite-de-vinculo-do-relogio-por-ip-e-em-memoria`).
- `GET /api/watch/session` envia `court_name`; o relógio guarda o nome para mostrar "Retornar" mesmo sem rede.
- A US4 (envio em segundo plano) precisa respeitar que a fila só é enviada com o app no placar, nunca na tela de escolha.

## Review Trigger

Se o relógio passar a enviar a fila em segundo plano (US4), ou se mais de um relógio por pessoa entrar no escopo.
