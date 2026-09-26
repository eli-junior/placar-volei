# Plano — CV3.DS2.US2: dados do treino no placar

Branch: `feature/cv3-ds2-us2-frequencia-cardiaca-no-placar`, criada da `master` em `8308341` (0.10.1). Versão alvo: `0.11.0` (minor, nova capacidade).

## Direção do Navigator (2026-09-26)

Ver no placar do relógio a frequência cardíaca e a duração do exercício enquanto o Samsung Health grava o treino. A duração do Samsung Health não é legível por outros apps; o Navigator aprovou como substituto um cronômetro da partida a partir do primeiro ponto.

## Escopo

1. **Servidor**: `estado_partida` ganha `iniciada_em` (hora do primeiro `PONTO_MARCADO` da partida, mesmo que desfeito depois) e `encerrada_em` (hora do ponto ativo que encerrou a partida; `null` enquanto aberta). Campos aditivos, calculados na projeção a partir de `criado_em` dos eventos; nada muda no banco.
2. **Relógio — cronômetro**: `mm:ss` (ou `h:mm:ss` depois de 1 h) = `(encerrada_em ?: agora) − iniciada_em`, atualizado a cada segundo. Sem ponto confirmado, não aparece. Partida encerrada congela; desfazer o ponto da vitória retoma.
3. **Relógio — frequência cardíaca**: `MeasureClient` do Health Services (`HEART_RATE_BPM`), registrado só com o placar visível e cancelado ao sair. Permissão pedida uma vez ao abrir o placar (`BODY_SENSORS` e `android.permission.health.READ_HEART_RATE`). Negada: não aparece. Sem leitura válida: `♥ --`.
4. **Tela**: linha no topo, centrada na bolinha de conexão: `♥ 132  ●  23:41`. O aviso de motivo (fim de partida) desce para não encostar.

## Aceite

- Dado um treino de Vôlei ativo no Samsung Health e o placar aberto, então a frequência aparece e atualiza, e o Samsung Health continua gravando e registra o treino inteiro ao encerrar.
- Dada uma partida com o primeiro ponto marcado às 20:00, quando o relógio mostra o placar às 20:23:41, então o cronômetro mostra `23:41`, igual após reiniciar o app.
- Quando a partida encerra, o cronômetro para; desfazer o ponto da vitória faz ele voltar a correr.
- Sem permissão de sensor, o placar funciona igual, só com o cronômetro.
- A frequência cardíaca não sai do relógio.

## Decisões

- Cronômetro pelo horário do servidor, não do relógio: o mesmo em qualquer aparelho e resistente a reinício. Rejeitado: cronômetro local ao abrir o placar (zera ao reiniciar).
- `iniciada_em` conta o primeiro ponto mesmo desfeito: a partida começou quando alguém marcou; desfazer não volta o tempo.
- `MeasureClient` em vez de `ExerciseClient`: o `ExerciseClient` encerraria o treino do Samsung Health.
- Rejeitados: Samsung Health Sensor SDK (aprovação de parceiro), ler a notificação do treino do Samsung Health (frágil, permissão de notificações).

## Ordem

1. **Prova no aparelho**: APK desta branch só com a frequência no placar. Navigator instala com o treino do Samsung Health ativo. Se o `MeasureClient` não ler ou interromper o treino, parar e reapresentar opções.
2. Servidor: campos na projeção, com testes.
3. Relógio: cronômetro (função pura testada) e linha do topo.

## Fora do escopo

Calorias e zonas do Samsung Health, dados no site, frequência no servidor, envio em segundo plano (CV3.DS1.US4).

## Riscos

- Paralelismo `MeasureClient` × treino do Samsung Health ainda não provado no Watch 8.
- Diferença de relógio entre servidor e Watch desloca o cronômetro. Ambos sincronizam pela rede; aceito sem correção. Se aparecer diferença visível, usar o horário do servidor recebido no snapshot.
- Mudança no servidor exige subir o contêiner no Mini PC, e isso apaga as salas: fazer fora de partida.
