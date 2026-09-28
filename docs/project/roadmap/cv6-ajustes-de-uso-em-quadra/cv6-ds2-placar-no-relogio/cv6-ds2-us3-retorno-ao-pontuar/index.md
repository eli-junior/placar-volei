---
code: CV6.DS2.US3
level: User Story
status: Done
status_reason: validada no Galaxy Watch e fechamento autorizado pelo Navigator; Wear 0.24.1
updated: 2026-09-28
---

# CV6.DS2.US3 — Perceber pontos registrados pelo relógio

## Intent

Como jogador, quero receber retorno perceptível ao pontuar, para notar inclusive um toque acidental e poder desfazê-lo.

## Scope

- Avaliar e implementar retorno visual por animação e retorno sonoro conforme suporte do relógio.
- Associar o retorno à equipe e ao ponto efetivamente registrado ou pendente.
- Preservar acesso rápido ao desfazer.

## Acceptance / Done Condition

- Quando um toque registra um ponto, então um retorno perceptível permite notar a ação sem bloquear o próximo comando.
- Quando o comando é rejeitado, então não ocorre sinal enganoso de sucesso.
- Quando a fila é reenviada ou chega um snapshot repetido, então o mesmo ponto não produz repetidamente o retorno de uma nova marcação.
- Quando som ou movimento estão desativados, então permanece uma indicação visual legível.

## Validation Route

Marcar e desfazer no relógio, testar silêncio, movimento reduzido, toque rejeitado e ponto offline seguido de reconexão; conferir no telefone. Aprova se cada ação é compreensível sem duplicar pontos ou sinais; falha se houver sucesso falso ou repetição no reenvio.

Aplicar também a [matriz comum](../../index.md#validação-comum). Resultados e roteiro em [test-guide.md](test-guide.md).

## Out of Scope

Mudanças não descritas nesta HU, novas regras de jogo e alterações de permissões.

## Notes

Entrega aceita na versão Wear 0.24.1. O retorno imediato significa gravação local, com pendência indicada até o servidor confirmar. Pontos remotos atualizam o marcador, sem som/vibração de toque local. O som segue as preferências do sistema. A bola persistente substituiu o +1 transitório por pedido do Navigator.

Ajustes aprovados na validação: posição da bola, desenho e giro iguais aos da abertura, Equipe A azul/B laranja, títulos de até 16 sp e jogadores em linhas separadas. A bola deriva dos pontos ativos e acompanha desfazer, fila, reabertura e nova partida.

Revisão e coerência: [review.md](review.md). US4 permanece separada para repouso e continuidade de conexão.
