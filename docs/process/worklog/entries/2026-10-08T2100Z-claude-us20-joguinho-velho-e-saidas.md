---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-08
related:
  - CV8.DS7.US20
  - recriar-quadra-nao-vira-botao
---

# US20: joguinho de outro dia e mensagens que ensinam a saída (0.47.0)

- **Problema:** o joguinho de ontem não era sinalizado; "Encerrar sessão" ficava desabilitado com rodada ativa e só ensinava a saída destrutiva, sem dizer o que se perde; o motivo dos botões desabilitados ficava longe deles.
- **Entrega:** cartão de joguinho velho (continuar ou encerrar), `POST /api/sessao/encerrar` com `cancelar_rodada` atômico, confirmações que listam o que se perde (cancelar rodada e encerrar joguinho) e aviso de presença travada no topo de Presentes.
- **Decisão:** a recriação da quadra num passo só ficou fora (anular + criar e vincular já cobre).
- **Ambiente:** `pytest` oscilou numa rodada e terminou sem resumo em outra (instabilidade da máquina); reexecuções passaram.
- **Validação:** feita pelo Navigator em 2026-10-08.
