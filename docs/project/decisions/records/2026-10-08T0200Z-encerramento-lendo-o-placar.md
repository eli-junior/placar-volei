---
id: encerramento-lendo-o-placar
status: Decided
raised: 2026-10-07
decided: 2026-10-07
deciders:
  - Eli (Navigator)
  - Claude Sonnet 5.5 (Driver)
related:
  - CV8.DS3.US6
  - ponte-com-o-placar-e-sincronia
---

# Encerramento da Partida Lendo o Placar

## Question

Como registrar o resultado de uma partida jogada no placar e fazer a fila andar, sem duplicar a regra de pontuação nem encerrar por engano?

## Decision

- **O placar é a fonte do resultado.** `POST /api/rodada/encerrar-partida` lê o placar da quadra vinculada e só aceita uma partida que **terminou pelas regras do placar** (alvo da rodada com vantagem de 2). Em jogo → recusa com o placar parcial. Não há encerramento antecipado.
- **Tem de ser a partida da chamada:** se alguém usou "nova partida" no placar, a leitura é recusada (a partida chamada fica aguardando). Quadra indisponível também recusa, sem perder a chamada.
- **O resultado** (`placar_a/b`, vencedor, hora) é gravado em `partidas_rodada`; o time A do gerenciador é a equipe A do placar. A fila **não é gravada**: continua derivada dos resultados (`app/conducao.py`), o que faz o desfazer da US7 virar "apagar o último resultado".
- **Placar ao vivo:** cada evento da quadra vinculada avisa o gerenciador (só se houver aparelho conectado; nunca derruba o placar). O botão **Encerrar partida** habilita sozinho quando o placar termina.
- **Cancelar rodada com partidas** continua permitido, com confirmação reforçada; nada é apagado.
- **Fim da fila:** o painel avisa a transição para o mata-mata e bloqueia novas chamadas; o mata-mata e o caso da quadra vazia ficam para a US11.
- **Rotas da rodada** reunidas em `app/rodada_rotas.py`.

## Rationale

- Ler o placar evita duas fontes de pontuação e erro de digitação; a RN-09 pede confirmação manual, que é o toque no botão.
- Derivar a fila dos resultados mantém um só dado gravado e deixa o desfazer trivial.

## Options Considered

- Encerrar automaticamente ao terminar no placar (contraria a RN-09); aceitar encerramento antecipado (abre a dúvida de quem venceu); guardar a situação da fila em colunas; consultar o placar por polling.
