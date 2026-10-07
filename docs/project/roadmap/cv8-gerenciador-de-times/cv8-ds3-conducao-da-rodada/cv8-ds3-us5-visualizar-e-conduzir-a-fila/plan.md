# Plano — CV8.DS3.US5 Visualizar e conduzir a fila

Nível: User Story — a ponte entre o gerenciador e o placar já existente. Branch: `feature/cv8-ds3-us5-visualizar-e-conduzir-a-fila`. Versão-alvo: **0.35.0** (minor; backend, web e APK por consistência; Wear inalterado).

## O que a história entrega

Com a rodada em andamento, o operador vê num painel **quem está em quadra, a fila, os reis e os eliminados**, toca em **Chamar partida** e o placar da quadra (a mesma do placar de sempre) passa a mostrar as duplas e o alvo, zerado. Tudo isso **atualiza sozinho em todos os aparelhos** abertos na tela da sessão.

Registrar o resultado da partida (e, com ele, a fila andar, o time virar rei, o perdedor sair) é a **US6**; desfazer é a US7. Aqui o painel já sabe **calcular** esse estado (RN-02), mas, sem resultados registrados, só a situação inicial aparece de verdade.

## Como o gerenciador conversa com o placar

O placar tem "quadras" (salas com código de 5 dígitos), eventos e participantes com papéis; o banco delas é **efêmero** e a sala expira após 1 h sem uso. O gerenciador é durável e protegido pelo `OWNER_SECRET`. A ponte:

- **Vínculo sessão ↔ quadra:** coluna `quadra_id` na sessão (schema 5). Duas formas de criar: **"Criar quadra e vincular"** (usa a API de sempre para criar a quadra — o operador vira o admin dela neste navegador — e grava o vínculo) ou **"Vincular por código"** (uma quadra que já existe). O vínculo é conferido a cada uso: quadra sumida ou expirada (reinício do servidor, 1 h parada) aparece como **"indisponível — vincule de novo"**.
- **Chamar partida:** o servidor age **como o admin da quadra** (o `OWNER_SECRET` dá essa autoridade, do mesmo jeito que o relógio de um admin já faz) e usa o comando existente de nova partida com `zerar`: carrega os dois times (nomes e jogadores), o alvo da rodada e a vantagem de 2 (RN-09), e transmite o novo estado a todos da quadra pelo WebSocket de sempre. Quem marca os pontos continua sendo o operador no placar normal.
- **Proteção:** se a partida atual da quadra tem **pontos e não foi encerrada**, a chamada é recusada ("encerre ou reinicie a partida no placar antes") — nada é zerado sem querer.
- **Nomes no placar:** "Ana + Gil" (primeiros nomes; com a inicial do sobrenome se houver dois com o mesmo primeiro nome na rodada), porque o placar tem pouco espaço. A lista de jogadores completa vai junto.

## Estado da condução (módulo puro `app/conducao.py`)

Deriva, a partir da fila da rodada e das partidas **já encerradas**, a situação do rei da quadra (RN-02/RN-03): quem está em quadra, a fila, as vitórias seguidas, os **reis na ordem em que viraram**, os **eliminados** (jogadores dos times que perderam) e o fim da fase de fila (um time sozinho sem adversário). Sem resultados é a situação inicial: os dois primeiros da fila em quadra, o resto na fila.

- **Gate de "Chamar partida":** precisa de dois times completos em quadra; se um deles for o **incompleto**, bloqueia com "escolha o parceiro" (US8). Também precisa de quadra vinculada disponível e de nenhuma partida chamada em aberto.
- **Tabela `partidas_rodada`** (schema 5): `id, rodada_id, ordem, time_a_id, time_b_id, estado (chamada|encerrada), quadra_id, chamada_em` e as colunas do resultado (`placar_a`, `placar_b`, `vencedor_time_id`, `encerrada_em`), que a US6 preenche. No máximo uma partida `chamada` por rodada (índice único parcial).

## Sincronia entre aparelhos (CA3)

- **WebSocket `/ws/gerenciador`**, com um hub próprio (não mistura com o das quadras). O segredo **não vai na URL**: o cliente manda `{"tipo": "AUTENTICAR", "segredo": …}` na primeira mensagem (prazo de 5 s; mesmo comparador de tempo constante e mesma limitação de tentativas do restante). Autenticado, recebe o estado completo e, depois, `ESTADO_ATUALIZADO` a cada mudança.
- **Quem publica:** toda ação do gerenciador que muda o estado (presença, ordem, cadastro rápido, inativar, sorteio, resortear, confirmar, descartar, cancelar, vínculo, chamar partida). O mesmo estado volta na resposta HTTP de quem agiu.
- **Cliente:** reaproveita o `criarConexao` do placar (reconexão com espera crescente, batimento de 20 s, descarte de mensagem fora de ordem). "Atualizar" e a atualização ao voltar a aba ficam como reserva. Resolve a limitação "sem sincronia automática" aceita na US2.

## API

- `PUT /api/sessao/quadra {codigo}` e `DELETE /api/sessao/quadra` (vincular/desvincular); a criação usa `POST /api/quadras`, que já existe.
- `POST /api/rodada/chamar-partida`.
- O estado da sessão ganha `quadra` (`codigo`, `nome`, `disponivel`) e, com rodada em andamento, `conducao` (`em_quadra`, `partida` chamada, `fila`, `reis`, `eliminados`, `pode_chamar`, `motivo`).
- Declarar a rota `/ws/gerenciador` **antes** de `/ws/{quadra_id}`.

## Tela (`/sessao`)

Novo `PainelConducao.svelte` no lugar da lista simples quando a rodada está em andamento: bloco da **quadra vinculada** (criar/vincular/trocar, estado), **Partida** (em quadra, ou "próxima partida" com **Chamar partida**), **Fila** numerada, **Reis** (com a ordem) e **Eliminados** (vazios com um texto claro até a US6). Mantém **Cancelar rodada**.

## Aceite (BDD)

- Given uma rodada em andamento e nenhuma quadra vinculada, Then o painel mostra "vincule uma quadra" e **Chamar partida** fica desabilitado com o motivo.
- Given "Criar quadra e vincular", Then existe uma quadra do placar, o vínculo fica gravado e o operador consegue abrir `/quadra/<código>` e operar como admin.
- Given quadra vinculada e dois times completos em quadra, When toco em **Chamar partida**, Then o placar dessa quadra mostra as duas duplas, o alvo da rodada e 0 × 0, para quem está com ela aberta, sem recarregar.
- Given a quadra com uma partida em andamento e pontos marcados, When chamo, Then é recusado e o placar fica como estava.
- Given o time incompleto entre os dois primeiros, Then **Chamar partida** fica bloqueado com "escolha o parceiro".
- Given a quadra expirada ou sumida, Then o vínculo aparece como indisponível e a chamada é recusada com a explicação.
- Given dois aparelhos na tela da sessão, When um sorteia, confirma ou chama a partida, Then o outro mostra a mudança em poucos segundos, sem atualizar.
- Given o servidor reiniciado, Then o vínculo, a rodada e a partida chamada continuam gravados (a quadra do placar, que é efêmera, pode precisar ser vinculada de novo).
- Given a tela dentro do APK, Then continua oculta.

## Testes

- `tests/test_conducao.py` (puro): situação inicial; sequências com resultado (vencedor fica, 2 vitórias → rei e entram os 2 próximos, perdedor elimina, fila esvazia, reis em ordem, eliminados em ordem); invariantes (todo time em exatamente um lugar); incompleto bloqueia.
- `tests/test_chamada.py` (API + placar real): vincular/desvincular; chamar carrega nomes, jogadores e alvo no estado da quadra; recusa com pontos; quadra expirada; sem vínculo; gate do incompleto; segunda chamada com a primeira em aberto; índice único.
- `tests/test_ws_gerenciador.py`: autenticação por mensagem (certa, errada, ausente, prazo), difusão ao mutar, dois clientes, reconexão recebe o estado atual.
- Playwright: criar quadra e vincular, chamar partida e ver o placar da quadra (segunda aba) atualizar; dois contextos sincronizando; axe do painel.
- `npm test` para os helpers de formatação e do cliente.

## Alternativas rejeitadas

- **Criar a quadra inteira no servidor:** ninguém seria admin humano; o controle do placar ficaria sem dono (a sucessão devolve o comando ao admin ausente).
- **Gerenciador como "jogador" comum da quadra:** não teria papel para configurar a partida.
- **Segredo na URL do WebSocket:** vazaria em logs e histórico.
- **Reutilizar o hub das quadras:** a rotina de sucessão percorre as salas ativas e trataria "gerenciador" como quadra.
- **Esperar a US6 para modelar o rei da quadra:** o painel (CA1) precisa do estado; fazer a derivação agora e plugar o resultado depois evita retrabalho.

## Fora do escopo

Registrar resultado e fazer a fila andar (US6); desfazer (US7); parceiro do incompleto (US8); atrasados (US9); substituição (US10); mata-mata (US11); nomes das duplas no relógio (US14) e tela do espectador (US13).

## Pontos para o Navigator confirmar

1. **Escopo do painel:** a derivação completa do rei da quadra entra agora, mas só com resultados reais a partir da US6 — até lá, "Reis" e "Eliminados" aparecem vazios. Aceita?
2. **Vínculo com a quadra do placar** (criar pela tela ou por código, o gerenciador age como o admin dela), em vez de criar a quadra só no servidor. Aceita?
3. **Nomes no placar** como "Ana + Gil" (primeiros nomes).
4. **Recusar chamar** se a quadra tem partida em andamento com pontos.
5. **Operar o gerenciador continua exigindo o `OWNER_SECRET`** (a RN-12, "qualquer dispositivo", fica entendida como "qualquer aparelho que conheça o segredo"). Aceita?
6. **Time incompleto na vez** bloqueia a chamada até a US8.

## Riscos

- **Quadra efêmera:** reinício do servidor ou 1 h parada apaga a quadra e quebra o vínculo; mitigado com o aviso "indisponível" e o botão de refazer, mas o operador precisa reabrir o placar. (O banco efêmero é decisão do Navigator, mantida.)
- **Duas fontes de verdade durante a partida** (o placar da quadra e a partida chamada no gerenciador); a US6 as reconcilia ao registrar o resultado lendo o placar.
- **Tamanho:** é grande. Se crescer, separo a sincronia por WebSocket numa Technical Story à parte, antes do painel.
