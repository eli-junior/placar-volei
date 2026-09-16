---
code: CV2.DS1.US1
level: User Story
status: Validated
status_reason: implementada e testada, aguardando validação do Navigator
updated: 2026-09-15
related:
  - CV1.DS1.US2
  - docs/project/debt/items/2026-09-15T2210Z-toques-perdidos-e-erros-422-nao-normalizados.md
---

# CV2.DS1.US1 — Nenhum toque no +1 se perde em silêncio

## Intent

Devolver ao árbitro de beira de quadra a certeza de que o ponto entrou: cada toque no `+1` dá retorno visual imediato, toques rápidos consecutivos são todos enviados em ordem e, se a conexão cair, os botões se bloqueiam com um aviso de reconexão em vez de marcarem às cegas.

## Scope

- `web/src/App.svelte`: fila serializada de comandos (`enfileirarComando`). Um toque durante o envio de outro entra no fim da fila em vez de ser descartado; a versão de controle (`x-control-version`) passa a ser lida no momento do envio, não no momento do toque.
- `web/src/App.svelte`: contador `pendentes` exposto para a interface.
- `web/src/components/SalaQuadra.svelte`: separa "não dá para agir" (socket caído) de "tem comando em voo"; chip de reconexão com ícone animado e `role="status"`.
- `web/src/components/Placar.svelte`: `aria-busy` e pulso nos botões `+1`, `Desfazer` e `Iniciar Nova Partida` durante o envio; aviso de conexão caída acima do placar; aviso de fila (`Enviando N toques na fila…`); respeito a `prefers-reduced-motion`.
- Remoção do bloqueio local de 250 ms que engolia o segundo toque.

## Acceptance / Done Condition

```gherkin
Given uma sala aberta com o WebSocket conectado e eu no controle do placar
When eu toco cinco vezes seguidas no +1 da mesma equipe, mais rápido que a resposta do servidor
Then cada toque acende o retorno imediato do card da equipe e o botão fica com aria-busy="true" enquanto o envio acontece
And os cinco toques são enviados em ordem e o placar termina cinco pontos acima
And enquanto houver mais de um toque na fila a interface informa quantos estão sendo enviados

Given a mesma sala com o WebSocket desconectado
When eu olho os botões de marcação
Then eles estão desabilitados e visualmente apagados
And um aviso de reconexão em texto explica que os botões voltam sozinhos
And nenhum toque é aceito às cegas: se a ação chegar pelo teclado, a recusa aparece escrita em vez de sumir

Given que a conexão volta
When o WebSocket reconecta
Then os botões voltam a ficar ativos sem recarregar a página e o placar reconcilia pelo snapshot recebido.
```

## Validation Route

1. Dois clientes na mesma sala, um como admin no controle e outro como espectador.
2. Com o DevTools em `Network → Throttling → Slow 3G`, tocar cinco vezes seguidas no `+1`.
3. Observar o pulso e o `aria-busy` nos botões, o aviso de fila, e o placar final subindo cinco pontos nas duas telas.
4. Colocar o cliente que controla em modo avião por ~30 segundos e observar o bloqueio dos botões e o aviso de reconexão; voltar a rede e confirmar a reconciliação sem recarregar.

## Out of Scope

- Fila offline persistente: toques dados **com o socket caído** continuam não sendo aceitos, por decisão de correção — marcar às cegas e sincronizar depois abriria espaço para placar divergente entre operadores. O que a story garante é que a recusa é explícita, nunca silenciosa.
- Repetição automática de um comando que falhou por erro do servidor (o erro aparece escrito e o operador decide).
- Proteção contra duplo toque acidental: foi deliberadamente removida, porque era exatamente ela que engolia o segundo toque legítimo. O botão `Desfazer` cobre o engano.

## Notes

O débito descrevia dois sintomas com a mesma raiz — a interface não representava o estado de transporte da ação. Esta User Story cobre o sintoma dos toques; a `CV2.DS1.US2` cobre o sintoma das mensagens de erro.

A decisão mais forte aqui é **serializar em vez de bloquear**: a interface deixa de proteger o servidor descartando toques e passa a garantir ordem. Como o backend valida a versão de controle a cada comando, a serialização é o que permite enviar o segundo toque com a versão correta.
