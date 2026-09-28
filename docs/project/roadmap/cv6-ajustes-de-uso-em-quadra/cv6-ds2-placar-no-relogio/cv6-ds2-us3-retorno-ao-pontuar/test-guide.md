# CV6.DS2.US3 — Validação do retorno ao pontuar

Checkpoint 2: validação física pendente. Branch `feature/cv6-ds2-us3-retorno-ao-pontuar`.

## Preparação

- APK release: `wear/app/build/outputs/apk/release/app-release.apk`, versão 0.24.1, código 12. Backend sem mudança nesta HU.
- Instalar sobre o release existente: `adb -s <endereço-do-watch> install -r wear/app/build/outputs/apk/release/app-release.apk`. Não desinstalar nem apagar dados.
- No telefone, abrir https://placar.elijunior.click, criar ou entrar numa quadra de teste e vincular o relógio, se necessário. Passar o controle ao relógio. Manter telefone e Watch na mesma quadra.
- Habilitar sons de toque do sistema, volume de sistema audível e modo Som no relógio; desativar Não perturbe para o cenário com áudio.

## Cenários e resultado esperado

1. Marcar A, depois B. Cada toque aceito destaca somente sua equipe por 200 ms, mantém uma bolinha de vôlei no canto da equipe do último ponto, vibra e pede um som curto ao sistema. O número transiciona; telefone recebe exatamente um ponto por toque.
2. Marcar duas vezes seguidas na mesma equipe, depois alternar equipes. Cada gravação renova o retorno; o próximo comando continua disponível. Toques ignorados durante gravação não sinalizam novo ponto.
3. Marcar por engano e tocar **Voltar Ponto** imediatamente. A bolinha volta para a equipe do ponto anterior (ou some ao zerar), o número diminui e os dois aparelhos convergem. A faixa de desfazer permanece acessível durante o destaque.
4. Ativar silêncio, depois Não perturbe e depois desligar sons de toque. Repetir marcações em cada configuração: sem som, com indicação visual. Restaurar as preferências anteriores ao fim.
5. Desativar animações nas configurações do sistema. O número muda sem deslocamento e a bolinha continua visível. Restaurar a preferência ao fim.
6. No telefone, assumir o controle. Tocar nas equipes no Watch: não marca, não muda a bolinha e não emite retorno de ponto. Marcar no telefone: número no relógio atualiza, a bolinha acompanha a equipe do último ponto, sem som ou vibração de marcação local.
7. Devolver o controle ao Watch; deixá-lo sem rede por cerca de 30 s (desligar também Wi-Fi/Bluetooth se necessário). Marcar A e B. Há retorno local e indicação de pendentes; o telefone ainda não recebeu. Reconectar: dois pontos chegam uma única vez; a sincronização não repete som, vibração ou destaque de toque.
8. Repetir offline; assumir controle no telefone e marcar antes de reconectar o Watch. Ao reconectar, a fila conflitante é descartada com o aviso existente; nenhum novo sinal de ponto é emitido pelo descarte. O retorno original significou registro local pendente, não confirmação do servidor.
9. Observar a leitura com placar de três dígitos e fonte ampliada: a bolinha não pode impedir a leitura do número nem cobrir ações. Repetir marcação com treino do Samsung Health ativo.

**Aprova:** sinais perceptíveis no aparelho real, ligados à equipe tocada, sem bloquear correção ou duplicar sinais no reenvio; silêncio e animações desativadas respeitados; placares convergem.

**Falha:** retorno em toque recusado, áudio no silêncio, repetição ao sincronizar, perda/duplicação de pontos, sobreposição ilegível ou desfazer inacessível. Ausência de som com ajustes habilitados precisa ser investigada no aparelho antes do aceite.

## Evidência automatizada

```sh
JAVA_HOME=/home/eli/.sdkman/candidates/java/21.0.7-tem ./wear/gradlew -p wear testDebugUnitTest assembleDebug lintDebug assembleRelease
```

59 testes passaram, sem falhas. Três cenários novos exercitam fila real em arquivo, retorno por equipe, repetição na mesma equipe, perda de resposta/reenvio, snapshots repetidos, reabertura, desfazer, falta de controle e falha de disco. O marcador persistente também é testado com desfazer, sincronização, reabertura, ponto de outro cliente e nova partida. Build e lint passaram. JVM não prova áudio, legibilidade nem vibração no hardware.

Não reiniciar o servidor de produção para esta HU: o reset configurado apaga quadras e vínculos. Repouso/conexão em segundo plano pertencem à US4.

## Decisão de áudio

Usar `AudioManager.playSoundEffect(FX_KEY_CLICK)` sem volume explícito; a plataforma respeita a configuração de sons de interface. Há também bloqueio explícito em modo silencioso/vibração e Não perturbe. Sem nova permissão, dependência ou configuração no app.

Referência: [AudioManager](https://developer.android.com/reference/android/media/AudioManager#playSoundEffect(int)).

## Ajuste pedido na validação

O Navigator considerou o `+1` rápido demais e pediu uma bolinha de vôlei persistente na equipe do último ponto. A bola deriva da pilha de pontos válidos (confirmados + fila), acompanha desfazer e atualizações do telefone, e some com a pilha vazia. Destaque de 200 ms, som e vibração continuam exclusivos do toque local aceito.

Ajuste adicional do Navigator: recuar a bola para não encostar no aro (14 dp da lateral e 10 dp da base do cartão) e substituir Nós/Eles por Equipe A/Equipe B nos rótulos padrão. Conferir no mostrador circular, com a bola em ambos os lados; Equipe A azul e B laranja. Títulos usam até 16 sp; nomes personalizados dos jogadores aparecem um por linha.

Validar também duplas personalizadas (ex.: Eli Junior / Camila e Rafa / Marvin): cada jogador ocupa sua própria linha, com cabeçalhos de mesma altura nos dois lados. Com apenas uma equipe personalizada, a outra mantém seu rótulo padrão. Nome de equipe sem lista de jogadores aparece por extenso. Conferir que nomes longos cabem, os números seguem alinhados e a bola mantém folga do aro.
