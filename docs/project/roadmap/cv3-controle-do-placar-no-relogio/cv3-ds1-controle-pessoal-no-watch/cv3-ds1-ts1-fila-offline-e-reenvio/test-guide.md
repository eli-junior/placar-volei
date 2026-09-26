# Roteiro de validação — CV3.DS1.TS1

Branch: `feature/cv3-ds1-us4-offline-reconciliacao`. O servidor e o APK mudaram; a versão exibida só muda no fechamento.

## Automático

```sh
.venv/bin/python -m pytest -q          # 198 aprovados
.venv/bin/ruff check app tests
export JAVA_HOME=/home/eli/.sdkman/candidates/java/21.0.7-tem
./wear/gradlew -p wear testDebugUnitTest assembleDebug lintDebug
```

## Preparação

1. **Servidor.** No Mini PC, fora de partida. Recriar o contêiner **apaga as salas**.

   ```sh
   git fetch origin
   git switch feature/cv3-ds1-us4-offline-reconciliacao
   git pull --ff-only origin feature/cv3-ds1-us4-offline-reconciliacao
   docker compose up -d --build placar
   curl -fsS https://placar.elijunior.click/openapi.json | grep -o '"base_seq"' | head -1
   ```

   Passa: o último comando imprime `"base_seq"`.

2. **APK.** Reinstale (`adb install -r wear/app/build/outputs/apk/debug/app-debug.apk`). SHA-256: `d7a0caf13a9054b3c822649a5123a8a045509c76eeb4e467462773204ef63b1d`.

3. **Telas.** T1: crie a sala como `eli`. N2 (anônimo): entre como espectador, com a linha do tempo visível. Relógio: vincule, torne controlador e **Passar controle**.

## Cenários

### 1. Offline e reinício do app
- No relógio, ative o **modo avião** (sem Wi-Fi nem Bluetooth). Marque **A, B, A** e **desfaça** uma vez.
- **Passa:** o relógio mostra 1 × 1 e o contador de pendentes em 4. Em N2, o placar não muda.
- Feche o app (deslize para sair) e abra de novo, ainda em modo avião. Toque **Retornar à quadra**.
- **Passa:** o placar volta com 1 × 1, as 4 pendências continuam e dá para marcar mais um ponto. **Falha:** "Carregando placar…" travado, pendências zeradas ou botões bloqueados.
- Desfaça esse ponto extra e mantenha o modo avião por cerca de 30 s.

### 2. Reconexão sem duplicar
- Desligue o modo avião e deixe o app aberto.
- **Passa:** as pendências vão a zero. Em N2, o placar fica 1 × 1 e a linha do tempo mostra cada lance **uma vez**, na ordem tocada. **Falha:** algum ponto a mais, ou lances fora de ordem.

### 3. Controle volta ao relógio sem mudança na partida
- Em modo avião, marque **A**. Em T1, use **Assumir controle** e, sem pontuar, passe o controle de volta ao relógio.
- Desligue o modo avião.
- **Passa:** o ponto é aplicado sem a tela de lance retido. **Falha:** "O controle mudou" retém o lance.

### 4. Controle volta depois de outro ponto (continua recusado)
- Repita o cenário 3, mas em T1 marque um ponto para **B** antes de devolver o controle.
- **Passa:** o lance do relógio fica **retido** (tela de recusa), e o ponto de B vale. A revisão pelo telefone fica para a US4. **Falha:** o ponto do relógio é aplicado por cima.

### 5. Reinício do backend
- Com o relógio online, marque um ponto e aguarde a confirmação. Reinicie o contêiner (`docker compose restart placar`, sem rebuild).
- **Passa:** após reconectar, o placar continua igual e nenhum ponto é duplicado.

Pass condition: os cinco cenários passam. Fail condition: qualquer duplicação, perda de lance sem aviso ou fila aplicada sobre mudança alheia.
