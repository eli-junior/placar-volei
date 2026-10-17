---
status: Accepted
date: 2026-10-17
related:
  - CV8.DS7.US21
  - CV8.DS7 (decisão A)
---

# Vitória por W.O. em partida abandonada

## Contexto

Uma partida chamada só saía encerrada (placar terminado pelas regras) ou anulada (US16, não conta). Quando um time ia embora, chovia ou alguém se machucava, o grupo queria dar a vitória ao outro e só podia anular (QA F1.2, F1.3). A decisão A da DS7 (2026-10-08, "por ora só anular") adiou isso para a US21.

## Decisão (Navigator, 2026-10-17)

- Nova saída da partida chamada: **dar a vitória (W.O.)** a um dos lados. O operador escolhe o vencedor; quem lidera o placar vem pré-selecionado, nunca decide sozinho.
- **Para a rodada é uma vitória normal:** perdedor eliminado, vitória conta para rei, mata-mata e triângulo; "Desfazer a última partida" vale.
- **A nota não muda:** a partida não terminou; o Elo puniria quem saiu machucado ou premiaria um placar parcial.
- **Fora do saldo e da Resenha** (inteira, sem contar nem como partida jogada): a Resenha deduz o vencedor pelo placar e erraria num W.O. de quem perdia.
- **Conta no tempo sem jogar** (US23): o time esteve em quadra.
- O placar parcial lido da quadra fica guardado (0 × 0 se ela não está disponível), com `partidas_rodada.wo = 1` (schema 14). Nada é lançado no log de eventos do placar.

## Alternativas rejeitadas

- **Lançar o placar à mão:** mais trabalho na quadra e espaço para resultado inventado.
- **Registrar o W.O. no log da quadra:** o placar é um log de pontos, e W.O. não é ponto.
- **Vitória automática de quem liderava:** placar parcial não diz quem ganharia; quem decide é o grupo.
- **Contar o W.O. como "partida jogada" na Resenha:** exigiria um tipo de partida à parte em `estatisticas.py`; adiado sem demanda.

## Consequências

`app/ponte.py` (`_registrar_wo`, rota `POST /api/rodada/dar-vitoria`) grava o resultado sem `aplicar_partida`; `rodada.py` tira o W.O. do saldo e `estatisticas.carregar`, da Resenha. A decisão A da DS7 fica revista.
