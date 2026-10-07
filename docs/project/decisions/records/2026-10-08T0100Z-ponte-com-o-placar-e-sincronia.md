---
id: ponte-com-o-placar-e-sincronia
status: Decided
raised: 2026-10-07
decided: 2026-10-07
deciders:
  - Eli (Navigator)
  - Claude Sonnet 5.5 (Driver)
related:
  - CV8.DS3.US5
  - sorteio-da-primeira-rodada
---

# Ponte com o Placar e Sincronia do Gerenciador

## Question

Como o gerenciador (durável, protegido pelo `OWNER_SECRET`) carrega as duplas no placar (quadras efêmeras, com participantes e papéis) e mantém todos os aparelhos em dia?

## Decision

- **Vínculo sessão ↔ quadra do placar:** a sessão guarda o código de uma quadra (coluna `quadra_id`, schema 5). Cria-se pela tela (**Criar quadra e vincular**, que usa a API de sempre e faz o operador admin no navegador) ou vincula-se por código. O vínculo é conferido a cada uso e pode estar **indisponível** (reinício do servidor, 1 h parada); trocar ou desvincular é bloqueado com partida chamada.
- **Chamar partida:** o servidor age **como o ADMIN da quadra** (autoridade do `OWNER_SECRET`, como o relógio de um admin) e usa o comando de nova partida com `zerar`: nomes das equipes, jogadores, alvo da rodada e vantagem de 2. É **recusada** se a partida da quadra tem pontos e não foi encerrada. O registro (`partidas_rodada`, uma `chamada` por rodada, índice no banco) vem antes do placar e é **desfeito se o placar falhar**.
- **Nomes no placar:** primeiros nomes ("Ana + Gil"), com a inicial do sobrenome quando há homônimos na rodada.
- **Condução** derivada (`app/conducao.py`, puro) dos resultados: em quadra, fila, reis na ordem, eliminados, fim da fila. Sem resultados é a situação inicial; os resultados chegam na US6. O gate de chamar considera quadra, partida aberta, fase e time incompleto (bloqueia até a US8).
- **Sincronia:** WebSocket `/ws/gerenciador`, hub próprio. O segredo vai na **primeira mensagem** (prazo de 5 s), nunca na URL; mesma comparação de tempo constante e mesmo limite de tentativas do HTTP. Toda mudança publica o estado completo; o estado leva `revisao` e o cliente descarta o mais velho.
- **Operação** segue exigindo o `OWNER_SECRET`: a RN-12 vale como "qualquer aparelho que conheça o segredo".

## Rationale

- Criar a quadra só no servidor deixaria o placar sem admin humano (a sucessão devolveria o comando a um admin ausente); a quadra criada pelo operador já nasce com dono.
- Registrar antes e compensar depois evita duas chamadas simultâneas e partida fantasma.
- Hub e rota próprios impedem que a rotina de sucessão das quadras trate o gerenciador como sala.

## Options Considered

- Quadra 100% no servidor; gerenciador como jogador comum; segredo na URL do WebSocket; reutilizar o hub das quadras; esperar a US6 para modelar o rei da quadra.
