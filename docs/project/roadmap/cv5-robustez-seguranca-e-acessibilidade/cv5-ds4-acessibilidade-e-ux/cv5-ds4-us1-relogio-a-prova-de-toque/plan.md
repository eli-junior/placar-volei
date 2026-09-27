# Plano — CV5.DS4.US1 Relógio à prova de toque acidental

- **Nível:** User Story · **Branch:** `feature/cv5-ds4-us1-relogio-a-prova-de-toque` · **Versão:** patch (APK)

## Scope
1. **"▶ Nova" em dois toques** (`ScoreScreen.kt`, `UndoAndNewBar`): o primeiro toque troca o rótulo para "Tocar de novo" com fundo âmbar e vibração curta; o segundo, em até 3 s, inicia a partida (vibração CONFIRM). Sem o segundo toque, volta ao normal.
2. **Desfazer com contexto:** o rótulo vira "↶ Desfazer +1 {equipe}" usando o ponto do topo que a `ScoreSync` já conhece (`ScoreSync.kt:52`); o `contentDescription` diz "Desfazer o último ponto de {equipe}". Na faixa dividida, só o `contentDescription` muda (falta espaço).
3. **Textos maiores:** motivo de bloqueio e avisos do descarte de 11sp para 13sp; contador na bolinha de 10sp para 11sp com a bolinha de 18 para 22dp.
4. **Número previsto:** o traço já existe; o `contentDescription` do número ganha "(enviando)".
5. Padding horizontal do `ReasonText` passa a depender de `isScreenRound` (36dp redondo, 16dp quadrado).

## Acceptance
- Dado o fim da partida, quando toco "Nova" uma vez, então nada reinicia; quando toco de novo em até 3 s, então a partida nova começa.
- Dado o último ponto do Time Azul, então o desfazer diz "Desfazer +1 Azul" e o TalkBack lê "Desfazer o último ponto de Time Azul".
- E os textos de bloqueio cabem sem corte no Galaxy Watch 8 de 40 mm.

## Design
Dois toques em vez de toque longo: toque longo é pouco descobrível e confunde com o gesto do sistema. Desfazer continua com um toque (é a correção frequente, e é reversível).

## Out of Scope
Confirmação na web (já abre modal).

## Validation
Testes JVM do rótulo do desfazer; roteiro físico no relógio de 40 mm com TalkBack.
