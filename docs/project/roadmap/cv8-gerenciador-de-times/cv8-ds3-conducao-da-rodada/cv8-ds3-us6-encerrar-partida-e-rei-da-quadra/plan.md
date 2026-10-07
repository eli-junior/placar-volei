# Plano — CV8.DS3.US6 Encerrar partida e aplicar rei da quadra

Nível: User Story. Branch: `feature/cv8-ds3-us6-encerrar-partida-e-rei-da-quadra`. Versão-alvo: **0.36.0** (minor; backend, web e APK por consistência; Wear inalterado).

## O que a história entrega

Depois que a partida acaba no placar, o operador toca em **Encerrar partida** no gerenciador. O sistema lê o placar final da quadra vinculada, registra o resultado e **faz a fila andar** (RN-02): o perdedor vira eliminado, o vencedor segue para o próximo confronto ou vira **rei** com 2 vitórias seguidas (e entram os 2 próximos da fila), e quando a fila acaba a fase de fila **termina** e o painel avisa que vem o mata-mata (RN-03). A derivação desse estado já existe desde a US5 (`app/conducao.py`); esta história **grava os resultados** que a alimentam.

## Como funciona

**Encerramento manual, com o placar como fonte (CA1)**
- `POST /api/rodada/encerrar-partida`: confere que há uma partida **chamada**, lê o placar da quadra vinculada e exige que **seja a mesma partida** que foi carregada na chamada (se alguém usou "nova partida" no placar, a leitura é recusada com a explicação) e que **tenha terminado** pelas regras do placar (alvo da rodada com vantagem de 2). Partida ainda em jogo → recusa com o placar parcial ("ainda não terminou: 7 × 5").
- Grava o resultado em `partidas_rodada`: `placar_a`, `placar_b`, `vencedor_time_id`, `encerrada_em`, e `estado = 'encerrada'`. O time A do gerenciador é a equipe A do placar.
- A derivação existente aplica as regras e devolve o novo painel (em quadra, fila, reis, eliminados, fim da fila). Nada de regra nova a inventar: só passa a haver resultados.
- Idempotente: encerrar de novo sem partida chamada → 409.

**Placar ao vivo no painel**
- A partida chamada passa a mostrar o **placar atual** da quadra (A × B, "terminou"/"em jogo") e o botão **Encerrar partida** só habilita quando terminou.
- Para o painel acompanhar o placar sem recarregar, cada evento da quadra **vinculada** também avisa o gerenciador (se houver aparelho conectado, a checagem é um `if` barato; só então o estado é recalculado e publicado). Toca no caminho quente do placar (`transmitir_estado`), por isso fica protegido por essa checagem e por `suppress` — a sincronia nunca derruba o placar.

**Painel**
- Bloco **Partida**: confronto, placar ao vivo, **Encerrar partida**.
- Bloco **Partidas encerradas** (histórico da rodada): ordem, placar e vencedor.
- Reis e eliminados passam a encher de verdade; vitórias seguidas aparecem no time em quadra.
- **Fim da fila (CA5):** faixa "A fase de fila terminou. Próxima fase: mata-mata" e **Chamar partida** bloqueado; o mata-mata em si é a US11.
- **Cancelar rodada** (paga a dívida `cancelar-rodada-nao-checa-partidas`): continua permitido, mas com partidas registradas pede **confirmação reforçada** ("já tem N partidas; elas ficam gravadas, mas a rodada deixa de contar"). Nada é apagado.

## Refatoração incluída

Reúne as **rotas e operações da rodada num módulo só** (`app/rodada_rotas.py`): hoje estão repartidas entre `sessao.py` (sorteio, resortear, confirmar, descartar, cancelar) e `ponte.py` (chamar partida). `sessao.py` volta a ser só sessão e presença. Paga a dívida `rotas-da-rodada-na-sessao-py`.

## API

- `POST /api/rodada/encerrar-partida`.
- `conducao.partida` ganha `placar` (`a`, `b`, `encerrada`, `vencedor`, `mesma_partida`) quando a quadra está disponível; `conducao.historico` lista as partidas encerradas; `conducao.pode_encerrar` e `conducao.motivo_encerrar` guiam o botão.

## Aceite (BDD)

- Given uma partida chamada que ainda está em jogo no placar, When toco em **Encerrar partida**, Then é recusado com o placar parcial e nada é gravado.
- Given a partida terminada no placar (ex.: 12 × 9 para o time 1), When encerro, Then o resultado fica gravado (12 × 9, vencedor Time 1), o Time 2 vira eliminado e o Time 1 segue em quadra com 1 vitória, contra o próximo da fila.
- Given o mesmo time que vence a segunda seguida, Then vira rei (1º rei), sai da quadra e entram os 2 próximos da fila.
- Given a fila esgotada com um time sozinho, ou a quadra vazia, Then o painel avisa que a fase de fila terminou e **Chamar partida** fica bloqueado.
- Given que alguém reiniciou a partida no placar depois da chamada, When encerro, Then recusa explicando que a partida do placar não é a chamada.
- Given a quadra vinculada indisponível, When encerro, Then recusa pedindo para vincular de novo (a chamada em aberto não se perde).
- Given dois aparelhos na sessão, When um encerra, Then o outro vê a fila andar sozinho; e o placar sendo jogado atualiza o painel ao vivo.
- Given uma rodada com partidas registradas, When cancelo, Then há confirmação reforçada e as partidas continuam gravadas.
- Given encerrar duas vezes seguidas, Then a segunda é recusada.

## Testes

- `tests/test_encerramento.py` (API + placar real): partida em jogo recusada; encerrar grava placar e vencedor (os dois lados); sequência completa de uma rodada pequena (vitórias, rei, entrada dos dois próximos, eliminados, fim da fila); partida trocada no placar; quadra indisponível; idempotência; concorrência; cancelar com partidas; histórico.
- `tests/test_ws_gerenciador.py`: evento de ponto na quadra vinculada publica o painel; quadra não vinculada não publica; placar não cai se o gerenciador falhar.
- `tests/test_conducao.py`: já cobre a derivação; acrescenta cenários de fim da fila pelo painel.
- Playwright: jogar uma partida no placar (pontos pela API) e ver o painel ao vivo, encerrar, fila andar, rei, fim da fila, axe.

## Alternativas rejeitadas

- **Encerrar automaticamente quando o placar termina:** a RN-09 diz que o encerramento é manual (operador confirma).
- **Aceitar o placar de uma partida não terminada** (encerramento antecipado, por tempo): abriria a pergunta de quem venceu; fica fora e pode virar história depois.
- **Guardar a situação da fila em colunas:** a derivação a partir dos resultados já existe, é testada e torna o desfazer da US7 trivial (apagar o último resultado).
- **Gerenciador consultar o placar por polling:** latência e carga; o gancho no evento é mais simples e instantâneo.

## Fora do escopo

Desfazer a última partida encerrada (US7); escolher o parceiro do time incompleto (US8); atrasados (US9); substituir quem saiu (US10); jogar o mata-mata e declarar o campeão (US11); encerrar a rodada; sortear as rodadas seguintes (US4).

## Pontos para o Navigator confirmar

1. **Só se encerra uma partida que terminou pelas regras do placar** (alvo com vantagem de 2); não há encerramento antecipado.
2. **Cada evento da quadra vinculada avisa o gerenciador** (placar ao vivo no painel e botão que habilita sozinho). Toca no caminho quente do placar, com checagem barata e proteção.
3. **Cancelar rodada com partidas registradas** passa a pedir confirmação reforçada, sem apagar nada, em vez de ser bloqueado.
4. **Reunir as rotas da rodada num módulo** (`rodada_rotas.py`) como parte desta história.
5. **Fim da fila** só avisa e bloqueia novas chamadas; o mata-mata e o caso da quadra vazia ficam para a US11.

## Riscos

- **Dependência do placar:** se a quadra sumir (reinício/1 h parada) com uma partida chamada e ainda não encerrada, o resultado não pode ser lido: a partida fica "chamada" até a quadra ser vinculada de novo (não há como recuperar o placar). Mitigação: aviso claro; o operador pode cancelar a rodada.
- **Consistência placar × gerenciador:** o resultado é uma cópia do placar no instante do encerramento; correções posteriores no placar não o alteram (o desfazer é a US7).
