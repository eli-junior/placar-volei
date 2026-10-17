---
code: CV8.DS7.US21
level: User Story
status: Validated
status_reason: validada pelo Navigator em 2026-10-17 (0.57.0); antes Deferred pela decisão A (2026-10-08)
updated: 2026-10-17
related:
  - ../../regras-de-negocio.md
  - ../../../../decisions/records/2026-10-17T1200Z-vitoria-por-wo-em-partida-abandonada.md
---

# Resultado de partida abandonada

## Intent

**Como** operador, **quero** dar a vitória a um time numa partida que não vai terminar no placar (time foi embora, chuva, lesão), **para** que ela conte na rodada sem precisar anular (QA F1.2, F1.3).

## Acceptance / Done Condition

- **Dado** a partida Time 1 × Time 3 chamada, placar 4 × 2,
- **Quando** o operador escolher "Dar a vitória (W.O.)" ao Time 3 e confirmar,
- **Então** a partida encerra com o Time 3 vencedor, marcada W.O. e com o placar parcial no histórico,
- **E** o Time 1 é eliminado e a rodada segue (rei, mata-mata, triângulo; desfazer vale),
- **E** a nota não muda e a partida fica fora do saldo e da Resenha, mas conta no tempo sem jogar.

## Perguntas respondidas (Navigator, 2026-10-17)

- Placar parcial **não** dá vitória automática: o operador escolhe; quem lidera vem pré-selecionado.
- W.O. **não** mexe na nota e fica **fora do saldo e da Resenha**.
- Fica **só no joguinho**, não na linha do tempo do placar.

## Validation Route

[test-guide.md](test-guide.md).

## Out of Scope

Lançar placar à mão; W.O. antes de chamar a partida (há *Retirar* e *Pular*); contar o W.O. como partida jogada na Resenha.
