---
id: debt-quadra-local-so-atende-relogio-com-tela-acesa
status: Carried
kind: architecture
severity: medium
source: CV7.TS3
revisit_trigger: Na quadra, a tela do celular apagar com frequência durante a partida e o relógio ficar sem confirmar os lances (pelo uso real da CV7.US2)
closure_condition: O celular aplicar os lances do relógio no processo nativo (plano C: regras também em Java, log com um escritor só) e responder com a tela apagada
---

# Quadra Local só Atende o Relógio com a Tela Acesa

## Description

As regras da quadra local rodam em JS no WebView, e o spike da CV7.TS3 mostrou que o WebView escondido para de executar JS cerca de 2 minutos depois de a tela apagar, mesmo com serviço em primeiro plano e wake lock parcial. Com a tela do celular apagada, o relógio não recebe resposta. A sala local mantém a tela acesa (wake lock da página) e a fila offline do relógio guarda os lances até o celular voltar; ao voltar, eles entram em ordem, uma vez só (recibos por id).

## Carrying Reason

Decisão do Navigator (plano B, 2026-10-02): é o caminho mais simples e já provado. O plano C é uma terceira cópia das regras (Python, JS, Java) com o log passando a ter dois escritores, e só vale se o uso real mostrar que a tela apaga demais.

## Updates

- 2026-10-02 (CV7.US2): o relógio segue o celular pelo sinal de vida (a cada 20 s, validade de 90 s), que também depende do JS. Com a tela do celular apagada o sinal para em ~2 min; sem lances na fila o relógio volta à tela do servidor ~3,5 min depois, e com lances na fila ele mantém a quadra local com o anel vermelho até a fila esvaziar ou o celular fechar a sala. Quando o JS volta (tela acesa), o relógio reentra na quadra local sozinho.

## Notes

Ver `docs/process/worklog/entries/2026-10-02T2000Z-claude-cv7-ts3-spike-webview-tela-apagada.md`. O plano C pode reaproveitar a estratégia de fixtures de paridade da CV7.TS2 estendida ao Java.
