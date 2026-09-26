---
code: CV4.DS2.US3
level: User Story
status: Active
status_reason: decisões de produto confirmadas; plano aguardando Checkpoint 1
updated: 2026-09-26
effort: 9
---

# CV4.DS2.US3 — Temas de placar escolhidos pelo administrador

## Intenção

Permitir que o administrador escolha entre os temas visuais **Esportivo** e **Clássico** nas configurações da partida. A escolha pertence à sala, vale para administradores, controladores e espectadores, persiste entre partidas e chega imediatamente a todos os clientes conectados. Claro/escuro continua sendo uma preferência independente de cada dispositivo.

**Esforço estimado:** 9/10. A mudança atravessa banco, contrato HTTP, snapshot, WebSocket, configurações e as composições de operação e acompanhamento.

## Decisões confirmadas pelo Navigator

- Os nomes exibidos serão **Esportivo** e **Clássico**.
- O administrador é o único papel autorizado a escolher o tema.
- A escolha vale para todos os participantes da sala.
- A troca pode ocorrer durante uma partida e deve aparecer imediatamente nos clientes conectados.
- A escolha fica persistida no servidor e continua válida em novas partidas da mesma sala.
- Tema de placar e aparência claro/escuro são eixos independentes.
- Os dois temas precisam atender também administrador e controlador, preservando comandos e permissões.
- O indicador **Ao vivo** terá a mesma altura externa dos demais controles do cabeçalho.

## Comportamento de aceite

- **Given** uma sala nova ou migrada, **When** ninguém alterou o tema, **Then** o placar usa `Esportivo` por padrão.
- **Given** administrador nas configurações, **When** escolhe `Clássico` e salva, **Then** todos os clientes conectados mudam sem recarregar e a sala continua clássica após nova partida ou reconexão.
- **Given** administrador troca de `Clássico` para `Esportivo`, **When** o snapshot chega, **Then** espectadores e operadores veem o mesmo resultado, nomes, cores e lados no novo tema.
- **Given** controlador ou espectador, **When** usa a sala, **Then** não recebe ação para mudar o tema e uma chamada indevida ao servidor é recusada.
- **Given** qualquer tema visual, **When** claro/escuro muda localmente, **Then** o tema do placar permanece e somente os tokens de aparência do dispositivo mudam.
- **Given** administrador ou controlador com posse do controle, **When** marca ou desfaz, **Then** os mesmos comandos, fila, feedback e permissões funcionam nos dois temas.
- **Given** cabeçalho visível, **When** os controles são comparados, **Then** `Ao vivo` tem a mesma altura de tema, compartilhar, inverter lados e orientação.

## Entregas e esforço

### 1. Contrato persistente da sala — esforço 8/10

- Adicionar `tema_placar` à tabela `quadras`, com `esportivo` como valor padrão.
- Migrar bancos existentes por `ALTER TABLE`, sem alterar a versão técnica que hoje recria o banco.
- Incluir o campo em criação, leitura pública, leitura autenticada, listagens e snapshots.
- Validar no servidor somente `esportivo` ou `classico`.
- Manter a escolha ao reiniciar a partida, pois ela pertence à sala.

### 2. Autorização e sincronização em tempo real — esforço 8/10

- Estender a configuração administrativa para aceitar `tema_placar`.
- Atualizar a sala dentro da mesma transação protegida pelo lock existente.
- Aceitar troca isolada de tema, mesmo quando regras e duplas não mudarem.
- Reutilizar o snapshot e broadcast vigentes para atualizar todos os clientes.
- Testar recusa para não administradores, reconexão e persistência.

### 3. Seletor nas configurações — esforço 5/10

- Criar a seção **Visual do placar** no modal administrativo.
- Mostrar duas opções selecionáveis, com nome e descrição curta: leitura ampla para `Esportivo` e cartões de mesa para `Clássico`.
- Preencher pelo valor atual da sala e enviar junto ao salvamento.
- Não misturar essa seleção com o botão claro/escuro.
- Manter o seletor fora das superfícies de controlador e espectador.

### 4. Representações reutilizáveis — esforço 9/10

- Preservar `PlacarResultado.svelte` como representação esportiva comum.
- Extrair ou recuperar a representação clássica baseada em `CartaoDobravel`, sem copiar regras, transporte ou permissões.
- Fazer espectador, administrador e controlador escolherem a representação pelo mesmo `quadra.tema_placar`.
- Manter contexto, vitória, inversão e nomes coerentes nos dois temas.
- Evitar duplicar o estado da partida durante a troca; somente a representação visual muda.

### 5. Operação nos dois temas — esforço 9/10

- Separar a representação dos comandos atuais de `Placar.svelte`.
- Preservar `+1`, desfazer, nova partida, regras, compartilhamento, linha do tempo, fila de toques e feedback.
- No tema Esportivo, integrar ações ao painel moderno sem reduzir a prioridade dos pontos.
- No tema Clássico, manter os cartões e proporções conhecidas.
- Confirmar que inversão local altera posição visual, sem trocar a equipe enviada ao servidor.

### 6. Cabeçalho e indicador Ao vivo — esforço 2/10

- Aplicar a mesma altura mínima e o mesmo modelo de caixa dos demais controles ao `.ws-status`.
- Conferir claro/escuro, texto `Conectando...` e cabeçalho estreito.

### 7. Testes e validação — esforço 8/10

- Backend: migração, valor padrão, validação, autorização, persistência e broadcast.
- Frontend: seletor, roteamento das duas representações, operação e independência de claro/escuro.
- Regressão: testes completos do backend e frontend, Svelte, build e Ruff.
- Visual: administrador, controlador e espectador nos dois temas; claro/escuro; tela estreita e larga; troca durante uma partida.

## Detalhes técnicos previstos

- **Banco:** `app/db.py`, coluna `quadras.tema_placar TEXT NOT NULL DEFAULT 'esportivo'` e migração aditiva.
- **Sala e snapshots:** `app/quadras.py` e funções de snapshot em `app/comandos.py`.
- **API:** `ConfigurarPartidaBody` em `app/api.py`; o servidor continua sendo a autoridade da permissão.
- **Tempo real:** a resposta da configuração já passa por `aplicarSnapshot` e pelo broadcast `PLACAR_ATUALIZADO`; o campo da quadra seguirá esse caminho.
- **Configuração:** `web/src/components/ModalConfigurarPartida.svelte` receberá a quadra ou o tema atual além do estado esportivo.
- **Composição:** `SalaQuadra.svelte`, `Placar.svelte`, `PlacarManual.svelte`, `PlacarResultado.svelte` e um componente clássico puro se a extração se confirmar.
- **Contrato do frontend:** `App.svelte` continuará aplicando snapshots completos; não haverá armazenamento local para o tema visual da sala.

## Riscos e mitigação

- **Duplicação entre papéis:** extrair representações visuais e manter comandos numa composição única de operação.
- **Troca apagar estado:** o tema fica na sala e nunca recria partida ou componente de estado; pontos vêm do snapshot vigente.
- **Banco existente:** migração aditiva e teste específico, sem elevar `settings.version`.
- **Tema inválido:** enumeração no corpo da API e validação no domínio antes da escrita.
- **Cliente antigo:** ausência do campo deve cair em `esportivo`, mantendo a experiência atual.
- **Modal muito alto no Fold fechado:** opções compactas, rolagem do diálogo preservada e teste com teclado virtual.

## Fora do escopo

- Fullscreen real e mudanças nos timers de imersão (`CV4.DS2.US2`).
- Novos temas além de Esportivo e Clássico.
- Escolha individual de tema visual por participante.
- Alterar política de controle, regras de pontuação, protocolo do relógio ou tema claro/escuro.
- Redesenhar todas as superfícies auxiliares.

## Validação do Navigator

1. Criar sala e confirmar `Esportivo` como padrão.
2. Entrar com administrador e espectador em sessões distintas.
3. Marcar pontos, abrir configurações, escolher `Clássico` e salvar.
4. Confirmar troca imediata nas duas sessões sem mudança do resultado.
5. Repetir como controlador, marcar e desfazer nos dois temas.
6. Alternar claro/escuro em apenas um dispositivo e confirmar que o visual escolhido para a sala permanece.
7. Reiniciar partida e reconectar; confirmar persistência.
8. Conferir alinhamento e altura do indicador `Ao vivo`.

**Aprova:** todos recebem a escolha administrativa, a partida não perde estado, controles funcionam nos dois temas e claro/escuro permanece local.

**Falha:** cliente precisa recarregar, papel não autorizado altera tema, troca recria partida, estilos divergem entre papéis ou ações deixam de funcionar em uma representação.

## Estado para retomada

- Branch: `feature/cv4-ds2-us3-temas-placar`, baseada em `origin/master` `842d5c7`.
- Passo Ariad: Passo 2 — Planejamento.
- Último checkpoint aprovado: nenhum.
- Próxima ação: obter aprovação do Checkpoint 1; depois implementar até o Checkpoint 2.
