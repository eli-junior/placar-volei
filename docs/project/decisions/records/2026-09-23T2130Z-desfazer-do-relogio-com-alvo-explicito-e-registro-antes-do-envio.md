---
id: desfazer-do-relogio-com-alvo-explicito-e-registro-antes-do-envio
status: Decided
raised: 2026-09-23
decided: 2026-09-23
deciders:
  - Eli (Navigator)
  - Claude Opus 5.5 (Driver)
supersedes:
related:
  - CV3.DS1.US3
  - CV3.DS1.US4
---

# Desfazer do Relógio com Alvo Explícito; Ponto e Desfazer Registrados Mesmo Antes do Envio

## Question

O relógio pode estar atrasado em relação ao servidor e pode desfazer sem rede, antes de o ponto sair da fila. O que o desfazer do relógio desfaz, e o que fica registrado quando o ponto e a correção acontecem ainda no aparelho?

## Decision

- O desfazer do relógio aponta para **o ponto que o relógio mostrou no topo**: `alvo_seq` para um ponto confirmado, `alvo_comando` para um lance ainda na fila. O servidor só aplica se o alvo ainda for o último ponto ativo. Caso contrário, recusa, não toca em nenhum ponto, e o relógio retém a fila até o descarte explícito.
- Ponto e desfazer são sempre enviados. Um toque acidental corrigido antes do envio aparece na linha do tempo como ponto + ponto desfeito, como no site. O lance pendente não é apagado no relógio.
- Só o topo é desfazível, como no site. O desfazer não pede confirmação.

## Rationale

- Um "desfazer o último" genérico, vindo de um relógio atrasado, apagaria um ponto que o Eli nunca viu: placar errado sem rastro, a pior falha do produto.
- Apagar o lance pendente no próprio relógio cria uma corrida com o envio: o lance pode já estar a caminho, e o resultado seria um ponto aplicado sem a correção. Enviar os dois é determinístico e segue "nada é apagado".
- Pedir confirmação contraria "corrigir é tão barato quanto marcar".

## Options Considered

- Desfazer "o último ponto" sem alvo: rejeitado pelo atraso do relógio.
- Cancelar localmente o lance ainda não enviado: rejeitado pela corrida e pela perda do registro. Foi a alternativa apresentada ao Navigator, que escolheu o registro.
- Toque longo ou confirmação: rejeitado pelo princípio de correção barata.

## Consequences

- A linha do tempo pode mostrar pares ponto + desfeito criados offline. É esperado.
- A US4 (reconciliação) deve respeitar o alvo: um desfazer nunca é reescrito para outro ponto durante a reconciliação.
- O recibo guarda o alvo (`watch_recibos.alvo`), e reenviar o mesmo `id` com outro alvo é 409.

## Review Trigger

Se o relógio passar a permitir desfazer um ponto fora do topo, ou se a US4 introduzir revisão de fila no telefone que reordene lances.
