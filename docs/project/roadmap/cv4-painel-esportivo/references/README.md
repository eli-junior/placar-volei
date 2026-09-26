# Referências visuais aprovadas

Arquivos preservados da conversa de 2026-09-26, para que outro agente possa retomar o projeto sem acesso à sessão original:

- [Proposta do painel](proposta-painel.html): última prévia com Teko 600 e números ampliados, aprovada com “perfeito”. A aparência acompanha o ambiente e pode alternar entre claro e escuro.
- [Proposta clara](proposta-clara.html): versão que inicia em modo claro, aprovada com “ótimo”.

São **referências documentais**, fora do build e do runtime da aplicação. Não importar como componentes. Dados, estados e interações são ilustrativos.

## Como inspecionar

Ler a [decisão visual](../../../decisions/records/2026-09-26T1238Z-painel-esportivo-e-numeros-prioritarios.md) e os estilos dos fragmentos. Os arquivos podem ser apresentados novamente no ambiente de visualização da conversa, se disponível. Para abrir diretamente em navegador, o conteúdo principal funciona, mas ícones fornecidos pelo ambiente e ajustes opcionais podem não aparecer. A fonte da referência requer acesso ao Google Fonts. Não é necessário executar esses fragmentos para implementar a especificação textual.

## Valores de referência

| Elemento | Proposta aprovada |
|---|---|
| Fonte dos pontos | Teko |
| Peso | 600 |
| Escala no acompanhamento | `clamp(104px, 36cqw, 350px)` ilustrativo |
| Entrelinha / letras | `.9` / `-.03em` |
| Nome da quadra | 14–15 px, secundário |
| Código/regras | 12 px, secundários |
| Fundo claro / painel / texto | `#f4f5f1` / `#ffffff` / `#17201a` |
| Fundo escuro / painel / texto | `#101411` / `#191f1b` / `#f4f6f0` |
| Marca | Lima `#d4f25b`, texto `#17210a` |
| Equipes | Ciano e laranja, variantes por tema |

Os valores devem virar tokens semânticos e passar por contraste/zoom/layout no produto. A fonte já existe localmente em `web/public/fontes/teko-latin-var.woff2`; não carregar Google Fonts em produção.

## Limites que não viram requisitos automaticamente

- A escala da prévia não considera toda a altura disponível, teclado, zoom e três dígitos.
- O botão Tela cheia só altera a composição; não solicita fullscreen ao navegador.
- Não há sincronização real, backend, autenticação, fila ou permissões nesses arquivos.
- O fluxo do operador não foi desenhado por completo. A tela de criação demonstrativa não substitui sua especificação.
- Não há teste físico de leitura a distância nem evidência de acessibilidade automática.
- O prefixo zero em `08` é ilustrativo; preservar a regra de exibição do produto até decisão específica.
- Os controles do protótipo não reproduzem o temporizador automático. O desejo de manter o recolhimento em três segundos está registrado no plano.

As capturas iniciais do usuário não foram copiadas para o repositório: incluem conteúdo do navegador e ficam em caminhos temporários/dispositivos pessoais. O diagnóstico durável está no plano; futuras capturas de validação devem focar a aplicação e evitar dados pessoais externos ao teste.
