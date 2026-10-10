---
status: Accepted
date: 2026-10-10
related:
  - CV8.DS2.US4
  - RN-10
  - RN-14
---

# Nota do jogador evolui com as partidas

## Contexto

O Navigator viu que, no painel de times do `/joguinho`, todos os jogadores ficam com a nota inicial (por exemplo 60) depois de várias partidas. Pela RN-14 isso é o desenho atual: a `nota` cadastrada **nunca muda**; só uma "nota efetiva" (saldo da sessão, até ±15) é usada no sorteio da rodada seguinte, e `time_jogadores.nota` guarda a do sorteio, congelada. Em 2026-10-10 o Navigator pediu **atualizar a nota cadastrada**, para que ela evolua com os resultados.

## Decisão (Navigator, 2026-10-10)

O Navigator escolheu **atualizar a nota cadastrada**, com o sorteio usando **só a nota atual** (a nota efetiva sai) e intensidade **moderada (K = 4)**. O desenho abaixo é o que foi implementado.

- **Quando:** a cada partida encerrada, na mesma transação do resultado. Cada jogador do time ajusta a própria nota (o escalado ajusta por cada partida em que jogou). Partida anulada não ajusta.
- **Fórmula (Elo adaptado à escala 1–100):** força do time = média das notas atuais dos jogadores; `esperado = 1 / (1 + 10^((força_rival − força_própria) / 30))`; `delta = round(K × (resultado − esperado) × fator_margem)`, com `resultado` 1 para vitória e 0 para derrota, `K = 4` e `fator_margem = 0,5 + min(1, margem ÷ alvo)` (0,5 a 1,5); nota final limitada a 1–100. Dois times iguais: vitória apertada (margem de 2 em alvo 10) dá +1 / −1, vitória por 7 dá +2 / −2 e goleada +3 / −3; azarão que ganha leva mais.
- **Desfazer:** cada ajuste fica registrado por jogador e partida (tabela `ajustes_nota`, schema 13, aditiva). "Desfazer a última partida" reverte o ajuste daquela partida.
- **Sorteio seguinte usa a nota atual.** A "nota efetiva" (saldo ±15) deixa de existir, para o mesmo resultado não contar duas vezes. A prioridade de gênero, a serpentina e a preferência por não repetir dupla seguem como estão.
- **Painel:** mostra "60 → 62" (nota do sorteio → nota atual) ao lado do jogador. A tela Jogadores já lê a nota atual.
- **Edição manual** continua valendo e sobrescreve a nota atual.

## Alternativas consideradas

- Manter a RN-14 e só **mostrar** a nota efetiva ao vivo: não muda a base, mas não responde ao pedido.
- Só **mostrar o saldo** (+/−) por jogador: igualmente não atualiza a nota.
- Ajuste só no fim da sessão: o painel continuaria parado durante o jogo.

## Consequências

- Muda a RN-14 ("a nota cadastrada não muda") e a RN-10 (ranking por saldo vira nota atual).
- As notas passam a refletir o histórico: quem ganha sobe e passa a ser separado de quem ganha muito. É o objetivo, mas não volta ao valor inicial sozinho.
- A primeira subida em produção deve seguir o backup automático do `gerenciador.db`.
