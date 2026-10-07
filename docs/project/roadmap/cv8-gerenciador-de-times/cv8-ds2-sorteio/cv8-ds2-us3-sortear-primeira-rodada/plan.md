# Plano — CV8.DS2.US3 Sortear a primeira rodada

Nível: User Story (a maior da CV8 até aqui). Branch: `feature/cv8-ds2-us3-sortear-primeira-rodada`. Versão-alvo: **0.34.0** (minor; backend, web e APK por consistência; Wear inalterado).

## O que a história entrega

Com a sessão aberta e 4 ou mais presentes, o operador escolhe o alvo (10 ou 12), pede o sorteio e vê uma **proposta**: as duplas **equilibradas pela nota**, com o gênero prevalecendo, e a **fila** ordenada pela ordem de chegada. Ele pode **resortear** (outra combinação equivalente), **descartar** ou **confirmar e iniciar**. Confirmada, a rodada fica "em andamento" com a fila fixa. **Jogar as partidas é a DS3** (US-05/06): esta história termina com a rodada montada.

## Regras aplicadas

- **RN-11 / CA1:** menos de 4 presentes → 409 com a mensagem "faltam N".
- **RN-14 / CA3:** duplas equilibradas pela nota, sem aleatoriedade na combinação-base.
- **RN-01:** o número de duplas H+H é o **mínimo possível** (só o excedente de homens sobre mulheres: `max(0, (H − M) / 2)` entre os que formam duplas); M+M é livre. O gênero prevalece sobre o equilíbrio.
- **RN-05 / CA4:** número ímpar → o jogador sem par forma um time incompleto, **por último na fila**.
- **RN-13 / CA5:** a fila ordena os times completos pela **menor ordem de chegada entre seus jogadores**; o time incompleto vai ao fim. Os dois primeiros times da fila jogam a primeira partida (se o 1º e o 2º a chegar estão na mesma dupla, entra a dupla de quem chegou em 3º, e assim por diante).
- **RN-09 / CA2:** o alvo (10 ou 12) é escolhido antes do sorteio e fica gravado na rodada. O padrão da tela é 10.

## Algoritmo (módulo puro `app/sorteio.py`, sem banco)

1. **Jogador ímpar** (se houver): o **último a chegar** (maior ordem de chegada) sai do pareamento e vira o time incompleto.
2. **Combinação-base** com `k = max(0, (H − M)/2)` duplas H+H obrigatórias (H e M contados entre os que vão formar duplas): ponto de partida construído para já respeitar a RN-01, depois **melhorado por trocas de jogadores entre duplas** que (a) mantêm exatamente `k` duplas H+H e (b) reduzem a variância das somas de nota das duplas. Parte da serpentina por nota (1º com último, 2º com penúltimo) e usa semente fixa → **mesmo resultado sempre** para os mesmos dados.
3. **Resortear (CA5):** gera outra combinação com a **mesma garantia de gênero** e com **amplitude** (maior soma − menor soma) no máximo **3 pontos pior** que a melhor; a semente deriva de (sessão, rodada, nº da tentativa), então é reproduzível. Se não houver outra combinação diferente dentro da tolerância, devolve a melhor e a tela avisa "não há outra combinação equivalente".
4. **Fila:** ordena pela regra da RN-13 acima.

Alternativas descartadas: busca exata por enumeração (explode com 20+ jogadores e não gera variantes naturais); sorteio puramente aleatório (contraria a RN-14); resortear refazendo a serpentina (daria sempre o mesmo resultado).

## Dados (schema 4 do `gerenciador.db`, migração aditiva)

- `rodadas (id, sessao_id, numero, alvo, estado, tentativa, criado_em, confirmado_em)`; estados `proposta`, `em_andamento`, `cancelada` (e `encerrada`, que só a DS4 usa). Índice único parcial: **no máximo uma rodada `proposta`/`em_andamento` por sessão**.
- `times (id, rodada_id, fila, incompleto)` e `time_jogadores (time_id, jogador_id, nota, ordem_chegada)`: guarda a nota e a chegada **usadas no sorteio** (auditoria; mudar a nota depois não reescreve a rodada).

## API (todas com `OWNER_SECRET`; a rodada vem junto do `GET /api/sessao`)

- `POST /api/rodada/sorteio {alvo}` — cria a proposta (tentativa 0).
- `POST /api/rodada/resortear {alvo?}` — nova tentativa da mesma proposta (pode trocar o alvo).
- `POST /api/rodada/confirmar` — proposta → em andamento.
- `POST /api/rodada/descartar` — apaga a proposta.
- `POST /api/rodada/cancelar` — rodada em andamento → cancelada (só enquanto não houver partida; na DS3 essa regra passa a existir).

## Bloqueios que entram junto (o que mexe com a rodada)

- **Presença trava** (marcar, desmarcar, reordenar, cadastro rápido) enquanto houver rodada em proposta ou em andamento → 409 "há uma rodada ativa". Isso é a "trava da reordenação antes do sorteio" da RN-15. Atrasados e saídas passam a ser tratados nas US-09 e US-10.
- **Inativar** um jogador que está numa rodada ativa → 409.
- Sorteio com rodada ativa → 409; sessão encerrada com rodada ativa → 409 (cancele antes).

## Refatoração incluída

Extração do **módulo comum do `gerenciador.db`** (dívida registrada na US2, gatilho: um terceiro módulo): `app/gerenciador_db.py` com `conectar`, `erro_de_campo`, `agora` e a transação de escrita, em nomes públicos; `jogadores.py` e `sessao.py` passam a usá-lo, sem mudar comportamento. Quita a dívida `modulo-comum-do-gerenciador-db`.

## Tela (`/sessao`)

- Seção **Sortear**: alvo 10/12 (padrão 10), botão **Sortear** (desabilitado com aviso se faltarem presentes).
- **Proposta:** a fila em ordem, com a **1ª partida em destaque** ("Em quadra: X × Y"), cada time com os nomes, notas e a soma; o time incompleto marcado ("escolhe o parceiro na sua vez"); botões **Resortear**, **Descartar**, **Confirmar e iniciar**.
- **Rodada em andamento:** a mesma lista, rótulo "Rodada 1 — alvo N" e **Cancelar rodada** (com confirmação). A lista de presença fica só de leitura enquanto a rodada existir.
- Componente novo `PainelRodada.svelte` (apresentação) usado nos dois estados.

## Aceite (BDD)

- Given 3 presentes, When tento sortear, Then é recusado ("faltam 1").
- Given 8 presentes (notas 90, 85, 70, 65, 60, 55, 40, 30) e nenhuma restrição de gênero, When sorteio, Then as somas das 4 duplas ficam o mais próximas possível (amplitude mínima) e o resultado é o mesmo em duas chamadas idênticas.
- Given 6 mulheres e 2 homens, Then nenhuma dupla é H+H; Given 6 homens e 2 mulheres, Then há exatamente 2 duplas H+H (o excedente) e as duas mulheres formam duplas com homens.
- Given 7 presentes, Then o último a chegar fica sozinho num time incompleto, por último na fila.
- Given que a 1ª e a 2ª a chegar caíram na mesma dupla, Then a primeira partida é dessa dupla contra a dupla de quem chegou em 3º.
- Given uma proposta, When resorteio, Then a nova combinação difere da anterior, mantém o gênero e a amplitude fica a até 3 pontos da melhor.
- Given uma proposta, When confirmo, Then a rodada fica em andamento com o alvo escolhido e a presença fica travada; When cancelo, Then a presença volta a ser editável.
- Given o servidor reiniciado, Then a proposta ou a rodada em andamento continuam como estavam.
- Given a tela dentro do APK, Then continua oculta.

## Testes

- `tests/test_sorteio.py` (puro): gênero (todas as combinações de H/M de 4 a 20 jogadores: nº de H+H = mínimo), ímpar, determinismo, fila pela chegada (inclusive o caso 1º e 2º na mesma dupla), resortear (difere, respeita a tolerância, reproduzível), notas iguais, propriedade com muitas entradas aleatórias.
- `tests/test_rodada.py` (API): 409 por faltar jogadores/sessão/rodada ativa, ciclo proposta → resortear → confirmar → cancelar, descartar, unicidade da rodada ativa (inclusive concorrente), trava de presença, inativar bloqueado, persistência após reset, migração 3→4.
- `npm test` (helpers de formatação da proposta) e Playwright (fluxo completo + axe).

## Fora do escopo

Sortear as rodadas seguintes e o saldo/nota ajustada (US-04); evitar repetir duplas da sessão (RN-10, só rodadas 2+); chamar partida, placar, rei da quadra, mata-mata (DS3/DS4); escolha do parceiro do incompleto (US-08); atrasados (US-09); sincronia em tempo real entre aparelhos (US-05); editar a proposta à mão (trocar jogadores entre duplas).

## Pontos para o Navigator confirmar

1. **Quem fica de fora quando o número é ímpar:** o **último a chegar**. Premia a pontualidade e combina com a RN-05 (ele joga por último). A regra original não dizia como escolher o ímpar.
2. **"Resortear" = outra combinação igualmente equilibrada** (amplitude até 3 pontos pior que a melhor), mantendo o gênero. Como o sorteio não é mais aleatório, esta é a leitura que preserva o botão do CA5.
3. **Presença travada durante a rodada** e os botões extras **Descartar proposta** e **Cancelar rodada**: não estão nos CAs, mas sem eles o sistema prende a sessão numa rodada que ainda não pode ser jogada (a DS3 vem depois).
4. **Alvo padrão 10** na tela (o projeto já adotou 10 como padrão no placar).
5. **A extração do módulo comum** entra nesta história (quita a dívida registrada).

## Riscos

- **Qualidade do equilíbrio:** a busca por trocas é heurística, não prova de ótimo. Mitigação: testes de propriedade contra um ótimo exato em casos pequenos (até 10 jogadores) e a tolerância documentada.
- **Tamanho:** é grande; se passar do razoável, separo a refatoração do módulo comum numa TS à parte antes de começar o sorteio.
