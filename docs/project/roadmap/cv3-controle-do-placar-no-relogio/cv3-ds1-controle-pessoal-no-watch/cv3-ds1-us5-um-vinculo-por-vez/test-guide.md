# Roteiro de validação — CV3.DS1.US5

Branch: `feature/cv3-ds1-us5-um-vinculo-por-vez` (APK `0.10.0`; o servidor ainda responde `0.9.0` em `/health` até o fechamento da versão no Passo 7).

## Preparação

1. **Servidor.** No Mini PC, fora de uma partida (recriar o contêiner apaga as salas):

   ```sh
   git fetch origin
   git switch feature/cv3-ds1-us5-um-vinculo-por-vez
   git pull --ff-only origin feature/cv3-ds1-us5-um-vinculo-por-vez
   docker compose up -d --build placar
   curl -fsS https://placar.elijunior.click/openapi.json | grep -o '"substitui"' | head -1
   ```

   Passa: o último comando imprime `"substitui"`.

2. **APK.** Reinstale. Na raiz do projeto, no WSL:

   ```sh
   export PATH=/home/eli/Android/Sdk/platform-tools:$PATH
   adb connect IP_DO_WATCH:PORTA_DE_CONEXAO
   adb -s IP_DO_WATCH:PORTA_DE_CONEXAO install -r wear/app/build/outputs/apk/debug/app-debug.apk
   ```

   SHA-256 esperado: `594a09a436d25b92a000c6ae172de42c88e6dc14a28ce3381f2f3acf62ae9cd1`. O vínculo guardado pela 0.9.0 continua valendo, mas o deploy apaga as salas: o primeiro vínculo depois dele é do zero.

3. **Telas:**
   - **Telefone T1:** crie a **quadra A** como `eli`.
   - **Telefone T2** (ou navegador anônimo, como `eli`): crie a **quadra B**.
   - **Relógio:** toque **Ingressar numa quadra** (faixa inferior) e aprove o código em T1 pelo ícone do relógio. Em T1, torne **Eli (Relógio)** controlador e use **Passar controle**. Marque 1 ponto pelo relógio.

"Fechar o app" nos cenários abaixo = deslizar da esquerda para a direita (voltar) até sair para o mostrador, e abrir de novo pelo ícone.

## Cenários

### 0. Telas de vínculo (ajustes do primeiro teste físico)
- Sem vínculo, o relógio mostra só a bola quicando no centro e a faixa inferior **Ingressar numa quadra**, sem "Placar Vôlei" nem "Vínculo não encontrado".
- Com o código na tela: o código grande no centro, a dica "No telefone, toque no ícone do relógio, ao lado da engrenagem, e digite o código." e a faixa **Gerar novo código** embaixo.
- **Passa:** conteúdo centralizado, faixa inteira legível no mostrador redondo. **Falha:** texto cortado, botão solto no alto, faixa ilegível.

### 1. Reabrir o app: escolha
- Feche e abra o app.
- **Observe no relógio:** o botão **Retornar** (Quadra A) no centro e a faixa **Parear outra quadra** embaixo, os dois inteiros na tela.
- Toque **Retornar**.
- **Passa:** o placar de A volta, com o ponto marcado e o relógio no controle. **Falha:** o app entra direto no placar sem perguntar, ou "Retornar" leva à tela de vínculo.

### 2. Tela que só apagou não pergunta
- Com o placar na tela, deixe a tela apagar (ou cubra com a palma) e acenda de novo.
- **Passa:** o placar volta direto. **Falha:** aparece a tela de escolha.

### 3. Desistir do código novo
- Feche e abra o app → **Parear outra quadra**.
- **Observe no relógio:** o código de 8 dígitos, a dica e a faixa **Voltar à quadra A**. Anote o código.
- Toque **Voltar à quadra A**.
- **Observe no relógio:** o placar de A, com o controle.
- Em T2 (quadra B), tente aprovar o código anotado.
- **Passa:** T2 recusa ("Código inválido, usado ou expirado"), T1 ainda lista Eli (Relógio) e o relógio continua pontuando em A. **Falha:** T2 aceita o código, ou A perde o relógio.

### 4. Aviso de lances abandonados
- Ative o modo avião no relógio (ou afaste-o do telefone e desligue o Wi-Fi) e marque 2 pontos: a bolinha fica vermelha com "2".
- Feche e abra o app. Sem rede, **observe:** "Sem conexão. Vínculo guardado.", **Retornar** ativo e **Parear outra quadra** apagada.
- Tire o modo avião, feche e abra o app → **Parear outra quadra** (antes de tocar em Retornar).
- **Observe no relógio:** "2 lances da quadra A ainda não foram enviados. Se o novo código for aprovado, eles serão abandonados.", com **Parear mesmo assim** (vermelho) no centro e a faixa **Voltar**.
- Toque **Voltar**, depois **Retornar**.
- **Passa:** os 2 pontos saem e aparecem em T1. **Falha:** o aviso não aparece, conta errado, ou algum lance some.

### 5. Trocar de quadra
- Com o relógio no controle de A, marque 1 ponto sem rede (1 pendente) e volte a rede.
- Feche e abra o app → **Parear outra quadra** → **Parear mesmo assim**. Aprove o código em **T2** (quadra B).
- **Observe no relógio:** o placar da quadra B, sem pendentes.
- **Observe em T1 (quadra A):** Eli (Relógio) sai da lista; o controle volta para Eli; a linha do tempo mostra "Controle devolvido para Eli: relógio foi para outra quadra". O ponto pendente não entrou em A.
- **Observe em T2 (quadra B):** Eli (Relógio) na lista, como espectador.
- Feche e abra o app: agora **Retornar** mostra Quadra B.
- **Passa:** tudo acima. **Falha:** A continua listando o relógio, o controle fica preso no relógio em A, ou o ponto pendente de A aparece em B.

### 6. Vínculo inválido
- Em T2, revogue o relógio (Relógio → revogar). Feche e abra o app.
- **Passa:** o relógio mostra só a bola e **Ingressar numa quadra**. **Falha:** aparece **Retornar**.

## Condição de aprovação
Os cenários 0 a 6 passam no Galaxy Watch real, com T1 e T2 simultâneos, e nenhuma tela mostra o relógio em duas quadras ao mesmo tempo.

## Condição de falha
Qualquer lance que some sem aviso, relógio listado em duas quadras depois da aprovação, controle preso na quadra antiga, ou código cancelado aceito pelo telefone.
