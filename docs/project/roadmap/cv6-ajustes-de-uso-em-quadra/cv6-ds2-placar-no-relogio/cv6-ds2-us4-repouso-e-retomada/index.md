---
code: CV6.DS2.US4
level: User Story
status: Done
status_reason: implementação e validação disponível aceitas pelo Navigator; Wear 0.25.0. Cenários físicos adicionais e pausa de animação/sensor permanecem documentados como limitações/follow-up.
updated: 2026-09-28
---

# CV6.DS2.US4 — Apagar a tela e retomar pelo pulso

## Intent

Como jogador, quero que a tela apague quando não a consulto e volte ao levantar o pulso, para retomar a partida sem reabrir o aplicativo ou perder a conexão.

## Scope

- Investigar repouso de tela e retomada pelo gesto do sistema no relógio real.
- Preservar vínculo, sala, placar, fila e continuidade da conexão enquanto a tela está apagada.
- Revisar o comportamento atual de tela sempre acesa.

## Acceptance / Done Condition

- Dado o placar aberto, quando abaixo o pulso e deixo de consultar a tela, então ela pode apagar sem encerrar o aplicativo.
- Quando levanto o pulso, então retorno diretamente ao placar, sem seleção de sala, novo pareamento ou reconexão manual.
- Com rede disponível, durante o repouso, então a conexão permanece ativa e o placar retomado inclui atualizações recebidas.
- Dada queda real de rede durante o repouso, quando ela retorna, então ocorre reconciliação automática sem perder ou duplicar pontos.

## Validation Route

No relógio real, repetir ciclos de abaixar/levantar o pulso; enquanto apagado, marcar no telefone e verificar conexão com evidência de transporte, não apenas pela UI. Repetir com queda de rede de 30 segundos e treino ativo. Aprova se satisfaz continuidade e retomada; falha se fecha o app, perde estado ou exige ação manual.

Aplicar também a [matriz comum](../../index.md#validação-comum). Roteiro e evidência do Checkpoint 2 em [test-guide.md](test-guide.md).

## Out of Scope

Mudanças não descritas nesta HU, novas regras de jogo e alterações de permissões.

## Notes

Investigação obrigatória antes de implementar: ciclo de vida, restrições de execução em segundo plano, gesto, configurações do sistema e custo de bateria. Revisita CV3.DS2.US1 (tela sempre acesa). Conexão mantida e reconexão automática são resultados distintos; se o sistema não permitir o pedido integral, apresentar limites e alternativa ao Navigator antes de mudar o aceite.

Origem: rodada de feedback do Navigator em 27/09/2026. Plano aceito e implementação entregue no Wear 0.25.0; backend/web não mudam. O Navigator aceitou evidência inicial via ADB (60 s em Dozing, serviço foreground e WebSocket sem fechamento). Gesto físico, mensagem recebida durante repouso, queda de rede, treino ativo e bateria não foram observados. A pausa de animação e frequência cardíaca prevista no plano também ficou pendente; ver [revisão](review.md) e [roteiro de validação](test-guide.md).
