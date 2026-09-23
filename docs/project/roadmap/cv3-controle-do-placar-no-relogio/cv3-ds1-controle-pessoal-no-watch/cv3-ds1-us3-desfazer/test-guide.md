# Roteiro de validação — CV3.DS1.US3

Branch: `feature/cv3-ds1-us3-desfazer` (APK `0.9.0`; o servidor ainda responde `0.8.0` em `/health` até o fechamento da versão no Passo 7).

## Preparação

1. **Servidor.** No Mini PC, fora de uma partida (recriar o contêiner apaga as salas):

   ```sh
   git fetch origin
   git switch feature/cv3-ds1-us3-desfazer
   git pull --ff-only origin feature/cv3-ds1-us3-desfazer
   docker compose up -d --build placar
   curl -fsS https://placar.elijunior.click/openapi.json | grep -o '"desfazer"' | head -1
   ```

   Passa: o último comando imprime `"desfazer"`. Com `/health` não dá para distinguir a branch, porque a versão só muda no fechamento.

2. **APK.** O APK mudou. Reinstale-o. Na raiz do projeto, no WSL:

   ```sh
   export PATH=/home/eli/Android/Sdk/platform-tools:$PATH
   adb connect IP_DO_WATCH:PORTA_DE_CONEXAO
   adb -s IP_DO_WATCH:PORTA_DE_CONEXAO install -r wear/app/build/outputs/apk/debug/app-debug.apk
   ```

   SHA-256 esperado: `62d45580dea91283a086441ea31fef78f23cb86581b860d3339417af5c8c311d`.

3. **Telas:**
   - **Telefone T1:** crie a sala como `eli`.
   - **Navegador N2** (anônimo): entre como espectador. Deixe a linha do tempo visível.
   - **Relógio:** vincule e aprove em T1. Em T1, torne **Eli (Relógio)** controlador e use **Passar controle**.

## Cenários

### 1. Tela de vínculo sem endereço
- Antes de vincular (passo 3), a primeira tela do relógio mostra só "Placar Vôlei", a mensagem e **Gerar código**.
- **Passa:** não há campo de endereço, e o código é gerado e aprovado normalmente. **Falha:** campo de endereço visível, ou erro de endereço ao gerar.

### 2. Desfazer um ponto confirmado
- No relógio: toque em **Nós**, depois em **Eles**. Espere o "● Conectado" sem pendentes. Toque em **↶**.
- Observe no relógio: vibração diferente da do ponto, e o número de Eles **desce** (animação invertida). O placar fica 1×0.
- Observe em T1 e N2: 1×0. Na linha do tempo, o ponto de Eles aparece desfeito por **Eli (Relógio)**.
- **Passa:** 1×0 nas três telas, com um ponto desfeito na linha do tempo. **Falha:** outro placar, ponto de Nós desfeito, ou nenhum registro na linha do tempo.

### 3. Botão indisponível
- Toque em **↶** até zerar. Com 0×0, o botão fica apagado e não responde.
- Em T1, toque **Assumir o controle**. O botão também fica apagado.
- **Passa:** nenhum desfazer sai com 0×0 ou sem o controle. **Falha:** vibração ou mudança no placar.
- Devolva o controle ao relógio (Passar controle).

### 4. Desfazer offline, antes do envio
- Coloque o relógio em modo avião (ou desligue o Bluetooth do telefone e o Wi-Fi do relógio).
- Toque em **Nós**, **Nós** e **↶**. O relógio mostra 1×0 com "3 pendentes" (dois pontos e um desfazer). O número aparece mais apagado, com o traço embaixo.
- Feche o app (deslize para sair) e abra de novo, ainda sem rede. O placar previsto e os pendentes continuam os mesmos.
- Religue a rede com o app aberto.
- **Passa:** as três telas mostram 1×0. A linha do tempo mostra dois pontos de Nós e um deles desfeito, sem duplicata. **Falha:** 2×0, 0×0, ponto duplicado ou desfazer duplicado.

### 5. Vitória e reabertura
- Marque pelo relógio até a vitória (padrão: 12 com vantagem de 2). As telas mostram a partida encerrada, e os botões de ponto do relógio travam.
- Toque em **↶**.
- **Passa:** a partida reabre em T1 e N2, e as metades do relógio voltam a aceitar toques. **Falha:** o botão desfazer travado na vitória, ou a partida continua encerrada.

### 6. Desfazer pendente com o controle retomado
- Coloque o relógio sem rede. Toque em **↶** (há pelo menos um ponto no placar).
- Em T1, toque **Assumir o controle**.
- Religue a rede do relógio.
- **Passa:** o relógio mostra o motivo ("Outro operador está no controle do placar.") e "1 lance retido fora do placar", com **Descartar**. Nenhum ponto muda em T1/N2. Descartar com confirmação limpa a retenção. **Falha:** o ponto é desfeito, ou a fila some sem confirmação.

### 7. Ergonomia (sem aprovação automática)
- Durante alguns rallies reais, registre se o **↶** recebeu toque sem querer.
- **Passa:** nenhum toque acidental, ou poucos e fáceis de perceber. **Falha:** toques acidentais frequentes. Nesse caso, reposicionar o botão vira ajuste desta HU.

## Evidência automatizada (Passo 4)
- `uv run pytest`: 166 passaram, 15 deles novos: alvo por seq e por comando, alvo desatualizado ou já desfeito, lance-alvo recusado ou desconhecido, sem ponto ativo, reenvio e 409 com outro alvo, vitória reaberta, controle retomado, formato do comando, `equipes_ativas` e migração da coluna `alvo`.
- `ruff check` e `ruff format --check`: ok.
- Web: `npm test` 27/27, `npm run check` sem erros ou avisos, `npm run build` ok.
- Android: 25 testes (7 novos: pilha prevista, alvo do topo, desfazer sem ponto, partida anterior, fila com alvo, fila da 0.8.0, corpo do comando). `assembleDebug` e `lintDebug` ok: zero erros e sete avisos conhecidos de versão de dependência.
