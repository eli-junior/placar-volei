# Guia de Teste e Validação — CV1.DS1.US5

## Objetivo

Validar o comportamento do Modo Imersivo e do Placar Dobrável Manual em tempo real com dois clientes (um Controlador/Admin e um Espectador).

## Pré-requisitos

1. Backend rodando localmente (`uv run uvicorn app.main:app --reload --port 8000`) ou via container (`docker compose up -d`).
2. Frontend compilado (`npm --prefix web run build`).

## Roteiro de Validação Multi-Dispositivo (2 Telas)

### Preparação
1. Abra um navegador normal (Janela 1) em `http://localhost:8000/`. Crie ou selecione uma Arena, entre na Quadra informando o apelido `Marcador` (ele se tornará ADMIN).
2. Abra uma janela anônima (Janela 2) em `http://localhost:8000/`. Acesse a mesma Arena e Quadra com o apelido `Torcedor` (ele será ESPECTADOR).

### Rota de Teste 1: Entrada Automática em Modo Imersivo para Espectador
- **Ação:** Na Janela 2 (Torcedor/Espectador), não toque nem clique na tela por 3 segundos.
- **Observação esperada:**
  - O cabeçalho com o botão `← Quadras`, o perfil e a lista de presentes desaparecem suavemente.
  - O placar dobrável manual centraliza-se na tela em modo limpo e imersivo, com os anéis superiores, os cartões das duas equipes e a dica sutil `👆 Toque na tela para opções`.
- **Condição de aprovação:** A tela limpa-se e foca no placar dobrável manual após 3 segundos de inatividade.
- **Condição de falha:** Os botões continuarem visíveis ou a tela não centralizar.

### Rota de Teste 2: Animação de Virada de Cartão (Flip 3D) em Tempo Real
- **Ação:** Na Janela 1 (Marcador), clique no botão `+1` da Equipe A.
- **Observação esperada:**
  - Na Janela 2 (Torcedor), em tempo real e sem recarregar a página, o cartão da Equipe A vira para a frente (flip down 3D sobre os anéis) revelando o número `1`.
- **Ação 2:** Na Janela 1, clique em `↺ Desfazer Último Ponto`.
- **Observação esperada:**
  - Na Janela 2, o cartão da Equipe A vira para cima (flip up 3D), retornando para `0`.
- **Condição de aprovação:** O cartão executa a animação tridimensional física ao marcar e ao desfazer.
- **Condição de falha:** O número mudar seco sem virada ou quebrar o layout do cartão.

### Rota de Teste 3: Revelação dos Itens sob Toque e Acesso ao Botão Voltar
- **Ação:** Na Janela 2 (em Modo Imersivo), dê um clique ou toque em qualquer lugar da tela.
- **Observação esperada:**
  - O Modo Imersivo é desativado imediatamente.
  - Reaparecem: barra superior com botão `← Quadras`, status `Ao vivo`, identificação do participante, botão `📜 Linha do Tempo` e a lista de presentes.
- **Ação 2:** Aguarde 3 segundos sem mexer.
- **Observação esperada:**
  - O Modo Imersivo volta a ser ativado automaticamente.
- **Condição de aprovação:** Um toque revela imediatamente todas as opções e o botão de voltar, e a inatividade retoma o modo imersivo após 3s.
- **Condição de falha:** O clique não revelar os controles ou não voltar após 3s.

### Rota de Teste 4: Suspensão do Timer com Linha do Tempo Aberta
- **Ação:** Na Janela 2, toque na tela e clique no botão `📜 Linha do Tempo`. Deixe o modal aberto por mais de 5 segundos.
- **Observação esperada:**
  - O modal permanece aberto e visível, sem ser fechado ou ocultado pelo temporizador de inatividade.
- **Ação 2:** Feche o modal da Linha do Tempo e aguarde 3 segundos.
- **Observação esperada:**
  - Após 3 segundos sem toques, a tela retorna ao Modo Imersivo.
- **Condição de aprovação:** O modal da linha do tempo não é interrompido pelo timer.

### Rota de Teste 5: Estabilidade do Controlador
- **Observação na Janela 1 (Marcador/ADMIN):**
  - O Marcador NÃO entra em modo imersivo automático; seus botões de marcação `+1` e `Desfazer` continuam permanentemente acessíveis para operação ágil com uma mão.
