# Plano — CV3.DS1.US5 Um vínculo por vez: retomar ou trocar de quadra

Branch: `feature/cv3-ds1-us5-um-vinculo-por-vez`, criada da `master` em `b520f32` (0.9.0).

Nível: User Story. Versão pretendida: `0.10.0` (minor, nova capacidade no relógio: trocar de quadra sem o telefone revogar antes).

## Escopo

### Servidor
1. `POST /api/watch/pairing` aceita um corpo opcional `{"substitui": "<token atual>"}`. O relógio gera um token novo para o código e informa o token do vínculo que ele substitui. O servidor guarda só a referência (`watch_devices.substitui_id`, migração aditiva), nunca o token. Um `substitui` inválido ou já revogado é ignorado: o código novo vale como um vínculo do zero.
2. **Ao aprovar** o código (`POST /api/quadras/{court}/watch/approve`), na mesma transação: o vínculo substituído é revogado e, se era de outra quadra ou de outro participante, o "Eli (Relógio)" sai daquela quadra pelo mesmo caminho da revogação pelo telefone (`remove_watch_participant`). Se o relógio estava com o controle, o controle volta ao dono e a linha do tempo da quadra antiga registra "Controle devolvido para Eli: relógio foi para outra quadra" (motivo `relogio_trocou_de_quadra`).
3. Depois da transação: os sockets do vínculo antigo são fechados (4401) e a quadra antiga recebe o estado novo. O token antigo passa a receber 401.
4. `DELETE /api/watch/pairing` (Bearer do token novo) cancela um código ainda não aprovado. Idempotente. Se o código já tinha sido aprovado, responde 409 e o relógio adota o vínculo novo (é o que o servidor já fez).
5. Revincular na **mesma** quadra continua reaproveitando o participante "Eli (Relógio)" com papel e controle, como hoje.

### Relógio
6. **Tela de abertura.** Ao abrir o app (atividade criada de novo: primeiro toque no ícone ou depois de fechado com o gesto de voltar), com vínculo guardado:
   - vínculo confirmado pelo servidor: **"Retornar à quadra 48291"** e **"Gerar novo código"**;
   - sem rede: os mesmos dois botões, com o número da quadra guardado no aparelho e a indicação "sem conexão" (gerar código fica desabilitado até a rede voltar);
   - vínculo inválido (401: sala expirada, revogação): só **"Gerar código"**, como hoje.
   A tela de abertura **não** aparece quando a tela do relógio só apagou e acendeu no meio do jogo.
7. Presença (WebSocket) e envio da fila só começam depois de "Retornar".
8. **Gerar novo código com lances pendentes:** antes de gerar, uma confirmação: "3 lances da quadra 48291 ainda não foram enviados. Se o novo código for aprovado, eles serão abandonados." → **Gerar mesmo assim** / **Voltar**. Sem pendentes, gera direto.
9. **Enquanto o código novo espera aprovação:** o relógio mostra o código e **"Voltar à quadra 48291"**. O vínculo antigo continua valendo (token e fila intactos no aparelho).
10. **Aprovado:** o relógio troca o token, descarta a fila da quadra antiga (já confirmada no passo 8), guarda o número da quadra nova e entra no placar dela.
11. **Desistir ("Voltar à quadra"):** o relógio cancela o código no servidor (item 4) e volta ao placar da quadra antiga. Sem rede, o cancelamento fica marcado e é refeito quando a conexão voltar; o código expira em 5 minutos de qualquer forma.
12. `CredentialStore` passa a guardar, além do token ativo, o token do código pendente e o número da última quadra. Mesma cifra (AES-GCM / Keystore).

### Ajustes do primeiro teste físico (Navigator, 2026-09-23)
13. Todas as telas de vínculo seguem o desenho do placar: conteúdo no centro do mostrador e a ação na faixa inferior inteira (a mesma do desfazer).
14. Sem vínculo: só uma bola de vôlei quicando e a faixa **Ingressar numa quadra**, sem título nem "Vínculo não encontrado".
15. Código na tela: dica útil ("No telefone, toque no ícone do relógio, ao lado da engrenagem, e digite o código.") e a faixa **Gerar novo código**.
16. Abertura: **Retornar** (com o número da quadra) no centro e a faixa **Parear outra quadra**; a confirmação usa **Parear mesmo assim**.

## Aceitação
- **Dado** o relógio vinculado à quadra A com a sala ativa, **quando** reabrir o app, **então** vê "Retornar à quadra A" e "Gerar novo código"; "Retornar" leva ao placar de A.
- **Quando** aprovar um código novo na quadra B, **então** a quadra A deixa de listar "Eli (Relógio)", o controle de A volta ao dono (com o registro na linha do tempo, se o relógio estava no controle), e o token antigo recebe 401.
- **Dado** um código novo gerado e não aprovado, **quando** tocar "Voltar à quadra A", **então** o relógio volta ao placar de A, o vínculo com A continua valendo, e o código cancelado é recusado se alguém tentar aprová-lo.
- **Dados** lances pendentes da quadra A, **quando** tocar "Gerar novo código", **então** o relógio avisa quantos lances serão abandonados e pede confirmação; nada é descartado em silêncio, e nada é descartado se o código não for aprovado.
- **Dada** uma sala expirada ou vínculo revogado, **quando** abrir o app, **então** só aparece "Gerar código".
- **Dado** o relógio no meio do jogo, **quando** a tela apagar e acender, **então** o placar volta direto, sem a tela de abertura.
- Chamada forjada: aprovar código com `substitui` de um token alheio inexistente não revoga nada; cancelar código já aprovado não desfaz a aprovação.

## Decisões de desenho

- **Token novo para o código novo, com referência ao antigo.** Reaproveitar o token atual obrigaria a desligar o vínculo antigo já ao gerar o código, e "desistir" deixaria o relógio sem vínculo. Com dois tokens, o antigo só morre na aprovação.
- **O relógio prova a posse do vínculo antigo enviando o token dele.** O servidor não tem como saber que o código novo vem do mesmo aparelho de outra forma. Só o hash é consultado; o token não é gravado.
- **Revogação na transação da aprovação, sem pegar o lock da quadra antiga.** O SQLite (`BEGIN IMMEDIATE`) já serializa as escritas; um lance do vínculo antigo que chegue depois recebe 401. Pegar os dois locks abriria risco de deadlock entre duas trocas cruzadas.
- **Cancelamento explícito no servidor ao desistir.** Sem ele, alguém poderia aprovar o código abandonado nos 5 minutos seguintes e derrubar o vínculo antigo. Se a aprovação ganhar a corrida, o relógio adota o vínculo novo em vez de ficar sem nenhum.
- **Lances descartados na aprovação, não na geração.** Enquanto o código não é aprovado, a fila de A ainda pode ser enviada ao voltar para A.
- **Rejeitado: tela de abertura a cada vez que a tela acende.** Atrapalharia o jogo; o pedido é para quando o app é reaberto.
- **Rejeitado: trocar de quadra no meio do placar (menu no relógio).** Não foi pedido; a saída é fechar e reabrir o app.

## Fora de escopo
- Envio em segundo plano e reconciliação da fila (US4). Sem rede, "Retornar" leva ao placar como hoje (sem placar guardado no aparelho).
- Mostrar o placar no aparelho sem rede ao reabrir o app.
- Vários relógios por pessoa, relógio de outras pessoas.
- Mudanças no site: a quadra antiga só vê o relógio sair, pelo caminho que já existe.

## Validação

### Automatizada
- `pytest`: troca de quadra com e sem controle (evento na quadra antiga, 401 do token antigo, participante removido), revínculo na mesma quadra, `substitui` inválido, cancelamento (antes e depois da aprovação), código cancelado não aprovável, migração aditiva de `substitui_id`, descrição da linha do tempo.
- `ruff check`, `ruff format --check`; web `npm test`, `npm run check`, `npm run build` (sem mudança esperada).
- Android: testes da decisão da tela de abertura e do texto de abandono (lógica pura, fora do Compose), `assembleDebug`, `lintDebug`.

### Navigator (Watch real, dois telefones, duas salas)
Roteiro detalhado em `test-guide.md`, a escrever no Passo 4. Resumo: vincular em A e passar o controle; fechar e reabrir o app (ver a escolha); gerar código e desistir (continua em A, código recusado se digitado no telefone B); marcar sem rede para criar pendentes, gerar código (ver o aviso), aprovar em B; conferir A (sem relógio, controle com o dono, registro na linha do tempo) e B (relógio presente); apagar e acender a tela no meio do jogo (sem tela de abertura).

## Riscos
- O que conta como "abrir o app" no Wear OS: o plano usa a criação da atividade. Se o sistema matar o app em segundo plano, a tela de abertura aparece ao voltar, o que é aceitável.
- Deploy da 0.10.0 recria o contêiner e apaga as salas (sem volume persistente, dívida já registrada).
