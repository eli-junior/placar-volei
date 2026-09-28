---
status: Decided
raised: 2026-09-28
decided: 2026-09-28
deciders:
  - Navigator
  - Codex (Driver)
supersedes: []
related:
  - CV6.DS2.US4
---

# Sessão do placar do relógio durante o repouso

## Question

Como preservar a sessão do placar quando o Wear OS pausa a Activity ao apagar/escurecer a tela, sem deixar o transporte depender da tela aberta?

## Decision

O acompanhamento ativo usa um serviço foreground iniciado pelo app visível, com notificação/Ongoing Activity para voltar ao placar ou encerrar o acompanhamento. A sessão e seu WebSocket pertencem ao processo, não ao ciclo de vida da Activity. Encerrar a sessão fecha o transporte local; não apaga vínculo, fila nem partida. Não iniciar no boot nem solicitar isenção de bateria. O tipo `specialUse` descreve o acompanhamento contínuo da partida.

## Rationale

Fechar e reabrir o socket em cada pausa violaria o objetivo de continuidade e poderia exigir retomada manual. WorkManager não substitui transporte contínuo de baixa latência. Uma ação de encerramento explícita mantém o usuário no controle. O teste aceito no Galaxy Watch observou o serviço e o socket por 60 s em Dozing via ADB; isso não garante rede durante Doze ou em todos os fabricantes.

## Options Considered

- Manter apenas a tela acesa: rejeitado porque impede o repouso solicitado e mantém transporte preso à Activity.
- Reconectar somente ao voltar: rejeitado porque não mantém conexão durante o repouso.
- WorkManager: rejeitado para a sessão de socket contínua.
- Serviço foreground com Ongoing Activity: escolhido para manter sessão explícita e oferecer retorno/encerramento visíveis.

## Consequences

O serviço só começa após o usuário vincular/abrir acompanhamento; a notificação permite retornar ou encerrar. Restrições de Doze ainda podem atrasar rede. Gesto físico, atualização remota durante repouso, queda de rede, treino ativo e bateria seguem sem validação observada; animação Compose e leitura de batimento não são pausadas pelo modo ambiente.

## Review Trigger

Revisitar se validação em uso normal perder atualizações, interromper Samsung Health, mostrar consumo inviável ou se regras do Android/Wear OS sobre `specialUse` mudarem.
