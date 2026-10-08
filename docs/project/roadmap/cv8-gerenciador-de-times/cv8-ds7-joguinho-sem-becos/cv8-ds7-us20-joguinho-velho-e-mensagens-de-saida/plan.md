# Plano — CV8.DS7.US20 Joguinho de ontem e mensagens que ensinam a saída

Branch: `fix/cv8-ds7-us20-joguinho-velho-e-saidas` · Versão alvo: **0.47.0** (minor: ação nova "cancelar rodada e encerrar" na API e aviso novo na tela)

## O que a US16–US19 já resolveram e o que falta

Já feito: "vincule de novo" não aparece mais com partida chamada (US16), "Anular partida" existe, o motivo de "Encerrar partida" e de "Chamar partida" aparece logo abaixo dos botões, e a confirmação de "Cancelar rodada" já avisa das partidas registradas.

Falta (QA F1.5, F4, F5.1, F5.3):

1. **Joguinho aberto em dia anterior não é sinalizado** (`sessoes.aberta_em` existe, a tela não o usa).
2. **"Encerrar sessão" com rodada ativa** só mostra "Descarte a proposta ou cancele a rodada…": ensina a saída destrutiva sem dizer o que se perde nem oferecê-la ali. O botão fica desabilitado.
3. **"Cancelar rodada"** resume só as partidas; não fala de fila, reis nem de partida chamada.
4. **Presença travada** (botões "Desmarcar", ↑ ↓, ⠿, "Presente" desabilitados): o motivo fica no fim da página, longe dos botões.
5. **Resortear desabilitado** (proposta com uma única combinação) sem dizer por quê.

## Desenho

1. **Aviso de joguinho velho** (cliente, `Sessao.svelte`): se `sessao.aberta_em` cai num dia anterior ao de hoje **no fuso do aparelho**, aparece um cartão no topo: "Joguinho aberto em 07/10 (ontem)" com **Continuar este joguinho** e **Encerrar joguinho**. "Continuar" esconde o aviso daquela sessão (guardado em `localStorage` por id da sessão; se o storage falhar, o aviso só volta ao recarregar). "Encerrar joguinho" abre a confirmação do item 2. Regra pura em `web/src/lib/` com teste (hoje, ontem, N dias atrás, virada de mês).
2. **Encerrar com rodada ativa vira uma ação, não um beco.** O botão "Encerrar joguinho" fica sempre habilitado. Com rodada ativa a confirmação diz o que se perde (rodada N; proposta, ou fila/reis/partidas registradas/partida chamada) e o botão passa a ser **Cancelar rodada e encerrar**.
   - **Servidor:** `POST /api/sessao/encerrar` aceita corpo opcional `{"cancelar_rodada": true}`. Na **mesma transação** cancela a rodada (`em_andamento` → `cancelar`; `proposta` → `descartar`) e fecha a sessão; ou tudo, ou nada. Sem a flag, o comportamento e o 409 de hoje continuam (compatível com o MCP e testes).
3. **Confirmação de "Cancelar rodada" completa:** passa a resumir fila (times aguardando), reis, partidas registradas e a partida chamada, se houver, e diz que a quadra do placar não é tocada.
4. **Motivo junto do botão:** o aviso de presença travada sobe para o topo de "Presentes", com a ação ali ("Cancelar rodada" fica no painel acima, então o texto aponta para ele). O "Resortear" desabilitado ganha a linha "Só há uma combinação possível com esses presentes."
5. **Nada de texto novo longe do botão:** revisão final de todos os `disabled` do Joguinho; o que sobrar sem motivo próximo entra neste plano antes de implementar.

### Pergunta para o Navigator (item "Esperado" da história)

O texto da história inclui "ao detectar quadra indisponível, **recriar a quadra com as mesmas duplas**, ou anular a chamada". Recomendo **não** construir a recriação agora: depois de **Anular partida** os mesmos dois times voltam a ser a próxima partida, então **Criar quadra e vincular → Chamar partida** já recria a quadra com as mesmas duplas (dois toques, sem tela nova), e a decisão B (2026-10-08) escolheu reconciliar + anular. Se preferir um botão "Anular e criar nova quadra" num só passo, vira uma história própria. Confirma?

### Alternativas descartadas

- **Dois chamados do cliente (cancelar, depois encerrar):** se o segundo falha, a rodada fica cancelada e a sessão aberta; por isso a ação atômica no servidor.
- **Expirar o joguinho velho sozinho no servidor:** apagaria trabalho sem o dono saber; o aviso com escolha é o pedido.
- **Fuso do servidor para "outro dia":** o jogo é de quem está na quadra; vale o dia do aparelho.

## Escopo

- `app/sessao.py`: `encerrar_sync(cancelar_rodada)`; `app/rodada.py` sem mudança de regra (reusa `cancelar`/`descartar`).
- `web/src/lib/` (regra do "joguinho velho"), `Sessao.svelte`, `PainelConducao.svelte`, `PainelRodada.svelte`.
- Testes: pytest (encerrar sem flag mantém o 409; com flag cancela e fecha, com proposta, com rodada em andamento e com partida chamada; atomicidade), unitários da regra do dia, e2e (aviso de ontem com as duas escolhas; encerrar com rodada ativa; resumo do cancelamento).
- Docs: CHANGELOG 0.47.0, roadmap, worklog, guia (corpo opcional do `/encerrar`).

## Fora do escopo

US19 (retirar jogador), US21 (placar manual/W.O.), recriar quadra em um passo, expirar sessão no servidor, mexer em permissões (F5.2).

## Aceite (BDD)

- **Dado** um joguinho aberto em dia anterior **quando** abro a tela **então** vejo "Joguinho aberto em <data>" com continuar ou encerrar.
- **Dado** "Encerrar joguinho" com rodada ativa **então** a confirmação diz o que se perde e oferece "Cancelar rodada e encerrar", que faz as duas coisas de uma vez.
- **Dado** "Cancelar rodada" **então** a confirmação resume partidas, reis, fila e partida chamada.
- **Dado** qualquer botão desabilitado no Joguinho **então** o motivo aparece junto dele.

## Riscos

- Muda a API (corpo opcional): compatível, mas o MCP/scripts que chamam `/encerrar` sem corpo seguem iguais.
- O aviso depende do relógio do aparelho; relógio errado dá aviso errado (inofensivo: "Continuar" resolve).
