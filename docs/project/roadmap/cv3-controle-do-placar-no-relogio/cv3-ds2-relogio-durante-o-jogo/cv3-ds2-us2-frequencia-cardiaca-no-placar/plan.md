# Plano — CV3.DS2.US2: frequência cardíaca no placar

Branch: `feature/cv3-ds2-us2-frequencia-cardiaca-no-placar`, criada da `master` em `8308341` (0.10.1). Versão alvo: `0.11.0` (minor, nova capacidade).

## Direção do Navigator (2026-09-26)

Ver a frequência cardíaca no placar do relógio enquanto o Samsung Health grava o treino. A duração do exercício do Samsung Health não é legível por outros apps. O cronômetro da partida proposto como substituto foi **retirado** pelo Navigator no Checkpoint 1: fica só o batimento.

## Escopo

1. `MeasureClient` do Health Services (`HEART_RATE_BPM`), registrado só com o placar visível e cancelado ao sair.
2. Permissão pedida uma vez, ao abrir o placar pela primeira vez (`BODY_SENSORS`; o manifest declara também `android.permission.health.READ_HEART_RATE`, do Wear OS 6). Negada: nada aparece.
3. Topo do placar: `● ♥ 132`, ao lado da bolinha de conexão. Sem leitura válida: `♥ --`.
4. Nada muda no servidor.

## Aceite

- Dado um treino de Vôlei ativo no Samsung Health e o placar aberto, então a frequência aparece e atualiza, e o Samsung Health continua gravando e registra o treino inteiro ao encerrar.
- Sem permissão de sensor, o placar funciona igual, sem o batimento.
- A frequência cardíaca não sai do relógio.

## Decisões

- `MeasureClient` em vez de `ExerciseClient`: o `ExerciseClient` encerraria o treino do Samsung Health.
- Rejeitados: Samsung Health Sensor SDK (aprovação de parceiro), ler a notificação do treino do Samsung Health (frágil, permissão de notificações), cronômetro da partida (retirado pelo Navigator).

## Fora do escopo

Duração, calorias e zonas do Samsung Health; dados no site; frequência no servidor; envio em segundo plano (CV3.DS1.US4).

## Riscos

- Paralelismo `MeasureClient` × treino do Samsung Health ainda não provado no Watch 8: o teste físico é a prova. Se falhar, parar e reapresentar opções.
- `targetSdk 35` no Wear OS 6: o pedido de `BODY_SENSORS` deve valer pela compatibilidade; confirmar no aparelho.
