# Plano — CV3.DS1.US2 Ver o placar e marcar pontos no pulso

Branch: `feature/cv3-ds1-us2-ver-e-marcar`, criada da `master` em `bc32dec` (0.7.0).

## Histórico do plano
- **Revisões 1–2 (Checkpoint 1 aprovado em 2026-09-23):** o relógio era um dispositivo do mesmo participante `eli`, a habilitação era pelo apelido-senha `eli.relogio` e havia uma chave de sala, "Controlar pelo Relógio". Implementadas até o Checkpoint 2 (`3eccfae`…`fe45cf8`). O texto da revisão 2 está no histórico do Git deste arquivo.
- **Revisão 3 (Navigator, 2026-09-23, no teste físico):** o Navigator redirecionou o desenho:
  - `eli` em qualquer caixa já habilita o relógio e é gravado como `Eli`;
  - o relógio vincula um **participante próprio, "Eli (Relógio)"**, que recebe o controle por delegação;
  - a chave "Controlar pelo Relógio" sai.

  Escolhas do Navigator nesta revisão:
  - pontuar já nesta HU, por delegação;
  - o controle nas mãos do relógio **não** é devolvido por ausência (o admin retoma com "Assumir o controle");
  - a normalização para Title vale só para `eli` → `Eli`;
  - o relógio conectado conta como presença do dono para a sucessão de admin.

A revisão 3 substitui a decisão `apelido-senha-habilita-relogio` e a decisão 1 do plano da DS1 ("relógio como dispositivo de Eli, sem participante duplicado").

## Escopo (revisão 3)

### Habilitação
1. `eli`, `ELI` e `Eli` (espaços nas pontas ignorados) entram gravados como **`Eli`** e recebem `watch_grants`. A lista vem de `WATCH_AUTO_GRANT` (padrão `eli`). O apelido-senha `eli.relogio` deixa de existir.
2. No site, o ícone do relógio abre o vínculo só para `eli`, em qualquer caixa. Os demais veem "Em breve…".

### Relógio como participante próprio
3. Ao aprovar o código, o servidor cria na sala o participante **"Eli (Relógio)"** (`<apelido do dono> (Relógio)`), com papel ESPECTADOR. A credencial do relógio passa a agir como esse participante, e `watch_devices.owner_id` guarda o dono (o `Eli` do telefone).
4. Revincular reaproveita o mesmo participante, com o mesmo papel e o mesmo controle. Revogar pelo telefone ou desabilitar pelo owner remove o participante. Se ele estava no controle, o controle volta ao dono.
5. A habilitação continua sendo do dono. O relógio vê a sala enquanto o dono estiver habilitado, qualquer que seja o papel do "Eli (Relógio)".

### Delegação e pontuação
6. O admin usa os botões que já existem: **promove** "Eli (Relógio)" a controlador e **passa o controle** para ele. Quem tem o controle pontua, como hoje no site. Com o controle no relógio, o site não mostra +1/Desfazer para ninguém, e o admin pode **Assumir o controle** a qualquer momento.
7. `POST /api/watch/comandos` mantém o recibo durável (tabela `watch_recibos`), a fila, a idempotência e o registro das recusas da revisão 2. A base do lance é `partida_id` + `controle_versao`: qualquer troca de controle invalida os lances pendentes.
8. **Ausência:** um controle nas mãos de um relógio não é devolvido ao admin por ausência, porque a tela apaga durante o jogo.
9. **Sucessão de admin:** o dono conta como presente enquanto o relógio dele estiver conectado ou tiver sido visto dentro da janela.

### Removido da revisão 2
A chave "Controlar pelo Relógio": `controle_relogio`, `relogio_versao`, `/controle/relogio`, `ChaveRelogio.svelte` e o evento `CONTROLE_RELOGIO_ALTERADO`. A delegação cumpre o mesmo papel.

### Relógio (Wear OS), mantido da revisão 2
- tela com Nós/Eles ou iniciais;
- fila durável;
- placar previsto separado do confirmado;
- envio FIFO;
- recusa com descarte confirmado;
- nenhum toque com a tela apagada;
- bloqueio na vitória prevista.

Enquanto o controle não estiver com o relógio, os botões ficam travados e a tela mostra "Controle no telefone. Peça ao admin para passar o controle.".

## Aceitação (revisão 3)
- **Dado** `ELI` ao criar a sala, **então** a sala mostra `Eli` e o ícone do relógio abre o vínculo. Com `Rafa`, aparece "Em breve…".
- **Dado** o código aprovado, **então** a lista de presentes mostra **Eli (Relógio)** como espectador, online com o app aberto. O relógio mostra o placar com os botões travados.
- **Quando** o admin promove "Eli (Relógio)" e passa o controle para ele, **então** o site mostra "Controle: Eli (Relógio)" sem +1/Desfazer, e o relógio libera os botões.
- **Dado** A, A, B no pulso, **então** todas as telas mostram 2×1, com três pontos de autor "Eli (Relógio)" e recibos `APLICADO`.
- **Dada** a tela do relógio apagada por mais de 15 s, **então** o controle continua com "Eli (Relógio)".
- **Dado** o telefone do Eli bloqueado por mais de 2 min com o relógio conectado, **então** o admin não é sucedido.
- **Quando** o admin toca "Assumir o controle", **então** o relógio trava, e os lances pendentes são recusados e aparecem para descarte.
- **Quando** o relógio é revogado, **então** "Eli (Relógio)" sai da lista e o controle volta ao Eli.
- Continuam valendo:
  - reenvio sem duplicar ponto;
  - 409 para `id` repetido com conteúdo diferente;
  - ordem dos toques rápidos preservada;
  - lance de partida anterior recusado;
  - partida encerrada bloqueada;
  - fila que sobrevive ao reinício do app.

## Fora de escopo
- desfazer pelo relógio (US3);
- envio em segundo plano e reconciliação (US4);
- inversão de lados, tiles e tela sempre ligada;
- relógio para outras pessoas.

## Versão
`0.8.0`. O deploy apaga as salas: a versão muda e o contêiner não tem volume.

## Riscos
1. `eli` passa a ser público. Numa sala sem o Eli, qualquer pessoa que entre como `eli` pode vincular um relógio. O impacto fica limitado à sala que essa pessoa mesma controla.
2. Se o `.env` do Mini PC define `WATCH_AUTO_GRANT=eli.relogio`, é preciso trocar para `eli` ou remover a linha.
3. Para receber o controle, o "Eli (Relógio)" precisa estar online (regra existente): o app do relógio tem que estar aberto na hora.
