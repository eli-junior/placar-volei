---
id: escalacao-do-parceiro-do-incompleto
status: Decided
raised: 2026-10-07
decided: 2026-10-07
deciders:
  - Eli (Navigator)
  - Claude Sonnet 5.5 (Driver)
related:
  - CV8.DS3.US8
  - encerramento-lendo-o-placar
---

# Escalação do Parceiro do Time Incompleto

## Question

Como o time incompleto (ímpar ou atrasado) escolhe o parceiro na vez dele, respeitando gênero, exclusões e o saldo das duas participações?

## Decision

- **Quando:** só com o incompleto **em quadra** e **antes** de chamar a partida; chamada em aberto recusa. **Chamar partida** fica bloqueado até a escolha.
- **Lista (RN-07), calculada no servidor na hora:** elegíveis são os jogadores dos times **eliminados** que não estão em nenhum time ativo (em quadra, fila ou rei); ficam de fora o próprio incompleto, outros incompletos e quem já foi escalado e ainda joga. O grupo "ainda não jogaram" (ímpar) existe no código mas é **vazio por construção**: o incompleto é o último da fila. O atrasado usa sempre a lista de escalação (`times.origem`).
- **Gênero (RN-01):** incompleto **homem** → só mulheres elegíveis; homem apenas se não houver nenhuma, com aviso de H+H por falta de alternativa; o servidor **recusa** H+H havendo alternativa. Incompleta mulher → qualquer um. **Ordem** por chegada.
- **Escolha:** o jogador entra no time incompleto (`time_jogadores.escalado = 1`, com a nota e a chegada do sorteio) e o time passa a completo; fica em **duas linhas**, uma em cada time, preservando o histórico das duas partidas. Revalidada na transação; escolhas simultâneas: só uma vale.
- **Painel:** o escalado sai de "Eliminados" enquanto joga pelo segundo time e volta se esse time também perder; "· escalado" ao lado do nome; **Saldo da rodada** (pontos feitos − sofridos, somando os dois times).
- **Schema 6** (aditivo): `times.origem` (`impar`|`atrasado`) e `time_jogadores.escalado`.

## Rationale

- Duas linhas (em vez de mover o jogador) mantêm o histórico e dão o saldo dobrado do CA5 sem conta especial.
- Fazer o servidor decidir a lista e revalidar a escolha evita divergência entre tela e regra.
- A coluna `origem` deixa a US9 (atrasados) só gravar `atrasado`.

## Options Considered

- H+H como aviso (contraria "gênero prevalece"); mover o escalado do time antigo; escolha automática do parceiro (a RN-05 pede que o jogador escolha).
