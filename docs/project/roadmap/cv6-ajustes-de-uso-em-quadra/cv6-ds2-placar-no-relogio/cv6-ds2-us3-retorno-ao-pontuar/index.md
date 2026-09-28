---
code: CV6.DS2.US3
level: User Story
status: Active
status_reason: plano aceito; implementação em validação no Checkpoint 2
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

Aplicar também a [matriz comum](../../index.md#validação-comum). Este roteiro é para a futura implementação; não representa testes já executados.

## Out of Scope

Mudanças não descritas nesta HU, novas regras de jogo e alterações de permissões.

## Notes

Investigar áudio e animação no dispositivo. Decidir padrão/controle do som e se sinais também ocorrem em pontos originados no telefone. Não prometer prevenção do toque acidental: o objetivo é percebê-lo.

Origem: rodada de feedback do Navigator em 27/09/2026. Dependências técnicas, desenho final e versão serão definidos no checkpoint de planejamento da implementação.

