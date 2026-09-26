# Rota de validação — CV4

Este documento descreve testes **a executar durante a implementação**. Nenhum resultado de aplicação foi produzido pelo planejamento. As verificações documentais desta branch estão no handoff.

## Preparação do ambiente

O Driver prepara o ambiente da história em um checkout isolado. Não apontar para o SQLite ou o segredo de produção.

1. Ler `docs/process/development-guide.md` e confirmar os comandos abaixo na base atual.
2. Criar `.env` local a partir de `.env.example` somente se ainda não existir; configurar banco de teste `data/placar-cv4.db` e segredo de desenvolvimento. Não versionar `.env`.
3. Executar, na raiz do checkout:

```powershell
uv sync
uv run pytest
```

4. No diretório `web/`:

```powershell
npm ci
npm test
npm run check
npm run build
```

5. Terminal A, na raiz, usando banco de desenvolvimento:

```powershell
$env:DB_PATH = 'data/placar-cv4.db'
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

6. Terminal B, em `web/`, para iteração:

```powershell
npm run dev -- --host 0.0.0.0
```

7. Abrir `http://localhost:5173/` no computador. No telefone/tablet da mesma rede, usar `http://<IP-LAN-do-computador>:5173/`. O Driver deve entregar o endereço **resolvido e testado** no Checkpoint 2, não deixar o Navigator adivinhar o IP. Confirmar que `http://<IP-LAN-do-computador>:8000/` serve o build gerado quando a validação usar estáticos.

HTTP em rede local atende inspeção básica de layout, mas não substitui o contexto seguro de produção: Wake Lock, instalação e outras APIs podem diferir. Para esses testes, preparar URL HTTPS de teste autorizada, com dados isolados, e informar o endereço concreto. Não publicar a branch de teste em produção sem autorização.

O runner de navegador ainda não existe na base. A implementação deve registrar o comando definitivo depois de adicionar e validar Playwright/axe; não apresentar comando futuro como executável hoje.

## Clientes e dados

- **A:** admin, apelido `Admin CV4`, cria uma quadra `Teste visual CV4`.
- **B:** espectador, `Leitura CV4`, outro navegador/perfil ou Fold.
- **C:** controlador ou terceiro participante, `Controle CV4`, tablet/outro perfil. Usar o relógio somente quando validar o fluxo existente que o inclui.
- Cada cliente precisa de sessão própria. Duas abas do mesmo perfil podem compartilhar identidade e não provar a condição multi-cliente.
- Anotar PIN gerado e URLs `/quadra/<PIN>` reais. PIN `82906` e pessoas das prévias são dados ilustrativos.
- Para valores extremos, criar fixtures locais ou cenários de teste. Não escrever diretamente no banco de produção; não gerar pontuação falsa numa sala real do grupo.
- Usar nomes curtos, duplas com nomes compridos e nomes no limite aceito pela API. Cobrir pontos `0`, `8`, `10`, `88`, `99`, `100` e resultado de três dígitos permitido pelas regras sem teto.

## Matriz mínima

| Superfície | Formatos/condições | Evidência |
|---|---|---|
| Fold fechado | Retrato e paisagem; barras do Chrome expandidas/recolhidas | Screenshot, dimensões CSS medidas e leitura física |
| Fold aberto | Retrato e paisagem; abertura/fechamento durante a partida | Estado antes/depois, sem recarregar |
| Tablet apoiado | Retrato e paisagem; modelo/navegador informados pelo Navigator | Leitura próxima e à distância |
| Computador | 1024 e 1440 px, janela estreita, teclado, zoom 200% | Foco, disposição e ausência de ações cortadas |
| Emulação complementar | 320/360/390/600/720/840 px; paisagem de 360/480 px de altura | Testes automatizados de geometria e screenshot |

Executar os cenários afetados nos **dois temas**. Variar papéis conforme cada entrega. Testar `prefers-reduced-motion`, nomes compridos e ausência de rede. Em zoom 200%, a aceitação é legibilidade e acesso a todas as funções; rolagem necessária não é defeito por si só.

Medir a área real do documento/contêiner; capturas de 968 ou 2160 pixels não fornecem diretamente a largura CSS. Não multiplicar medidas pelo fator de resolução da imagem.

## V1 — Home (E1)

1. Cliente A abre `/` sem apelido salvo. Alterna Entrar/Criar e os dois temas.
2. A cria quadra; B usa o PIN e um apelido diferente para entrar.
3. A marca ponto e B confirma o mesmo resultado. Voltar à Home e usar o mecanismo de atualização vigente para conferir o card.
4. B volta e entra pelo card com apelido salvo; outro perfil testa o card sem apelido salvo.
5. Em perfil novo, tentar um apelido já em uso; produzir também PIN inválido e sala inexistente/expirada.
6. Repetir com teclado virtual aberto e largura estreita. Verificar posição do erro junto à ação e foco no campo que requer correção.

**Aprova:** criação/entrada funcionam, erros ficam visíveis, card representa dados recebidos, campos e ações acessíveis e temas coerentes. A escolha da aba e nome salvo preservam o comportamento combinado.

**Falha:** toque parece não fazer nada; erro fora da área visível; ação cortada; pedido duplicado por toque; identidade ou regras alteradas sem acordo. Lista estática rotulada como atualização contínua sem mecanismo correspondente também falha.

## V2 — Leitura e responsividade (E2)

1. A controla e B acompanha. Em B, comparar tela normal e composição de acompanhamento.
2. A marca e desfaz; observar transição curta e números corretos, inclusive com movimento reduzido.
3. Em B, abrir/fechar o Fold e alternar orientação sem recarregar. Registrar PIN, papel, lado local e resultado antes/depois.
4. Inverter lados em B; A não deve inverter automaticamente. Atualizar novamente o placar.
5. Executar cenários de 1, 2 e 3 dígitos e nomes longos. Nenhum número pode receber reticências, sobrepor o outro ou sair do painel.
6. Testar tablet apoiado. Pedir ao Navigator leitura dos pontos e identificação das equipes a uma distância confortável e aproximadamente 3 m, ajustando o critério à situação real.

**Aprova:** placar domina a primeira tela na condição normal suportada, números completos e legíveis, metadados menores e estado preservado. Capturas registram dimensões e contexto de leitura.

**Falha:** nome da quadra empurra números para fora; placas crescem sem leitura útil; número de três dígitos cortado; abrir o Fold muda sessão ou estado; animação impede perceber a pontuação atual.

## V3 — Imersão e fullscreen (E3)

1. Em B, aguardar três segundos sem interação. Controles recolhem; pontos permanecem na mesma posição/tamanho.
2. Tocar para revelar. Abrir histórico/configuração disponível e aguardar mais de três segundos: o diálogo deve continuar utilizável.
3. Navegar por teclado: foco em controle deve impedir seu desaparecimento; fechar diálogo deve devolver o foco.
4. Acionar Tela cheia por toque real e conferir remoção das barras do navegador onde suportada, além do estado `fullscreenElement` observado pelo Driver.
5. Sair pelo sistema/Escape; a interface não deve indicar fullscreen ativo nem forçar reentrada.
6. Trocar de app, voltar, girar e abrir/fechar o Fold. Anotar quais mudanças encerram fullscreen naquele aparelho.
7. Simular suporte ausente e rejeição do pedido. Imersão dentro da aba continua operável e informa a condição.
8. Abrir diálogos enquanto em fullscreen; verificar visibilidade, fechamento e foco. Confirmar que toque para mostrar controles não executa uma ação oculta.
9. Desconectar B e conferir aviso de reconexão perceptível mesmo durante imersão. Após aproximadamente 30 s, reconectar sem recarregar.

**Aprova:** estados refletem o navegador; imersão não desloca o resultado; foco/diálogos/erros permanecem acessíveis; recusa tem alternativa funcional. Limitações por aparelho registradas.

**Falha:** simulação visual anunciada como fullscreen real; timers reentram em tela cheia sem gesto; modal some; barra invisível deixa foco preso; aviso de desconexão é ocultado.

Teste automatizado com fullscreen simulado comprova transições internas, não a experiência Android. Evidência física é obrigatória nesta entrega.

## V4 — Operação e papéis (E4)

1. A com controle marca duas vezes rapidamente; B e C acompanham os dois pontos e a convergência final.
2. A desfaz um ponto. Histórico registra correção; todas as telas convergem.
3. Promover C e transferir controle. A e C refletem posse; B permanece espectador.
4. C inverte seus lados e marca em cada lado; conferir a equipe real do evento.
5. Interromper conexão do controlador, aguardar comportamento de retorno de controle vigente e reconectar. Verificar estado, pendências e restrições sem reinventar política.
6. Validar transferência para o relógio quando disponível; a web continua identificando o controlador corretamente.
7. Reexecutar testes de backend de permissões/controle, incluindo chamada indevida de espectador conforme fixtures existentes.
8. Observar vitória, desfazer do ponto final permitido e nova partida conforme permissões atuais.

**Aprova:** pontuar e desfazer continuam a um toque quando autorizados; botões correspondem ao time mostrado; fila não perde toque nem duplica confirmação; permissões no servidor preservadas.

**Falha:** desfazer escondido em menu, toque executa equipe errada após inversão, papel confundido com posse, espectador consegue comando indevido ou números divergem.

## V5 — Superfícies auxiliares (E5)

1. Abrir compartilhar/QR, duplas/regras, participantes, relógio e histórico pelos caminhos reais permitidos ao papel.
2. Repetir em Fold fechado com teclado virtual, Fold aberto e fullscreen quando disponível.
3. Navegar por Tab/Shift+Tab; fechar por Escape e ação explícita; conferir foco no acionador.
4. Trocar tema, usar zoom 200%, nomes longos e histórico com muitos eventos.
5. A encerra e reinicia a partida, B observa. Verificar celebração e alternativa com movimento reduzido.
6. Reproduzir sala expirada e falha de rede; a ação de recuperação precisa estar acessível.

**Aprova:** conteúdo acessível, foco correto, hierarquia consistente, QR legível e partida preservada. Ações indisponíveis têm estado coerente.

**Falha:** teclado cobre campo/ação sem possibilidade de rolar; modal maior que a área disponível sem acesso ao fechamento; QR perde contraste; erro desaparece por timer.

## V6 — Consolidação (E6)

1. Executar todos os testes obrigatórios e o runner de navegador aprovado; registrar versões de ambiente e comando real.
2. Medir contraste dos temas, estados, foco e controles. Para texto normal usar referência de 4,5:1, texto grande 3:1 e elementos visuais essenciais 3:1; o teste deve avaliar o elemento/superfície real, não só uma variável isolada. Anotar critérios aplicáveis e exceções.
3. Verificar keyboard, labels, semântica, anúncios e zoom manualmente; axe sozinho não comprova conformidade completa.
4. Conferir matriz física e anexar evidências por dispositivo/navegador. Resultados não executados ficam explicitamente pendentes.
5. Inspecionar requests do build: fontes e ícones locais, nenhum CDN obrigatório para renderizar a aplicação.
6. Rodar smoke test do build pelo FastAPI. Se houve mudança de estado, executar restart com dados isolados e confirmar reconstrução; se houve mudança de conexão, executar modo avião/reconciliação.
7. Revisar dívida, decisões, versões, roadmap, README, briefing, tokens e instruções de setup. Só quitar a dívida de contraste se a condição de fechamento estiver integralmente satisfeita.

**Aprova:** evidência reproduzível e aceita, sem falha crítica aberta. Riscos residuais têm responsável, motivo e condição de revisão.

**Falha:** aprovação baseada apenas em capturas, teste não executado descrito como verde, alteração indevida de dados/permissões, falta de rota física ou documentação contradizendo o resultado.

## Registro que o Driver deve preencher por entrega

| Campo | Valor a registrar |
|---|---|
| História / branch / commit | IDs reais |
| Base e versões | SHA da master, aplicação, ferramentas e browsers |
| URL de validação | Endereço real acessível ao Navigator |
| Banco / dados | Ambiente isolado e PIN gerado; nunca segredo |
| Testes | Comando, contagem, duração relevante, falhas preexistentes ou novas |
| Dispositivos | Modelo, navegador, tema, orientação, área CSS e distância usada |
| Evidências | Arquivos/capturas e comportamento observado |
| Checkpoint 2 | Pendente ou aceite explícito com data e escopo |
| Surpresas / limites | Comportamento inesperado e decisão necessária |
| Próxima ação | Menor passo concreto para retomar |
