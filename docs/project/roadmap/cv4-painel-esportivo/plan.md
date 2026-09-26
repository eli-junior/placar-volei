---
code: CV4
level: Value
status: Planned
status_reason: plano elaborado a pedido do Navigator; implementação depende de Checkpoint 1
updated: 2026-09-26
baseline: ab2cedb
planning_branch: codex/plano-cv4-painel-esportivo
---

# Plano de ação — Painel esportivo, responsividade e leitura do placar

## 1. Estado, objetivo e autorização

**Objetivo:** transformar a experiência web em um painel esportivo moderno, com pontos dominantes, começando pela Home. Cada entrega deve produzir um resultado verificável e poder ser retomada por outro agente.

**Estado:** somente planejamento e referências documentais. Nenhum código da aplicação alterado neste ciclo. Direção visual aprovada; este plano e a implementação ainda aguardam Checkpoint 1. Não interpretar “perfeito” e “ótimo” sobre as prévias como liberação para implementar ou publicar.

**Base inspecionada:** `origin/master` em `ab2cedb`, de 2026-09-26. README e changelog anunciam 0.11.0; briefing e versões web/backend ainda indicam 0.10.1. Registrar a divergência na coerência da primeira entrega, sem mudar a prioridade do CV3 nem versões do relógio automaticamente.

**Branch deste planejamento:** `codex/plano-cv4-painel-esportivo`. O código de cada US/TS será desenvolvido em branch própria nascida da `master` atualizada, depois que as dependências necessárias estiverem aceitas e integradas.

**Documentos complementares:** [handoff](handoff.md), [validação](test-guide.md), [decisão visual](../../decisions/records/2026-09-26T1238Z-painel-esportivo-e-numeros-prioritarios.md), [referências](references/README.md).

## 2. O que já foi decidido com o Navigator

1. Painel esportivo contemporâneo como direção visual.
2. Placar como elemento dominante; nome da quadra, código e regras menores.
3. Fonte **Teko**, já existente no projeto, com peso 600 e números maiores que na primeira proposta. Manter o reconhecimento visual de um placar esportivo.
4. Temas claro e escuro aprovados na mesma composição.
5. Começar pela tela inicial; evoluir para acompanhamento e operação.
6. Uso variável: Fold fechado ou aberto, na mão ou apoiado; tablet também exibe o placar. Não assumir um único modo de uso pelo tipo de aparelho.
7. Manter ocultação automática dos controles no acompanhamento. Acrescentar solicitação real de tela cheia quando suportada.
8. Computador deve funcionar bem, mas sua finalidade relatada é inspecionar o desenvolvimento.

**Propostas técnicas deste plano, ainda sujeitas ao aceite:** componente visual compartilhado entre papéis; controles revelados sobre o placar; entrada por código como aba inicial; testes de navegador como dependência apenas de desenvolvimento; organização de ações secundárias e janelas. Não criar novos papéis ou mudar quem pode marcar pontos.

## 3. Diagnóstico e correspondência com as entregas

| Achado | Evidência na base | Consequência | Entrega |
|---|---|---|---|
| Home não aproveita tela larga | `app.css`: `#app` limitado a 540 px; `HomePlacar.svelte`: 480 px e layout de 2 colunas só a partir de 960 px | O filho pode declarar 1060 px e continuar contido pelo pai | E1 |
| Ações cortadas no Fold fechado | Cabeçalho da sala em flex, ações sem adaptação suficiente; imagens mostram corte à direita | Esconder overflow remove a rolagem, mas não torna o botão acessível | E2/E4 |
| Pontos aparecem tarde na tela normal | Código, perfil, regras e controle em blocos antes do placar | O resultado fica abaixo da primeira área visível | E2/E4 |
| Escala irregular entre Fold aberto, fechado e paisagem | `PlacarManual.svelte` usa largura/altura da janela, proporções de cartões e dimensões de moldura fixas | Vazios grandes ou placas grandes com pouco ganho de leitura | E2 |
| Interfaces distintas por papel | `SalaQuadra.svelte` escolhe `Placar` ou `PlacarManual` a partir de `podeControlar` | Diferença de captura não é só responsividade; testar todos os papéis | E2/E4 |
| Imersão altera o fluxo | Cabeçalho e seções entram/saem com transições, timer de 3 s | Potencial deslocamento do placar e dificuldade de concluir ações | E3 |
| Tela cheia real não implementada | Busca em `web/src` e `web/public` não encontrou `requestFullscreen` | Recolher a interface não remove as barras do navegador | E3 |
| Medição incompleta da área visível | Há listener de `visualViewport.resize`, mas leitura de `innerWidth/innerHeight` | Teclado, barras, zoom e abertura do Fold exigem reprodução específica | E2/E3 |
| Cores/ações inconsistentes | Repetição de inverter lados, compartilhar e configurar; mistura de emojis, formatos e efeitos | Competição de atenção e caminhos redundantes | E1/E4/E5 |
| Contraste sem verificação em execução | Dívida existente de contraste; dica com opacidade animada e cores fixas | Inspeção de captura não prova acessibilidade | E1–E6 |
| Promessas anteriores diferentes do código atual | CV2.DS3 cita ausência de overflow, container queries e axe; código e dívida não comprovam tudo isso | Revalidar capacidades; não declarar dívida quitada por texto histórico | E6 |

As observações visuais vieram das capturas do Navigator. Não houve teste físico ou auditoria completa de browser nesta etapa. A hipótese de altura/escala precisa de medidas reais; não tratar pixels das imagens como pixels CSS.

## 4. Escala de esforço e sequência

Esforço **1–10** estima implementação, integração, testes e documentação. Não corresponde a dias nem deve ser somado como prazo. Reavaliar depois da inspeção da base de cada entrega.

- **1–2:** ajuste localizado com risco baixo.
- **3–4:** poucos componentes, comportamento conhecido e validação delimitada.
- **5–6:** vários estados/tamanhos ou integração transversal moderada.
- **7–8:** múltiplos papéis, ciclos de vida e dependências de navegador/aparelho.
- **9–10:** grande incerteza ou mudança estrutural de alto risco; dividir antes de executar.

| Ordem | História | Entrega verificável | Esforço | Dependências | Razão principal |
|---|---|---|---:|---|---|
| E1 | CV4.DS1.US1 | Home esportiva e entrada responsiva | **6/10** | Conferir correção concorrente da Home | Largura do app, formulário, estados de erro, temas e testes iniciais |
| E2 | CV4.DS2.US1 | Placar do espectador legível em todas as telas | **7/10** | E1 | Escala por espaço disponível, nomes/3 dígitos, Fold e animação |
| E3 | CV4.DS2.US2 | Imersão estável e tela cheia real | **8/10** | E2 | Gesto do usuário, eventos do navegador, modais e foco |
| E4 | CV4.DS3.US1 | Admin e controlador com operação confortável | **7/10** | E2; sequência preferida após E3 | Permissões, transferência de controle, comandos em fila e ergonomia |
| E5 | CV4.DS3.US2 | Ações auxiliares e estados consistentes | **5/10** | E3 e E4 | Diálogos, teclado virtual, presença, erros e fim da partida |
| E6 | CV4.DS3.TS1 | Regressão, acessibilidade e consolidação da entrega | **6/10** | E1–E5 | Evidência em navegador e aparelhos; dívida e coerência documental |

Cada entrega só segue para a próxima após seu aceite e integração autorizada. Testes começam em E1 e crescem a cada US; E6 consolida a cobertura, não adia qualidade para o fim.

## 5. Arquitetura e regras transversais propostas

### Layout e componentes

- Manter Svelte 5, FastAPI, WebSocket e o motor de comandos/eventos existente.
- Separar o limite da Home, o layout da sala e o palco do placar. Evitar remover o limite global de 540 px sem revisar os demais consumidores.
- Usar grid/flex com `minmax(0, 1fr)`, largura mínima zero nos filhos e quebras deliberadas para ações. Não usar `overflow-x: hidden` como correção de conteúdo inacessível.
- Extrair, se a inspeção confirmar benefício, `Scoreboard.svelte` e um elemento de pontuação para a representação comum. `Placar.svelte` conserva a operação; `PlacarManual.svelte` pode ser adaptado/substituído com migração dos seus chamadores. Nomes finais devem seguir as convenções locais.
- Evitar reescrever `App.svelte` e o transporte para fazer uma mudança de apresentação. Não duplicar cálculo de placar ou regra de vitória no componente visual.
- Adaptar pela área disponível, não por detecção do modelo Z Fold. Começar por larguras CSS 320/360/390/600/720/840/1024/1440 e alturas 360/480/640/900/1100; ajustar aos valores reais medidos.
- Container queries para composição e CSS fluido para tamanho. Considerar `dvh`, áreas seguras e altura reservada para mensagens essenciais. Se JS for necessário, observar o contêiner real e limpar os listeners. Não desligar zoom para fazer caber.
- Em altura curta, reduzir metadados/espaçamento antes dos pontos. Dados críticos, erro de conexão e desfazer não podem sumir. Se zoom exigir rolagem para manter legibilidade, permitir rolagem acessível; não prometer ausência de rolagem em toda condição.

### Tipografia, temas e identidade

- Reutilizar `web/public/fontes/teko-latin-var.woff2` e Inter local. Peso 600 real, evitando o antigo pedido de 800 para uma fonte declarada até 700.
- Ponto inicial aprovado: peso 600, `line-height: .9`, `letter-spacing: -.03em`, numerais tabulares, cerca de 36% da largura do contêiner na prévia, limite ilustrativo de 350 px.
- A fórmula de produção deve caber em largura **e altura**. Tratar 0, 8, 10, 88, 99, 100 e três dígitos com vantagem sem teto. A exigência de largura vale também para o maior resultado válido da regra vigente; não truncar números com reticências.
- Zero à esquerda (`08`) é demonstrativo, não decisão de negócio: manter a representação atual, salvo aprovação explícita.
- Novos tokens semânticos em `app.css` para superfícies, bordas, marca, ações, foco e times. Migrar somente componentes afetados em cada entrega; não promover uma limpeza global como escopo oculto.
- Temas pelo contrato `data-tema="sol"` e preferência existente `placar:tema`. Fonte grande não compensa contraste fraco. Medir texto normal, texto grande, foco, controles e estados reais.
- Ícones pelo `Icone.svelte` existente. Não introduzir CDN ou biblioteca de ícones apenas porque o protótipo a utilizou.
- Animações informativas de 150–300 ms para ponto, correção e estados. Com movimento reduzido, atualização imediata e feedback textual acessível.

### Preservação funcional

- Manter PIN de cinco dígitos, apelido, dados de quadras e permissões existentes.
- Manter chave local de inversão por sala, conexão, fila de comandos, desfazer auditável, pareamento do relógio, continuidade da sessão e retorno à Home.
- Transferência de controle não deve mudar quem pode pontuar. Estado visual precisa refletir o dono atual do controle, não apenas o papel.
- Nenhuma alteração em `wear/` ou banco de produção. Qualquer necessidade nova vira proposta explícita.

## 6. E1 — Home esportiva e entrada responsiva

**História:** [CV4.DS1.US1](cv4-ds1-inicio/cv4-ds1-us1-home/index.md). **Esforço 6/10.**

**Resultado:** entrar por código, criar quadra e escolher uma quadra ativa no visual aprovado, aproveitando telas largas e mantendo os campos acessíveis no Fold fechado.

| Tarefa | Esforço | Trabalho concreto |
|---|---:|---|
| E1.1 — Conferir base e fluxo de entrada | 3/10 | Comparar a branch `fix/entrar-na-quadra-pela-home`, seus testes e seu aceite; identificar o que já foi integrado |
| E1.2 — Base visual e largura da Home | 4/10 | Tokens aditivos, fonte local, layout da Home independente do limite global, temas |
| E1.3 — Formulários e cards reais | 5/10 | Aba de acompanhar inicial, código/apelido, criação simples, pontuação real nos cards e entradas com/sem apelido salvo |
| E1.4 — Estados e acesso | 4/10 | Carregando, vazio, falha, PIN inválido/expirado, apelido em uso, nome longo, foco e teclado virtual |
| E1.5 — Verificar e documentar | 4/10 | Testes de fluxo, primeiras verificações de navegador, capturas, roteiro para Navigator e atualização de tokens |

**Arquivos prováveis:** `web/src/components/HomePlacar.svelte`, `web/src/app.css`, `web/src/App.svelte` e `ModalEntrar.svelte` somente se o fluxo exigir; testes em `web/tests/` e proposta de `web/e2e/`.

**Detalhes:** fazer uma composição de coluna única estreita e duas regiões em largura suficiente; priorizar formulário sem hero alto no telefone. Nome da quadra discreto no card, placar maior e nomes das equipes legíveis. O card deve indicar a ação e apresentar erro perto dela. Não aumentar frequência de atualização nem prometer que a lista acompanha em tempo real sem verificar o mecanismo vigente; hoje a Home carrega a lista e permite atualizar.

**Concorrência:** a branch de correção relata 409 por apelido em uso e erro fora da área visível. Esse diagnóstico pertence à outra história. Reusar a correção após aceite ou coordenar a dependência; não duplicar nem concluir por conta própria o trabalho alheio. O protótipo não prova que essa falha foi resolvida.

**Aceite:** Given Home em cliente novo ou com apelido salvo; When entrar por código, escolher card ou criar quadra; Then a operação conclui ou informa um erro visível junto à ação; And os campos, botões e feedback cabem em ambos os temas e nos formatos suportados.

**Validação:** roteiro V1. Dois clientes simultâneos, dados reais de teste, checagem de layout em 320 px e telas largas. Erro 409 deliberado deve ser perceptível sem procurar no topo.

**Fora do escopo:** mudar APIs, acrescentar QR scanner ou redesenhar a sala nesta entrega. **Ponto de pausa:** Home aceita e utilizável; o agente seguinte pode iniciar E2 sem trabalho incompleto de E1.

## 7. E2 — Placar do espectador e adaptação ao Fold/tablet

**História:** [CV4.DS2.US1](cv4-ds2-acompanhamento/cv4-ds2-us1-placar/index.md). **Esforço 7/10.**

| Tarefa | Esforço | Trabalho concreto |
|---|---:|---|
| E2.1 — Representação comum do resultado | 5/10 | Separar pontuação visual dos controles sem duplicar estado e regra de jogo |
| E2.2 — Escala por área disponível | 6/10 | Teko 600, largura/altura, 1–3 dígitos, equipes longas, orientação e barras do navegador |
| E2.3 — Hierarquia da sala | 4/10 | Nome/código/regras compactos; metadados não empurram o resultado para fora da primeira tela |
| E2.4 — Animação e acessibilidade | 4/10 | Distinguir ponto/desfazer, anúncios moderados e movimento reduzido |
| E2.5 — Validar Fold e tablet | 5/10 | Abrir/fechar/girar durante o jogo, ler de longe, testar os dois temas e preservar inversão |

**Arquivos prováveis:** `SalaQuadra.svelte`, `PlacarManual.svelte`, `CartaoDobravel.svelte`, novo componente visual se necessário, tokens e testes. Inspecionar consumidores de `CartaoDobravel` antes de remover ou alterar; o controlador ainda pode usá-lo até E4.

**Aceite:** Given espectador em uma partida; When há ponto/correção ou a tela muda de tamanho; Then o placar continua completo e legível, sem perda de estado; And nome da sala e regras ocupam papel secundário. A inversão continua local.

**Validação:** V2. Valores extremos, duplas longas, passagem entre dois e três dígitos, Fold fechado/aberto em retrato/paisagem e tablet apoiado. Proposta de teste de leitura a aproximadamente 1 m e 3 m, a calibrar com o Navigator; isso não é promessa de legibilidade universal.

**Fora do escopo:** tela cheia real e regras novas. **Ponto de pausa:** acompanhamento responsivo entregue com o comportamento de navegação vigente preservado.

## 8. E3 — Imersão estável e tela cheia real

**História:** [CV4.DS2.US2](cv4-ds2-acompanhamento/cv4-ds2-us2-imersao/index.md). **Esforço 8/10.**

| Tarefa | Esforço | Trabalho concreto |
|---|---:|---|
| E3.1 — Separar estados de apresentação | 5/10 | Estado dos controles visíveis separado de fullscreen do navegador e orientação |
| E3.2 — Solicitação e eventos de fullscreen | 6/10 | Gesto direto, disponibilidade, promise rejeitada, `fullscreenchange`, saída pelo sistema e listener cleanup |
| E3.3 — Controles sobre o placar | 6/10 | Revelação sem mover os pontos; timer de 3 s suspenso durante interação/foco/modal |
| E3.4 — Modais, erros e ciclo de vida | 6/10 | Conteúdo dentro do elemento em fullscreen, Escape, foco de retorno, perda de conexão, troca de app |
| E3.5 — Verificação física e alternativa | 6/10 | Chrome no Fold, tablet disponível, navegador com suporte ausente/recusa e modo instalado se disponível |

**Arquivos prováveis:** `SalaQuadra.svelte`, `Dialogo.svelte` e consumidores, módulo de apresentação/fullscreen em `web/src/lib/` se justificar, testes unitários e de navegador.

**Comportamento proposto:**

1. Espectador pode entrar em imersão automaticamente; recolher a interface é independente de fullscreen.
2. Botão acessível “Tela cheia” solicita `requestFullscreen()` diretamente no gesto. Não chamar apenas após o timer de três segundos nem depois de uma sequência de operações assíncronas que perca a ativação do usuário.
3. Confirmar fullscreen por evento/estado real. Falha não pode produzir botão “Sair da tela cheia” quando nada entrou; informar e continuar em imersão dentro da aba.
4. Toque revela controles sem deslocar o resultado. Não capturar o toque de forma que acione pontuação ou uma ação que ainda estava oculta.
5. Suspender timer com modal aberto, foco em controle/input, interação ativa e erro que exige ação. Movimento de mouse não deve produzir ocultação imprevisível para quem usa teclado.
6. `Escape`, Voltar do Android, troca de app e saída do navegador atualizam o estado sem reentrada automática. Um novo pedido usa novo gesto.
7. Modais e ferramentas devem estar na árvore do elemento solicitado em fullscreen, ou solicitar a raiz que os contém. Verificar top layer de `<dialog>` no browser real.
8. Wake Lock continua sendo um mecanismo independente, sem prometer que fullscreen manterá a tela acesa. Preservar o tratamento vigente de visibilidade e indisponibilidade.

**Aceite:** Given espectador com navegador compatível; When toca em Tela cheia; Then a aplicação solicita e reconhece a entrada real; And os controles continuam acessíveis. Given recusa ou indisponibilidade; Then placar continua funcionando na aba e o estado visual informa a condição corretamente.

**Validação:** V3. Testar ausência/recusa por simulação e funcionamento físico; testes headless não provam remoção das barras Android. Verificar painel sem saltos antes/depois de ocultar controles.

**Limite técnico:** browser e sistema podem manter elementos de navegação, negar suporte ou encerrar fullscreen. O produto não pode garantir ocultação irrestrita do sistema. [MDN: requestFullscreen](https://developer.mozilla.org/en-US/docs/Web/API/Element/requestFullscreen) e [guia de fullscreen](https://developer.mozilla.org/en-US/docs/Web/API/Fullscreen_API/Guide), consultados em 2026-09-26.

**Ponto de pausa:** imersão e fullscreen aceitos, com limitações reais documentadas por aparelho.

## 9. E4 — Admin e controlador

**História:** [CV4.DS3.US1](cv4-ds3-operacao/cv4-ds3-us1-controle/index.md). **Esforço 7/10.**

| Tarefa | Esforço | Trabalho concreto |
|---|---:|---|
| E4.1 — Aprovar superfície de operação | 3/10 | Mostrar composição com +1, desfazer, posse do controle e ações secundárias antes de implementar |
| E4.2 — Reusar placar e posicionar ações | 5/10 | Dois botões inequívocos, alvo de toque confortável e desfazer sempre a um toque |
| E4.3 — Papéis e posse do controle | 6/10 | Admin com/sem controle, controlador com/sem controle, transferência para relógio e presença |
| E4.4 — Fila, erro e feedback | 5/10 | Toques rápidos, pendências, desconexão, vitória e desfazer sem reescrever sincronização |
| E4.5 — Validar operação em três clientes | 5/10 | Operador, espectador e terceiro cliente/relógio; verificar permissões também no servidor |

**Arquivos prováveis:** `Placar.svelte`, `SalaQuadra.svelte`, `ListaPresentes.svelte`, componente visual comum, testes de controle/sync. `App.svelte` somente para ligação dos eventos existentes.

**Aceite:** Given participante com posse do controle; When toca em +1 ou desfazer; Then um comando válido é processado e todos convergem; And correção continua a um toque. Given participante sem controle; Then a interface reflete essa condição e o backend preserva restrições.

**Detalhes:** diferenciar papel e posse do controle, remover ações duplicadas com uma localização clara e evitar que cor da equipe signifique “admin”. Não ocultar desfazer em menu ou confirmação. Ao inverter lados, trocar também os comandos visuais para que o botão corresponda ao time mostrado. O Navigator ainda precisa aprovar esta composição; a prévia de espectador não cobre isso.

**Validação:** V4, incluindo dois toques rápidos, correção, promoção/revogação, transferência ao relógio e tentativa indevida conforme os testes existentes. Reconectar não deve repetir comando já confirmado.

**Fora do escopo:** novos gestos de pontuação, nova política de transferência ou mudanças no Wear OS. **Ponto de pausa:** operação aceita com testes existentes preservados.

## 10. E5 — Superfícies auxiliares e estados

**História:** [CV4.DS3.US2](cv4-ds3-operacao/cv4-ds3-us2-superficies/index.md). **Esforço 5/10.**

| Tarefa | Esforço | Trabalho concreto |
|---|---:|---|
| E5.1 — Inventário e hierarquia de ações | 3/10 | Local único para compartilhar/QR, regras, presentes e relógio; preservar descoberta |
| E5.2 — Diálogos responsivos | 4/10 | `Dialogo`, configuração, compartilhamento, relógio, entrada e histórico nos dois temas |
| E5.3 — Vitória e condições excepcionais | 4/10 | Encerramento, reinício, sala expirada, erro, vazio e perda de conexão |
| E5.4 — Teclado e textos longos | 4/10 | Zoom, foco, rolagem do diálogo e retorno ao elemento acionador sem esconder campo |
| E5.5 — Validar coerência | 3/10 | Navegação entre estados e temas, permissões e fullscreen sem botões inacessíveis |

**Arquivos prováveis:** `Dialogo.svelte`, `ModalEntrar.svelte`, `ModalConfigurarPartida.svelte`, `ModalCompartilhar.svelte`, `ModalCelebracaoVitoria.svelte`, `ModalRelogio.svelte`, `LinhaDoTempo.svelte`, `ListaPresentes.svelte`, somente nos aspectos necessários à identidade e acessibilidade.

**Aceite:** Given qualquer superfície auxiliar; When aberta em Fold fechado, aberto ou tablet, inclusive fullscreen; Then conteúdo e ação principal ficam acessíveis por toque/teclado; And fechar retorna o foco e o placar sem perder sessão.

**Validação:** V5. Cada diálogo abre/fecha por caminhos reais; formulário com teclado virtual; histórico com muitos eventos; presentes com nomes longos; vitória e reinício acompanhados em dois clientes.

**Fora do escopo:** nova funcionalidade de diálogo ou novos fluxos de pareamento. **Ponto de pausa:** jornada coerente nos dois temas.

## 11. E6 — Regressão e consolidação

**História:** [CV4.DS3.TS1](cv4-ds3-operacao/cv4-ds3-ts1-regressao/index.md). **Esforço 6/10.**

| Tarefa | Esforço | Trabalho concreto |
|---|---:|---|
| E6.1 — Consolidar testes de navegador | 5/10 | Fluxos/viewport/temas, controles fora da tela, animação reduzida e foco |
| E6.2 — Contraste e acessibilidade | 5/10 | axe e medições dos números/controles nos estados reais; registro da cobertura e exceções |
| E6.3 — Matriz física de aceitação | 5/10 | Fold fechado/aberto, tablet e desktop; dois/três clientes conforme a história |
| E6.4 — Coerência, dívida e release | 4/10 | Tokens, decisão, roadmap, briefing, changelog, worklog, versões e instruções |
| E6.5 — Empacotamento e reversão | 3/10 | Build estático, verificação sem CDN em runtime e plano de rollback sem editar banco |

**Estratégia de teste:** propor Playwright e axe como ferramentas de desenvolvimento em E1; confirmar compatibilidade das versões no início da implementação, registrar custo e permitir aprovação dessa decisão no Checkpoint 1. Manter dependências fora da imagem de runtime. Exercitar comportamento, não testar snapshots de classes CSS como substituto de validação.

**Aceite:** evidência reproduzível, matriz física preenchida e nenhuma falha crítica de corte, controle, contraste ou divergência de estado aberta. Medições automáticas não autorizam declarar conformidade total WCAG. Registrar o que foi ou não coberto.

**Dívida:** revisitar `debt-contraste-do-modo-sol-sem-verificacao-automatica`. Só marcar Paid quando sua condição de fechamento for atendida, com execução automatizada no pipeline usado pelo projeto, não apenas comando local. Sem pipeline disponível, registrar o trabalho faltante e conservar o estado apropriado.

**Ponto de pausa:** CV4 consolidado, aguardando apenas o checkpoint de histórico/publicação que ainda não tiver sido autorizado.

## 12. Validação obrigatória em cada entrega

- Medir baseline de testes antes de modificar código; falha já existente deve ser registrada com evidência.
- Rodar `npm test`, `npm run check`, `npm run build` em `web/` e `uv run pytest` na raiz, conforme o contrato local. Executar `ruff` quando houver Python alterado ou no fechamento integrado.
- Acrescentar o runner de navegador somente após aprovado e registrar o comando definitivo em `web/package.json`, guia de desenvolvimento e test-guide; não assumir que `npm run test:e2e` já existe.
- Apresentar contagem real de passes/falhas, capturas e roteiro físico no Checkpoint 2. Nenhum resultado foi antecipado neste plano.
- Nunca depender só de emulação de largura: validar abrir/fechar o Fold com a partida em andamento, tablet real e contraste em ambiente de jogo.
- Se houver mudança no estado/sincronização, executar reinício e reconciliação exigidos no guia; banco de produção nunca é dado de teste.

## 13. Riscos e questões que o próximo agente deve carregar

| Risco / decisão pendente | Ação | Momento |
|---|---|---|
| Correção concorrente da Home | Conferir aceite, merge e testes; coordenar arquivos compartilhados | Antes de E1 |
| Versões e briefing divergentes | Registrar fonte de verdade e combinar coerência da release; não reverter 0.11.0 do relógio | E1 e fechamento |
| Tablet não identificado | Obter modelo, navegador e orientação usual ao preparar teste; isso não bloqueia plano/Home | Antes da validação física E2/E3 |
| Distância de leitura sem requisito fixo | Teste proposto a 1 m/3 m; Navigator aceita situação real, não uma medida arbitrária | E2 |
| Recusa/saída de fullscreen | Comportamento alternativo claro; validar por browser e sistema | E3 |
| Diálogo fora do elemento fullscreen | Conferir árvore renderizada, top layer e Escape | E3/E5 |
| Três dígitos e nomes compridos | Ajustar escala sem truncar resultado; não impor teto esportivo | E2 |
| Animação atrasa leitura ou toque | Curta, cancelável e respeitando movimento reduzido; estado correto primeiro | E2/E4 |
| CSS global provoca regressão gradual | Tokens aditivos, isolamento de componentes e capturas das superfícies ainda não migradas | Todas |
| Mudança indevida de regra/controle | Reusar comandos e checar permissões no servidor | E4 |

Decisões de produto pendentes devem ser levadas ao checkpoint da entrega afetada; não é necessário perguntar todas antes de iniciar E1. As especificações visuais do operador e das janelas devem ser mostradas antes de sua implementação.

## 14. Intenção de versão e publicação

- Este plano e suas referências não alteram a versão do produto.
- Primeira entrega visível: intenção **minor**, candidata a `0.12.0` partindo da base documentada. O número exato deve ser recalculado após conferir releases concorrentes.
- E2–E5 podem gerar minors independentes por capacidade observável; correções internas posteriores podem ser patch. Não acumular código não validado em `master` para “fechar tudo junto”.
- E6 não exige versão nova se apenas consolida evidência e documentação; se corrigir comportamento, classificar a mudança real.
- Merge e publicação exigem aceite do Navigator no checkpoint correspondente. Não alterar produção neste ciclo de planejamento.
- Reversão: identificar release/commit anterior e restaurar o artefato da aplicação conforme processo de deploy, avaliando antes a política de recriação do banco por versão. Não prometer preservação de dados sem verificar essa política e nunca reverter banco manualmente.

## 15. Checkpoints, commits e retomada

1. **Agora — Checkpoint 1:** apresentar este plano, sequência, esforço, limites e E1. A aprovação visual já existe; a autorização de implementação não.
2. **Após autorização de E1:** implementar apenas E1 e seus testes; parar no Checkpoint 2 com roteiro concreto.
3. **Após validação física:** revisar refatoração/dívidas (Checkpoint 3), documentar/coerência e propor histórico/merge (Checkpoint 4).
4. **Entregas seguintes:** conferir a base e atualizar seu plano antes do respectivo Checkpoint 1. Uma aprovação de E1 não libera E2–E6 automaticamente.
5. **Persistência:** commits parciais documentais/de trabalho e push na branch são previstos em “Commit and Release Rules” do guia local. Não significam aceite ou merge em `master`. Há redação anterior de commit ao final; seguir a regra explícita de persistência de branch e registrar essa interpretação no handoff.
6. **Ao interromper:** atualizar assinatura, passo, último checkpoint aceito, comandos/resultados, arquivos pendentes, próxima ação e bloqueios; sincronizar branch. O agente seguinte começa por `handoff.md` e confirma o estado remoto.

**Próxima ação concreta:** Navigator revisar o plano e autorizar E1. Até lá, conservar todas as histórias em `Planned` e a implementação intacta.
