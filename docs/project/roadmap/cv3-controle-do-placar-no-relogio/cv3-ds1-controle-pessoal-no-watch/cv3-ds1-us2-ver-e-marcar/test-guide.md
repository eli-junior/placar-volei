# Roteiro de validação — CV3.DS1.US2

Branch: `feature/cv3-ds1-us2-ver-e-marcar` (servidor e APK `0.8.0`).

## Preparação

1. **Servidor.** No Mini PC, fora de uma partida (a troca de versão apaga as salas):

   ```sh
   git fetch origin
   git switch feature/cv3-ds1-us2-ver-e-marcar
   git pull --ff-only origin feature/cv3-ds1-us2-ver-e-marcar
   docker compose up -d --build placar
   curl -fsS https://placar.elijunior.click/health
   ```

   Passa: `/health` responde com a versão `0.8.0`.

2. **APK.** Na raiz do projeto, no WSL:

   ```sh
   export JAVA_HOME=/home/eli/.sdkman/candidates/java/21.0.7-tem ANDROID_HOME=/home/eli/Android/Sdk
   ./wear/gradlew -p wear assembleDebug
   export PATH=/home/eli/Android/Sdk/platform-tools:$PATH
   adb connect IP_DO_WATCH:PORTA_DE_CONEXAO
   adb -s IP_DO_WATCH:PORTA_DE_CONEXAO install -r wear/app/build/outputs/apk/debug/app-debug.apk
   ```

   Pareamento sem fio: ver `wear/README.md`. O vínculo antigo não vale mais, porque o banco foi recriado.

3. **Três telas:**
   - **Telefone T1:** crie a sala como `eli.relogio`, **sem** preencher jogadores.
   - **Navegador N2** (anônimo): entre como `Rafa`. O ADMIN promove Rafa a controlador.
   - **Navegador N3:** entre como espectador.
   - **Relógio:** gere o código; em T1, toque no **ícone do relógio** e aprove.

## Cenários

### 1. Ícone e "Em breve…"
- Em T1 (eli), o ícone do relógio abre o modal de vínculo.
- Em N2 (Rafa, controlador), o mesmo ícone mostra "Em breve…" por ~2,5 s e **não** abre modal.
- **Passa:** só eli abre o vínculo. **Falha:** Rafa vê o modal, ou eli vê "Em breve…".

### 2. Chave desligada: relógio só mostra; rótulos Nós/Eles e iniciais
- Depois do vínculo, o relógio mostra **Nós** (esquerda, laranja) e **Eles** (direita, azul), 0 × 0, com "Ative Controlar pelo Relógio no telefone" embaixo.
- Tocar nas metades não muda nada e não vibra.
- Em T1, **engrenagem**: A = `Eli Junior` / `Camila`, B = `Rafa` / `Marvin` → Salvar. Sem tocar no relógio, os rótulos viram **EC** e **RM**.
- **Passa:** placar visível, botões inertes, rótulos atualizados ao vivo. **Falha:** algum ponto aparece em qualquer tela, ou os rótulos ficam A/B.

### 3. Ligar a chave
- Em T1: **engrenagem → Controlar pelo Relógio → ligar**.
- Em T1, N2 e N3: os botões de +1 e Desfazer somem, e aparece "Controlado pelo relógio de eli". O painel mostra "Controle: relógio de eli". A linha do tempo registra "Placar passou a ser controlado pelo relógio de eli".
- Em T1: a engrenagem continua abrindo as configurações.
- Em N2 (Rafa): a chave não aparece nas configurações (Rafa não tem relógio e não é admin).
- **Passa:** nenhuma tela do site oferece marcar. **Falha:** algum botão de ponto continua ativo.

### 4. A, A, B no pulso
- No relógio, toque EC, EC, RM.
- Cada toque vibra na hora, o número sobe e fica mais apagado com um traço embaixo enquanto estiver pendente. No alto aparece "● Conectado · N pendentes", que volta a "● Conectado" ao confirmar.
- T1, N2 e N3 mostram **2 × 1**. A linha do tempo tem três pontos, com autor **eli**.
- **Passa:** 2 × 1 em todas as telas, três eventos e nenhum duplicado. **Falha:** 3 × 1, 2 × 2, ou evento repetido.

### 5. Toques rápidos
- Toque 5 vezes em sequência rápida, alternando lados como quiser (anote a ordem).
- **Passa:** o placar soma exatamente 5 e a linha do tempo mostra a mesma ordem tocada. **Falha:** toque perdido, somado a mais, ou fora de ordem.

### 6. Telefone bloqueado
- Bloqueie T1 e feche o navegador de N2. Toque 2 pontos no relógio.
- **Passa:** N3 mostra os 2 pontos. **Falha:** os pontos só aparecem depois de desbloquear o telefone.

### 7. Tela apagada e retomada
- Com o app aberto, abaixe o pulso até a tela apagar. Toque na tela apagada (modo ambiente/relógio).
- Levante o pulso e volte ao app.
- **Passa:** nenhum ponto foi registrado com a tela apagada, e o placar reaparece igual ao de N3. **Falha:** ponto registrado sem o app visível, ou placar diferente.

### 8. Sem conexão com fila
- Ponha o relógio em modo avião (ou afaste do telefone e desligue o Wi-Fi do relógio). Toque 2 pontos.
- O relógio mostra "Sem conexão · 2 pendentes", com números previstos.
- Feche o app (deslize para sair), abra de novo: os 2 pendentes continuam lá.
- Reative a rede **com o app aberto**.
- **Passa:** os 2 pontos entram uma única vez em N3, na ordem tocada. **Falha:** pontos perdidos ou duplicados.
- Observação: o envio só acontece com o app aberto. O envio em segundo plano é da US4.

### 9. Recusa e descarte
- Modo avião no relógio; toque 1 ponto (fica pendente).
- Em T1, **desligue** a chave. Religue a rede do relógio com o app aberto.
- O relógio mostra por cima: "A chave Controlar pelo Relógio mudou depois deste lance.", "1 lance retido fora do placar" e **Descartar**. Toque Descartar → **Confirmar descarte**.
- **Passa:** o ponto retido não aparece em N3 em momento nenhum, e o relógio volta ao placar. **Falha:** o ponto entra no placar, ou some sem a confirmação.

### 10. Site volta a pontuar e forja recusada
- Com a chave desligada, T1 volta a ter +1 e Desfazer.
- Religue a chave. Em T1, na lista de presentes, **passe o controle para Rafa**. Assim N2 tem o controle e a versão certa, e só a chave pode barrar o ponto.
- Em N2 (Rafa), no console do navegador:

  ```js
  const id = location.pathname.split('/').pop();
  const q = await (await fetch(`/api/quadras/${id}`)).json();
  const r = await fetch(`/api/quadras/${id}/pontos`, {method: 'POST', headers: {'Content-Type': 'application/json', 'x-control-version': String(q.controle_versao)}, body: '{"equipe":"A"}'});
  console.log(r.status, (await r.json()).detail);
  ```

- **Passa:** `409 O placar está sendo controlado pelo relógio.`, e o placar não muda. Um ponto no relógio continua entrando normalmente, mesmo com Rafa no controle do site. **Falha:** `201`, ou o relógio passa a ser recusado.

### 11. Fim de partida
- Com a chave ligada, marque pelo relógio até a vitória (padrão: 12 com vantagem de 2).
- Ao atingir a vitória prevista, os botões travam ("Fim de partida. Aguardando confirmação.") e depois mostram "Partida encerrada.".
- **Passa:** nenhum ponto a mais depois da vitória. **Falha:** 13 × 10 ou similar.
- Em T1, **Iniciar próxima partida**: o relógio mostra 0 × 0 e volta a aceitar toques.

### 12. Revogar desliga a chave
- Em T1: ícone do relógio → **Revogar acesso**.
- **Passa:** a chave desliga sozinha, o site volta a mostrar +1 e a linha do tempo mostra "Placar voltou a ser controlado pelo telefone (relógio revogado)". O relógio volta à tela de vínculo.

### 13. Ergonomia (Watch 8, 44 mm)
- Sob luz externa: os números e EC/RM são legíveis a um braço de distância.
- Com **Remover animações** ligado (Acessibilidade do relógio): o número muda sem deslizar e continua legível.
- **Passa:** leitura e toque confortáveis com uma mão durante o jogo. Anote o que incomodar.

## Evidência automatizada

- `uv run pytest`: 149 passaram (16 novos em `tests/test_watch_comandos.py`).
- `uv run ruff check .` e `ruff format --check .` passaram.
- Web: `npm test` 25/25 (3 novos), `npm run check` com 0 erros e 0 avisos, `npm run build` ok.
- Android: 18 testes (13 novos), `assembleDebug` e `lintDebug` ok (0 erros; os mesmos 7 avisos de antes).
