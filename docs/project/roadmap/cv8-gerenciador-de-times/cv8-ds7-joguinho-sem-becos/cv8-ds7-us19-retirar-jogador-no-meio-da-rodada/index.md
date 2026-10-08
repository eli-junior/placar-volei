---
code: CV8.DS7.US19
level: User Story
status: Active
status_reason: plano aprovado em 2026-10-08 (Checkpoint 1); implementando junto da TS3
updated: 2026-10-08
---

# Retirar jogador no meio da rodada

## Intent

**Como** operador, **quero** tirar da rodada um jogador que foi embora, **para** que ele não seja escalado de novo, sem cancelar a rodada (QA F2).

## Hoje

Presença travada com rodada ativa; inativar é recusado; a substituição (US10) exige substituto vindo da fila ou dos eliminados e é recusada com partida chamada. Sem substituto disponível não há saída além de cancelar a ## Regra (decisão C, Navigator, 2026-10-08)

- Quem sai deixa a **vaga vazia** no time. Enquanto o time está **na fila**, a vaga pode ficar vazia.
- O substituto é **obrigatório na hora de entrar em quadra**: na vez do time, a vaga é preenchida como a do time incompleto (lista de escalação, RN-07, US8).
- Time que fica **sem nenhum jogador** deixa de existir: sai da fila (e dos reis).
- Quem saiu fica ausente nas próximas rodadas (como na US10).

## Acceptance

- **Dado** um time na fila **quando** o operador retira um jogador dele **então** o jogador fica ausente, o time segue na fila com a vaga vazia e aparece como "Incompleto: escolhe o parceiro na sua vez".
- **Dado** um time com vaga vazia **quando** chega a vez dele de entrar em quadra **então** "Chamar partida" fica bloqueado até a vaga ser preenchida pela lista de escalação.
- **Dado** um time **quando** todos os seus jogadores são retirados **então** o time sai da fila e a próxima partida é recalculada.
- **E** os botões "Desmarcar" travados dizem o motivo ao lado, não só no fim da página.

## Decisões complementares (Navigator, 2026-10-08)

- **Em jogo não sai:** não é possível retirar jogador de um time que está em quadra com partida chamada. A ação fica bloqueada (com o motivo) até a partida ser encerrada ou anulada (US16).
- **Rei aguardando o mata-mata:** mesma regra. A vaga fica vazia e, na hora de entrar, o substituto é escolhido entre os eliminados, preservando o critério de time misto (RN-01, RN-07).
- **Ninguém elegível na vez de entrar:** o time é **pulado** (a próxima partida usa o time seguinte da fila).

## Decisões do plano (Navigator, 2026-10-08)

- **Relação com a US10:** **convivem**. *Substituir* = alguém entra no lugar agora; *Retirar* = sai sem substituto e a vaga espera a vez do time. Nada da US10 muda.
- **"Pular":** o time vai para o **fim da fila** (ou do rol de rivais no mata-mata) e a próxima partida usa o seguinte.
- **TS3 e US19** na mesma branch (`feature/cv8-ds7-us19-retirar-jogador`), com commits separados.
