# Plano de Implementação — CV2.DS1.US1: Nenhum toque no +1 se perde em silêncio

## 1. Contexto e Intenção

O fluxo do placar foi construído na `CV1.DS1.US2` assumindo a rede local estável do Mini PC. Em 4G de quadra, três comportamentos se somam contra o árbitro:

1. `App.svelte` tinha `if (!quadraAtual || !wsConectado || operando) return;` no início de `executar()`. Qualquer toque dado enquanto outro estava em voo era **descartado sem aviso**.
2. `Placar.svelte` tinha um `submetendo` local com `setTimeout(..., 250)` que bloqueava o botão por um quarto de segundo após cada toque — um segundo descarte silencioso, agora dentro do componente.
3. Com o socket caído, `desabilitado` já apagava os botões, mas a explicação era uma frase discreta no painel de controle, longe do polegar.

O resultado prático é o mesmo em todos os casos: o ponto não aparece e ninguém sabe se o toque chegou.

## 2. Nível no Roadmap e Branch

- **Nível**: User Story (`CV2.DS1.US1`).
- **Branch**: `worktree-agent-a5cb003370b910540`.

## 3. Escopo

### 3.1 Fila serializada (`web/src/App.svelte`)

```js
function enfileirarComando(tarefa) {
  pendentes += 1;
  operando = true;
  filaComandos = filaComandos.catch(() => {}).then(tarefa).finally(() => {
    pendentes = Math.max(0, pendentes - 1);
    if (pendentes === 0) operando = false;
  });
  return filaComandos;
}
```

- `executar()` deixa de retornar cedo por `operando` e passa a enfileirar.
- O `catch(() => {})` na cabeça da cadeia garante que uma falha não trave a fila inteira.
- `pendentes` alimenta a interface; `operando` continua valendo como "há algo em voo" para os botões que **devem** bloquear (assumir controle, gerenciar papéis).

### 3.2 Versão de controle lida no envio

`x-control-version` passa a ser lido de `quadraAtual.controle_versao` **dentro** da tarefa enfileirada. Se o comando anterior da fila mudou a versão (por exemplo, `assumir controle`), o próximo já sai com o valor certo em vez de tomar 409.

### 3.3 Separação de "desabilitado" e "enviando"

`SalaQuadra.svelte` passava `desabilitado={!wsConectado || operando}` para o `Placar`. Agora passa:

- `desabilitado={!wsConectado}` — não dá para agir;
- `enviando={operando}` — há comando em voo, mas o botão continua clicável;
- `pendentes` — quantos toques aguardam resposta.

### 3.4 Retorno visual (`web/src/components/Placar.svelte`)

- `aria-busy={enviando}` nos botões `+1`, `Desfazer` e `Iniciar Nova Partida`.
- Pulso de brilho e uma barra fina na base do botão enquanto `aria-busy="true"`.
- Aviso `role="status"` acima do placar: conexão caída (ícone girando, texto explicando que os botões voltam sozinhos) ou envio em andamento (`Enviando N toques na fila…`).
- Chip de reconexão com a mesma linguagem no painel de controle do `SalaQuadra`.
- Bloco `@media (prefers-reduced-motion: reduce)` desliga todas as animações novas e mantém o estado legível por contraste.

## 4. Comportamento de Aceite (BDD)

Ver `index.md`, seção *Acceptance / Done Condition*.

## 5. Decisões de Design

- **Serializar, não bloquear.** O bloqueio protegia o servidor ao custo de perder informação do usuário. A fila preserva a intenção de quem tocou e ainda respeita a ordem exigida pela versão de controle.
- **Sem otimismo local no placar.** O número só muda quando o snapshot volta. Manteve-se assim de propósito: o placar é a verdade compartilhada, e o `aria-busy` já cobre a lacuna de percepção sem arriscar mostrar um número que o servidor pode recusar.
- **Toque offline continua recusado.** Enfileirar toques com o socket caído criaria uma fila cega: sem saber se a partida encerrou ou se o controle mudou, a sincronização posterior poderia marcar pontos indevidos. A story garante recusa explícita, não aceitação otimista. Registrado como fora de escopo no `index.md`.
- **Remoção do debounce de 250 ms.** Era a proteção contra duplo toque acidental, e era ela que engolia o toque legítimo. Como `Desfazer` existe e é barato, o erro de excesso é reversível; o erro de falta não é perceptível.
- **`aria-busy` em vez de spinner sobreposto.** O botão continua clicável e o leitor de tela anuncia o estado. Um spinner por cima do alvo de toque reduziria a área útil no celular, que é o dispositivo real de uso.

## 6. Riscos

- Um toque acidental duplo agora vira dois pontos. Mitigação: `Desfazer` disponível e visível; o aviso de fila torna o excesso perceptível na hora.
- A fila cresce se o servidor ficar lento. Mitigação: o contador é exibido, então o operador vê o acúmulo em vez de sofrer com ele em silêncio.

## 7. O que está Fora de Escopo

- Fila offline persistente e reenvio automático.
- Reexecução automática de comando que falhou por erro do servidor.

## 8. Intenção de Versão

- **Minor** dentro da `CV2.DS1`: muda comportamento observável da interface de operação do placar.
