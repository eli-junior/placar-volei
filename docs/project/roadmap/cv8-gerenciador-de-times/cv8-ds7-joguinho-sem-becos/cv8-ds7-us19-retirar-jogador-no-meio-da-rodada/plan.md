# Plano — CV8.DS7.US19 Retirar jogador no meio da rodada (com a TS3)

Branch: `feature/cv8-ds7-us19-retirar-jogador` · Versão alvo: **0.48.0** (minor: ação nova na API, schema 11 do `gerenciador.db`, regra nova na condução)

## Por que esta história é a mais delicada da DS7

A condução não guarda "quem está onde": `derivar` **reconstrói** quadra, fila, reis e eliminados a partir da ordem do sorteio e dos resultados. Isso faz três pedidos da decisão C mexerem na história, e não só no estado de agora:

1. **Time que fica sem nenhum jogador deixa de existir.** Se ele já jogou (vencedor que ficou na quadra, rei), os resultados gravados ainda o citam; apagar a linha quebra a reconstrução ("resultado de uma partida que não estava em quadra"). E remover só no estado final deixa a quadra ocupada por um time fantasma entre uma partida e outra.
2. **"Ninguém elegível na vez de entrar: o time é pulado."** Pular é reordenar, e reordenar um time que já jogou quebra o replay pelo mesmo motivo.
3. **A vaga vazia exige substituto ao entrar em quadra, inclusive o rei no mata-mata.** Hoje o bloqueio de "escolher o parceiro" só existe na fase de fila.

## Desenho

### TS3 — ajustes da fila (base técnica, sem tela)

- Tabela nova `ajustes_fila` (schema 11, aditiva): `rodada_id`, `apos_partidas` (quantas partidas encerradas existiam), `tipo` (`remover` | `pular`), `time_id`.
- `derivar(..., ajustes)` aplica cada ajuste **logo depois da partida de número `apos_partidas`** (fila e mata-mata contadas juntas) e antes de encher a quadra de novo. `remover` tira o time da quadra/fila/reis/rivais; `pular` manda o time para o **fim** da fila (ou do rol de rivais). Sem ajustes, a saída é idêntica à de hoje (teste de equivalência). "Desfazer a última partida" continua coerente: um ajuste com `apos_partidas` maior que as partidas existentes passa a valer no fim da sequência.
- Um time só é "removido" quando fica com **zero jogadores**; o cálculo é feito na hora da retirada e gravado como ajuste.

### US19 — retirar o jogador

- **Ação:** `POST /api/rodada/retirar` `{ "jogador_id": … }`, só com rodada **em andamento**. Na mesma transação: remove o jogador de **todos** os times em que consta (o escalado joga por dois), tira a presença (ausente nas próximas rodadas, como na US10; volta como atrasado, US9), marca o time com vaga como incompleto e, se algum time ficou vazio, grava o ajuste `remover`.
- **Bloqueios, com o motivo na tela:** jogador de um time **em jogo** (partida chamada) não sai; é preciso encerrar ou anular (US16). Rodada em proposta continua com "descarte e remarque" (fora do escopo).
- **Vaga na hora de entrar em quadra:** time incompleto em quadra continua pedindo o parceiro pela lista de escalação (RN-07, US8), agora também no **mata-mata** (rei com vaga entra pelos eliminados, mantendo o time misto, RN-01/RN-16). "Chamar partida" fica bloqueado até preencher. O time com vaga mantém vitórias e posição na fila.
- **Sem elegível:** em vez de "Cancele a rodada", a caixa de escalação oferece **Pular o Time N** (grava o ajuste `pular`: o time vai para o fim da fila e a próxima partida usa o seguinte).
- **Tela:** em Presentes, com rodada em andamento, cada jogador ganha **Retirar da rodada**; a confirmação diz o efeito ("Time 3 fica incompleto e escolhe parceiro na vez dele" / "O Time 4 deixa de existir"). Com partida chamada o botão fica desabilitado com o motivo ao lado.

### Alternativas descartadas

- **Apagar o time vazio e regravar `fila`:** quebra o replay dos resultados que o citam.
- **Substituir a US10 pela retirada:** a US10 resolve "alguém entra no lugar agora, com vitórias preservadas"; remover essa saída tira uma opção útil e muda comportamento já validado. Veja a pergunta 1.
- **Pular automático (sem confirmação):** o operador pode preferir esperar um atrasado a perder a vez do time; por isso é um botão.
- **Marcar `retirado` em `time_jogadores` em vez de apagar a linha:** guarda histórico, mas obriga todo consumidor (saldos, histórico, sorteio seguinte) a filtrar. A US10 já reescreve a linha; seguimos o precedente.

## Perguntas para o Navigator (decidir antes de implementar)

1. **Relação com a US10 (Substituir).** Recomendo **conviverem**: *Substituir* = alguém entra no lugar agora (fila ou eliminados); *Retirar* = sai sem substituto, a vaga espera a vez do time. Nada da US10 muda. Alternativa: aposentar o *Substituir*, deixando a retirada como único caminho (o substituto passa a ser sempre escolhido na hora de entrar).
2. **O que "pular" faz com o time.** Recomendo **fim da fila** (ele volta quando chegar a vez e houver elegível). Alternativas: o time sai da rodada; ou fica na frente e a cada partida a gente tenta de novo.
3. **Uma branch, duas histórias.** Recomendo fazer a **TS3 e a US19 na mesma branch** (a TS3 sozinha não tem o que o Navigator validar), com a TS3 registrada como item próprio do roadmap e commits separados. Alternativa: fechar a TS3 antes, como entrega interna.

## Escopo

- `app/gerenciador_db.py` (schema 11), `app/conducao.py` (`derivar` com ajustes), `app/rodada.py` (retirar, contexto com ajustes, escalação no mata-mata, "pular"), `app/rodada_rotas.py` (rotas `retirar` e `pular`), `app/sessao.py` se a presença exigir.
- Web: `Sessao.svelte` (Retirar da rodada e confirmação), `PainelConducao.svelte` (escalação no mata-mata e "Pular Time N"), regra pura do efeito da retirada em `web/src/lib/joguinho.js`.
- Testes: puros de `derivar` com ajustes (exemplos e invariantes), pytest da API (cada situação abaixo), unitários da web, e2e.
- Docs: CHANGELOG 0.48.0, roadmap (TS3 e US19), worklog, decisão registrada, `regras-de-negocio.md` e guia.

## Situações cobertas pelos testes

Time na fila; time em quadra sem partida chamada (inclusive vencedor que ficou); time em jogo (bloqueado); rei antes e durante o mata-mata; desafiante; jogador escalado em dois times; time que fica vazio na fila, na quadra e entre os reis; trio com 3→2→1→0; retirar e depois registrar como atrasado; desfazer a última partida depois de uma retirada; sem elegível → pular → fim da fila.

## Fora do escopo

Retirar na **proposta** (descartar e remarcar basta); US21 (placar manual/W.O.); permissões de quem opera (F5.2); reverter uma retirada (o jogador volta como atrasado, que já existe).

## Aceite (BDD)

- **Dado** um time na fila **quando** retiro um jogador dele **então** o jogador fica ausente e o time segue na fila como "Incompleto: escolhe o parceiro na sua vez".
- **Dado** um time com vaga **quando** chega a vez de entrar em quadra **então** "Chamar partida" fica bloqueado até a vaga ser preenchida pela lista de escalação (também para o rei no mata-mata).
- **Dado** um time **quando** todos os seus jogadores são retirados **então** ele sai da fila (ou da quadra, ou dos reis) e a próxima partida é recalculada, sem quebrar os resultados já registrados.
- **Dado** um time com vaga e **sem elegível** na vez de entrar **então** a tela oferece "Pular o Time N", que o manda para o fim da fila.
- **Dado** um jogador de um time em jogo **então** "Retirar da rodada" fica desabilitado, com o motivo ao lado.

## Riscos

- **Replay da condução:** é o risco principal; por isso a TS3 vem primeiro, com testes de equivalência e invariantes antes de qualquer tela.
- **Dados de produção:** a migração é aditiva (tabela nova), mas a primeira subida em produção deve seguir o backup automático do `gerenciador.db` (já existe).
- **Tamanho:** é a maior história da DS7; se a revisão achar o diff grande, o mata-mata (rei com vaga) pode ser separado numa US19b sem perder a TS3.
