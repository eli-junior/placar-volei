---
date: 2026-09-27T19:00:00Z
author: Codex (Driver)
kind: milestone
related:
  - CV6.DS2.US1
verification:
  - 52 testes JVM do relógio
  - 221 testes backend
  - build debug/release e lint Android
  - Svelte Check sem erros ou avisos
  - validação manual do Navigator no Galaxy Watch real
---

# CV6.DS2.US1 validada no relógio

## What changed

O placar passou a ajustar os números à área disponível usando Teko local, centralizou o indicador de batimentos e reservou espaço para avisos e ações. O controle no telefone usa mensagem curta; a correção é **Voltar Ponto**; **Nova** aparece verde e continua protegida por dois toques.

## Why it matters

O jogador consegue ler 0, 12 e 100 no pulso sem perder as ações de correção e nova partida. A mensagem acessível continua dizendo qual equipe teve o último ponto, mesmo com o rótulo visual curto.

## Verification

O APK release foi instalado no Galaxy Watch SM-L330 sem apagar o vínculo. O Navigator validou a leitura e o fluxo no aparelho. Os testes automatizados passaram; a ausência de testes de tela do relógio permanece no débito técnico existente.

## Follow-up

Fechar a HU após o Checkpoint 4 e integrar a branch. A próxima HU do relógio é `CV6.DS2.US2`, com plano aprovado para o aro de conexão.
