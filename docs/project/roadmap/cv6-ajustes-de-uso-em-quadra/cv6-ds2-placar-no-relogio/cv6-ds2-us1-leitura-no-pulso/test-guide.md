# Validação — CV6.DS2.US1

## Estado no Checkpoint 2

Implementada; aceite manual pendente. Nenhum merge ou publicação de versão feito. O APK ainda informa 0.20.0; a versão proposta 0.20.1 será consolidada no fechamento.

## Evidência automatizada

Na raiz do repositório:

```sh
JAVA_HOME=/home/eli/.sdkman/candidates/java/21.0.7-tem ./wear/gradlew -p wear testDebugUnitTest assembleDebug lintDebug
.venv/bin/pytest -q
npm --prefix web run check
git diff --check
```

- Relógio: 52 testes, zero falhas (inclui dois cenários novos: mensagem curta com bloqueio de comandos e prioridade da recusa de fila).
- Backend: 221 aprovados; quatro avisos de depreciação de dependências.
- Android: APKs debug e release compilados; lint com zero erros e 12 avisos em dependências/uso de KTX fora dos arquivos alterados.
- Svelte Check: zero erros e zero avisos. Não houve alteração na interface web.
- Fonte Teko original incorporada ao APK com licença OFL e origem em `assets/licenses/`; nenhuma busca de fonte durante o uso.

## Inspeção visual feita pelo Driver

Usado Galaxy Watch SM-L330, 480 × 480, densidade 340 dpi. Cópia temporária em `/tmp/cv6-watch-preview`, pacote separado `br.com.placarvolei.watch.preview`, usando o mesmo ScoreScreen com snapshots e batimentos simulados. Não conectou a uma quadra nem alterou dados do app principal.

Inspecionados 0, 12 e 100, batimento indisponível, controle no telefone, fim de partida, iniciais e fonte ampliada em 30%. Também simulada área de 192 dp via densidade apenas na cópia: a mensagem pode ocupar duas linhas, e os números reduzem para preservar o conteúdo. A legibilidade nessa configuração extrema depende do aceite do Navigator.

[Fim de partida e Nova verde](evidence/green.png), [placar zerado sem batimento](evidence/zero.png) e [192 dp com fonte ampliada](evidence/small.png). Os batimentos visíveis nessas capturas são simulados.

Capturas comprovam renderização; não comprovam coleta real do sensor, gravação no Samsung Health, sincronização ou aceite de legibilidade. Esses itens ficam no roteiro abaixo.

## Preparar o app real

APK debug: `wear/app/build/outputs/apk/debug/app-debug.apk`, servidor compilado `https://placar.elijunior.click`. O relógio conectado recusou debug por assinatura diferente; atualização deve usar o release assinado com a chave local, sem desinstalar o app principal.

O release `wear/app/build/outputs/apk/release/app-release.apk` foi instalado com sucesso via `adb install -r` no SM-L330 em 2026-09-27, preservando dados; a cópia temporária foi removida e o app principal aberto. SHA-256: `33368a5ffc952faaab698c7f619b72506472d9d84ec74dc8c77a679076bec391`.

Para reinstalar, na raiz, com depuração Wi-Fi conectada (IP e porta podem mudar):

```sh
/home/eli/Android/Sdk/platform-tools/adb devices -l
/home/eli/Android/Sdk/platform-tools/adb -s IP:PORTA install -r wear/app/build/outputs/apk/release/app-release.apk
```

Usar o pacote principal `br.com.placarvolei.watch`, app **Placar Vôlei**. Se o app instalado tiver assinatura de release, o Android recusará a atualização com debug: gerar o release com a mesma chave conforme `wear/README.md`; não desinstalar para contornar, pois isso apagaria vínculo/fila. Não reiniciar servidor nem recriar contêiner para esta validação.

## Roteiro do Navigator

1. **Preparação:** no telefone, abrir https://placar.elijunior.click e criar uma quadra de teste como Eli. Em outro navegador/sessão, entrar como espectador. Vincular o relógio pelo botão Relógio e código de pareamento, conforme `wear/README.md`.
2. **Sem controle:** manter o controle no telefone. O relógio deve mostrar exatamente **Controle no telefone.**; toques nos pontos não mudam a contagem. Observar o mesmo placar nos três clientes.
3. **Leitura:** configurar alvo 100 (sem teto, com vantagem) e conferir 0, 12 e 100 no relógio. Para chegar a 100 sem encerrar antes, alternar os pontos dos times até 100 × 100. Rótulos devem ficar acima dos números; conferir também jogadores cadastrados, que viram iniciais. Comparar fonte padrão e tamanho de fonte ampliado do relógio.
4. **Controle e correção:** no telefone, tornar Eli (Relógio) controlador e passar o controle. Marcar A/B, desfazer e conferir a transição dos números, a linha do tempo e os três placares. Repetir com animações desativadas na acessibilidade do relógio; ao terminar, restaurar a preferência anterior.
5. **Batimentos:** com permissão, conferir o indicador centralizado. Com leitura indisponível, observar **♥ --**; com permissão negada, indicador oculto. Com Samsung Health gravando um treino, voltar ao placar e depois conferir que o treino continua. Não usar o número simulado da prévia como prova de medição.
6. **Fim de partida:** como dono admin, terminar o jogo usando o relógio. **Desfazer** deve continuar acessível e **Nova** ter fundo verde com texto branco. Primeiro toque em Nova mostra **Tocar de novo** em âmbar; esperar três segundos deve voltar ao verde. Dois toques dentro do prazo iniciam outra partida, sincronizada no telefone/espectador.
7. **Conexão:** durante partida de teste, isolar o relógio da rede por cerca de 30 s (desligar também Wi-Fi se o modo avião não o fizer), marcar um ponto e observar pendência/placar previsto. Reconectar e conferir um único ponto no histórico e os três placares iguais, sem avisos sobrepostos.

**Passa:** números completos, melhor leitura no aparelho habitual, batimentos centralizados e honestos, ações acessíveis, Nova verde preservando confirmação e placares sincronizados.

**Falha:** recorte na borda circular, sobreposição, número ilegível, medição inventada, treino interrompido, ação disparada indevidamente ou divergência de placar.

## Arquivos desta implementação

- `ScoreScreen.kt`: organização do espaço, números Teko ajustados por medição, batimentos 17 sp e cor de Nova.
- `ScoreSync.kt` e `ScoreSyncTest.kt`: mensagem curta e regressões de bloqueio/prioridade de conflito.
- `res/font/teko.ttf` e `assets/licenses/teko-*`: fonte e licença incorporadas.
- Changelog, índice/plano da HU e este roteiro: estado, pedido adicional e evidência.

Após o Navigator validar, seguir ao Passo 5 (revisão e dívida); documentação final e versão permanecem para os checkpoints seguintes.
