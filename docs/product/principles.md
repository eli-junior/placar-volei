# Product Principles

Princípios de comportamento de produto do Placar Vôlei. Servem para orientar trade-offs de implementação, não para decorar o repositório.

## Principles

### O placar é auditável, não apenas atual

Todo estado visível deriva de um log de eventos append-only. Nada de contador mutável.

Na prática: marcar ponto grava evento; desfazer grava outro evento referenciando o anulado; nada é apagado. Se a discussão na quadra for "esse ponto foi meu", a linha do tempo responde. Uma implementação que atualize o placar sem gravar o evento correspondente está errada mesmo que a tela fique certa.

### Corrigir é tão barato quanto marcar

Erro de digitação é o incidente mais comum de um placar operado com uma mão, no sol, entre um rally e outro.

Na prática: desfazer é ponto a ponto, sem limite, até zerar, e está a um toque de distância — nunca atrás de menu, confirmação modal ou tela de histórico. Nenhuma correção exige explicar-se ao sistema.

### Todos veem a mesma partida

O placar é objeto compartilhado. Não existe visão privilegiada nem tela privada do operador.

Na prática: qualquer mudança de estado — ponto, correção, mudança de regra, troca de admin, takeover — é transmitida a todos os conectados e aparece na linha do tempo. Ação silenciosa de administrador é violação deste princípio, mesmo quando pareceria conveniente.

### A quadra manda, o software obedece

A regra do jogo é do grupo, não do sistema. O software não impõe uma interpretação de vôlei.

Na prática: pontuação-alvo, exigência de vantagem de 2 e teto da vantagem são configuráveis pela quadra. Quando uma regra precisar de valor padrão, escolher o padrão da pelada e deixá-lo ajustável, em vez de fixá-lo no código.

### Perder conexão não pode perder o jogo

Celular em quadra cai, o Mini PC reinicia, o navegador é fechado por engano.

Na prática: estado persiste em disco e é reconstruído do log; reconexão devolve o participante ao mesmo lugar, com o mesmo papel, sem reentrada manual; a ausência do admin é resolvida por sucessão automática, não travando a partida.

### Simplicidade de operação vale mais que completude de funcionalidade

O sistema roda no Mini PC do Navigator e é mantido por uma pessoa.

Na prática: um arquivo SQLite em vez de servidor de banco; sem fila, sem cache externo, sem serviço auxiliar; uma dependência nova precisa se justificar contra o custo de mantê-la ligada 24/7 numa máquina doméstica.

### O movimento conta o que mudou

Num placar compartilhado, a pergunta silenciosa é sempre "o que acabou de acontecer?". A resposta é dada por movimento, não por texto.

Na prática: o número do placar transiciona em vez de trocar seco; o evento entra na linha do tempo deslizando; o participante que chega ou sai aparece e some com transição; a vitória tem um momento visual próprio; um ponto desfeito é visivelmente desfeito, não apenas um número menor. Animação aqui é feedback funcional — story visível não fecha sem ela.

O limite é a legibilidade: nenhuma transição pode atrasar a percepção do placar atual nem competir com o próximo toque. Movimento na casa de 150–300 ms, e respeito a `prefers-reduced-motion`.

## Failure Costs

Nem todo erro custa igual, em ordem decrescente de gravidade:

1. **Placar errado sem rastro** — destrói a confiança no produto. Pior falha possível.
2. **Divergência entre telas** — dois participantes vendo placares diferentes.
3. **Perda de estado por queda ou restart.**
4. **Latência de propagação** — tolerável até alguns segundos.
5. **Falta de funcionalidade** — o grupo joga do mesmo jeito.
