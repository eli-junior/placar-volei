# MCP de dispositivos (celular e relógio)

Servidor MCP que deixa um agente falar com os aparelhos físicos do projeto: o celular (Galaxy Z Fold) e o relógio (Galaxy Watch). Pareia, conecta, compila, instala, captura a tela, toca e lê o log, com as armadilhas deste projeto já embutidas.

Registrado no `.mcp.json` do repositório: qualquer sessão do Claude Code aberta aqui enxerga o servidor `dispositivos` (aprove-o na primeira vez). Precisa de `uv`; a dependência (`mcp<2`) vem no cabeçalho do próprio `servidor.py`.

```bash
uv run --script tools/mcp-dispositivos/servidor.py   # roda por stdio; normalmente quem o inicia é o Claude Code
```

Para usar em outras pastas, registre também no seu usuário:

```bash
claude mcp add --scope user dispositivos -- uv run --script /projetos/eli-junior/placar-volei/tools/mcp-dispositivos/servidor.py
```

## Ferramentas

Os dispositivos se chamam `celular` e `relogio` (ou um serial `host:porta`).

| Grupo | Ferramentas |
|---|---|
| Conexão | `listar_dispositivos`, `conectar`, `parear`, `descobrir_portas`, `registrar_dispositivo`, `reiniciar_adb` |
| Estado | `estado_tela`, `info_app` |
| Build e instalação | `compilar`, `instalar`, `compilar_e_instalar`, `desinstalar` |
| Controle | `iniciar_app`, `parar_app`, `tocar`, `deslizar`, `tecla`, `texto` |
| Observação | `capturar_tela`, `logcat`, `adb_shell` |

Receitas:

- **"Gera um APK novo e instala":** `compilar_e_instalar(alvo="celular"|"relogio", tipo="debug"|"release")`. O celular embute o servidor `https://placar.elijunior.click` (outro com `servidor=`).
- **Aparelho não responde:** `conectar(dispositivo)`. A porta do `adb` sem fio muda e o MCP a acha varrendo o aparelho. Se o computador nunca foi pareado, abra "Parear novo dispositivo" no aparelho e use `parear(dispositivo, codigo)`.
- **Ver o que está na tela:** `capturar_tela(dispositivo)` e depois `tocar(dispositivo, x, y)` em pixels da captura.

## Armadilhas que o servidor já trata

- **Celular sempre com `--user 0`.** Sem isso o Samsung instala também no perfil Dual App (usuário 95) e o app aparece duplicado. `instalar` avisa se achar o app em mais de um usuário.
- **Release não atualiza debug** (assinaturas diferentes). `instalar` recusa e explica; `desinstalar_antes=true` desinstala o atual primeiro e **apaga os dados do app** (quadra local, vínculo). Só com autorização do Navigator.
- **Bloqueio de tela nunca é contornado.** `tocar`, `deslizar`, `texto` e a maioria das teclas recusam se o aparelho estiver bloqueado ou com a tela apagada, e dizem para pedir ao Navigator. `tecla WAKEUP`/`SLEEP` funcionam (acordar não desbloqueia).
- **Porta de pareamento e de conexão são diferentes** e mudam a cada vez que a depuração é religada. O `mDNS` não funciona no WSL, então o MCP as acha varrendo as portas 30000–50000 do aparelho.
- **O `adb` do relógio cai quando a tela dorme.** Toda ferramenta reconecta sozinha antes de agir.
- **Z Fold tem duas telas** (`screencap` imprime um aviso e precisa de `-d`). `capturar_tela` escolhe a tela ativa e limpa o aviso. Imagem preta quase sempre é tela apagada ou bloqueada: a nota que acompanha a imagem diz o estado.
- **Relógio:** só mostra o app com a tela acordada; `am start` com a tela apagada leva ao mostrador.
- **Nunca `pkill -f` em processo do `adb`**: o padrão casa com a própria linha de comando do shell e o derruba. Use `reiniciar_adb`.
- `adb_shell` recusa o que não tem volta (`reboot`, `wipe`, `rm -rf /`, `su`...). O pedido de permissão do agente continua sendo a barreira principal.

## Onde ficam os endereços

`~/.config/placar-dispositivos.json` (fora do repositório, porque IP e porta são da rede do Navigator; `PLACAR_DISPOSITIVOS_CONFIG` troca o caminho). Os valores iniciais estão em `nucleo.py`. `conectar` e `parear` atualizam a porta; `registrar_dispositivo` cadastra outro aparelho.

Outras variáveis: `PLACAR_ADB` (caminho do `adb`), `ANDROID_HOME`, `JAVA_HOME` (o build usa o JDK 21 do `sdkman`). O release lê a keystore de `~/.gradle/gradle.properties` (`placarKeystore*`), fora do repositório.

## Testes

`uv run pytest tests/test_mcp_dispositivos.py`: a lógica (`nucleo.py`) com um `adb` falso, sem aparelho. O servidor (`servidor.py`) é só a casca que expõe o núcleo como ferramentas.
