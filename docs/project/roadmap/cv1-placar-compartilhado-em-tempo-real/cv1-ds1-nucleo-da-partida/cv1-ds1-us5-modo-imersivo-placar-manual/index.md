---
code: CV1.DS1.US5
level: User Story
status: Done
status_reason: concluída, validada pelo Navigator e verificada com testes automatizados
updated: 2026-09-14
related:
  - CV1.DS1
  - CV1.DS1.US2
  - CV1.DS4.US1
---

# CV1.DS1.US5 — Modo Imersivo e Placar Dobrável Manual para Espectador

## Intent

Proporcionar aos espectadores da partida uma experiência visual nostálgica, imersiva e de alta legibilidade, apresentando o placar como um placar manual dobrável de quadra (com anéis e cartões que viram ao pontuar). Ao tocar na tela, os controles de navegação e auditoria reaparecem, retornando automaticamente ao modo imersivo após 3 segundos de inatividade.

## Scope

- Componente de Placar Dobrável Manual estilo retrô com visual de cartões articulados por anéis no topo, vinco central e alto contraste.
- Animação de virada tridimensional (flip 3D de 180°/90°) quando um ponto é marcado ou desfeito.
- Modo Imersivo para o Espectador: ocupação ampla da tela, removendo distrações visuais quando inativo.
- Revelação sob toque: ao tocar em qualquer local da tela, exibe os controles (botão de voltar, status ao vivo, identificação do participante, botão da Linha do Tempo e lista de presentes).
- Temporizador de inatividade de 3 segundos: esconde os controles e retoma o modo imersivo suavemente após 3 segundos sem toques (suspenso quando modais estão abertos).
- Suporte a acessibilidade e `prefers-reduced-motion`.

## Acceptance / Done Condition

Given que um participante está na quadra com o papel de Espectador
When ele permanece sem interagir por 3 segundos
Then a interface entra no Modo Imersivo, destacando o placar dobrável manual e ocultando cabeçalho, botão de voltar e lista de participantes.

Given que a tela está em Modo Imersivo
When um ponto é marcado na partida
Then o cartão de pontuação da equipe correspondente vira em animação 3D fluida revelando o novo número do placar.

Given que a tela está em Modo Imersivo
When o espectador toca ou clica na tela
Then o Modo Imersivo é desativado imediatamente, exibindo o botão de voltar, cabeçalho e demais itens da quadra.

Given que os controles estão visíveis após um toque
When se passam 3 segundos sem qualquer interação e nenhum modal está aberto
Then o Modo Imersivo é reativado automaticamente.

## Validation Route

Dois dispositivos ou abas: um Controlador (para marcar pontos) e um Espectador.
Observar a entrada no modo imersivo após 3 segundos, o efeito visual do placar manual, o toque na tela para exibir o botão de voltar e o retorno automático ao modo imersivo.

## Out of Scope

- Efeitos de áudio/sonoplastia na virada dos cartões.
- Substituição da tela de toque com botões grandes de marcação do Controlador (o controlador mantém foco em marcação rápida com uma mão).
