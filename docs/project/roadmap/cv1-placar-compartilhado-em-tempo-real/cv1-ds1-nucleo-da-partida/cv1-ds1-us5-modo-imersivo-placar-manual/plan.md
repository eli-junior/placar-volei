# Plano de Implementação — CV1.DS1.US5

## 1. Contexto e Objetivo

O Navigator solicitou uma experiência diferenciada para o espectador da quadra:
- Visual de placar dobrável manual clássico (com anéis e cartões que viram quando há ponto).
- Modo imersivo focado no jogo.
- Toque na tela para sair do modo imersivo e revelar os controles e botão de voltar.
- Retorno automático ao modo imersivo após 3 segundos de inatividade.

## 2. Arquitetura e Componentes

### 2.1 Componente de Placar Dobrável Manual (`CartaoFlip.svelte` / `PlacarManual.svelte`)
- Cartão com anéis metálicos no topo (ilusionismo visual via SVG/CSS com presilhas).
- Linha divisória horizontal central e vincos sutis simulando placa dobrável.
- Tipografia de alta visibilidade e contraste atlético (`font-display: Teko` com suporte a fallback).
- Efeito de virada 3D (`perspective: 1000px`, rotação no eixo X com sombra dinâmica).
- Animação de descida do cartão quando o ponto sobe, e efeito inverso quando desfeito.
- Suporte a `prefers-reduced-motion` com transição imediata ou sutil sem 3D.

### 2.2 Gerenciamento do Modo Imersivo (`SalaQuadra.svelte`)
- Estado reativo no Svelte 5: `modoImersivo = $state(true)`.
- Temporizador: `timerImersivo = null`.
- Função `registrarInteracao()`:
  - Se `modoImersivo` for `true`, alterna para `false`.
  - Reinicia o temporizador de 3000ms.
  - Ao expirar os 3000ms (se `!podeControlar` e `!modalLinhaDoTempoAberto`), define `modoImersivo = true`.
- Transições suaves usando `fade` ou `slide` do Svelte para entrada e saída dos controles (cabeçalho, botão voltar, lista de participantes).
- Preservação da experiência do Controlador: se o usuário for Admin ou Controlador, o modo padrão continua com os alvos táteis de marcação rápida de pontos (+1 e Desfazer), garantindo o princípio de uso com uma mão na beira da quadra.

## 3. Critérios de Aceite (BDD)

- **Cenário 1: Entrada no Modo Imersivo para Espectador**
  - **Given** que o participante entra na quadra como Espectador
  - **When** se passam 3 segundos sem toque na tela
  - **Then** a interface oculta os controles secundários e exibe o placar manual dobrável em destaque central.

- **Cenário 2: Virada de Cartão ao Marcar Ponto**
  - **Given** que a tela do espectador está aberta na quadra
  - **When** um controlador marca ponto para uma das equipes
  - **Then** o cartão de pontuação da respectiva equipe executa a animação de virada mecânica revelando a nova pontuação.

- **Cenário 3: Revelação dos Controles por Toque**
  - **Given** que o espectador está em Modo Imersivo
  - **When** ele toca em qualquer lugar da tela
  - **Then** a interface sai do Modo Imersivo imediatamente, revelando a barra superior com o botão "← Quadras", o perfil e a lista de presentes.

- **Cenário 4: Retorno Automático após 3 Segundos**
  - **Given** que os controles estão visíveis
  - **When** passam-se 3 segundos sem qualquer clique, toque ou movimento
  - **And** nenhum modal está aberto
  - **Then** o Modo Imersivo é reativado automaticamente.

## 4. Riscos e Mitigações

- **Conflito de toque com botões:** O clique no botão "← Quadras" ou "📜 Linha do Tempo" deve executar sua respectiva ação normalmente sem ser engolido pelo listener global. Mitigação: usar propagação de eventos padrão e reiniciar o timer de inatividade.
- **Modais abertos:** Se o usuário abrir a Linha do Tempo, a tela não deve voltar ao modo imersivo enquanto o modal estiver aberto. Mitigação: suspender o timer de inatividade enquanto `modalLinhaDoTempoAberto` for verdadeiro.
