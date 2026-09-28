---
date: 2026-09-28T19:00:00Z
author: Codex (Driver)
kind: milestone
related:
  - CV6.DS2.US4
verification:
  - JAVA_HOME=/home/eli/.sdkman/candidates/java/21.0.7-tem ./wear/gradlew -p wear testDebugUnitTest assembleDebug lintDebug assembleRelease
  - Galaxy Watch SM-L330/Android 16: serviço foreground e WebSocket ativos por 60 s em Dozing via ADB
---

# Repouso e retomada do placar no relógio

## What changed

O Wear 0.25.0 remove a trava de tela acesa e mantém a sessão do placar em serviço foreground com Ongoing Activity, retorno ao app e ação para encerrar acompanhamento. A Activity recriada reutiliza o mesmo proprietário de sessão no processo.

## Why it matters

O relógio pode repousar sem fechar o transporte apenas por sair de RESUMED, e a pessoa tem uma notificação para voltar ou encerrar a sessão.

## Verification

59 testes passaram; builds debug/release e lint concluídos. No Galaxy Watch SM-L330/Android 16, o sistema confirmou notificação concedida, serviço foreground e WebSocket sem fechamento durante 60 s em Dozing via ADB. Navigator aceitou essa evidência limitada.

## Follow-up

Gesto físico, atualização remota durante repouso, queda de rede, treino ativo e bateria não foram observados. Animações e leitura de frequência cardíaca não são pausadas no repouso. Esses limites estão registrados no roteiro, revisão e decisão da US4; o débito de testes de interface foi atualizado.
