---
code: CV8.DS7.US16
level: User Story
status: Done
status_reason: validada pelo Navigator em produção em 2026-10-08 (anulou a partida presa e revinculou a quadra)
updated: 2026-10-08
---

# Anular partida chamada

## Intent

**Como** operador, **quero** anular a partida chamada quando a quadra sumiu ou o jogo parou no meio, **para** seguir a rodada sem cancelá-la.

## Acceptance

- **Dado** uma partida chamada **quando** a quadra vinculada some (restart, validade de 1 h, liberada) **então** o painel mostra "indisponível — anule a partida para trocar de quadra" e o botão "Anular partida".
- **Dado** uma partida chamada (quadra viva ou não) **quando** o operador anula e confirma **então** a partida não conta, os dois times voltam a ser a próxima partida, a rodada segue e os controles da quadra voltam.
- **E** o placar da quadra não é tocado.
- **Dado** uma partida chamada **quando** a rodada é cancelada **então** a chamada é apagada e o vínculo da quadra pode ser trocado; o joguinho pode ser encerrado.
- **E** bancos antigos com chamada pendurada em rodada cancelada deixam de travar o vínculo.

## Design

- `POST /api/rodada/anular-partida` → `rodada.anular_partida` apaga a linha `chamada` (como o `_desfazer_chamada` da ponte). `conducao.pode_anular`.
- A trava `_exigir_sem_partida_chamada` passou a olhar só a rodada `em_andamento`.
- **Rejeitado:** permitir revincular com a partida chamada. A chamada guarda o código da quadra antiga, então o encerramento continuaria lendo a quadra morta. O caminho é anular → (criar/vincular quadra) → chamar.

## Validation Route

No Checkpoint 2 (conversa de 2026-10-08) e no `CHANGELOG.md` 0.46.2. Testes: `tests/test_encerramento.py` (6 novos) e `web/e2e/conducao.spec.js` ("quadra some com partida chamada…").

## Follow-up

- Depois de anular um jogo parado no meio com a quadra viva, chamar de novo é recusado enquanto o placar tiver pontos ("encerre ou reinicie no placar antes"). Se incomodar, a anulação pode reiniciar o placar como admin.
