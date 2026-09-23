# Roteiro de validação — CV3.DS1.US2 (revisão 3)

Branch: `feature/cv3-ds1-us2-ver-e-marcar` (servidor e APK `0.8.0`).
Desenho: o relógio é o participante **"Eli (Relógio)"** e pontua quando o admin passa o controle para ele.

## Preparação

1. **Servidor.** No Mini PC, fora de uma partida (recriar o contêiner apaga as salas):

   ```sh
   git fetch origin
   git switch feature/cv3-ds1-us2-ver-e-marcar
   git pull --ff-only origin feature/cv3-ds1-us2-ver-e-marcar
   grep WATCH_AUTO_GRANT .env   # se existir com eli.relogio, troque para eli ou apague a linha
   docker compose up -d --build placar
   curl -fsS https://placar.elijunior.click/health
   ```

   Passa: `/health` responde com a versão `0.8.0`.

2. **APK.** O APK mudou; reinstale. Na raiz do projeto, no WSL:

   ```sh
   export PATH=/home/eli/Android/Sdk/platform-tools:$PATH
   adb connect IP_DO_WATCH:PORTA_DE_CONEXAO
   adb -s IP_DO_WATCH:PORTA_DE_CONEXAO install -r wear/app/build/outputs/apk/debug/app-debug.apk
   ```

3. **Telas:**
   - **Telefone T1:** crie a sala como `eli` (ou `ELI`), **sem** preencher jogadores.
   - **Navegador N2** (anônimo): entre como `Rafa`. Em T1, promova Rafa a controlador.
   - **Navegador N3:** entre como espectador.

## Cenários

### 1. Nome e ícone
- T1 aparece como **Eli** na lista de presentes.
- Em T1, o ícone do relógio abre o modal com o campo do código.
- Em N2 (Rafa), o mesmo ícone mostra "Em breve…" e **não** abre o modal.
- Em T1, a engrenagem aparece e abre as configurações.
- **Passa:** tudo acima. **Falha:** "não habilitado" para Eli, modal para Rafa, ou engrenagem em branco.

### 2. Vínculo cria "Eli (Relógio)"
- No relógio, gere o código e aprove em T1.
- T1, N2 e N3 mostram **Eli (Relógio)** na lista de presentes, como espectador e online.
- O relógio mostra **Nós** × **Eles**, 0 × 0, com "Controle no telefone. Peça ao admin para passar o controle." Tocar não muda nada e não vibra.
- Em T1, na engrenagem, preencha A = `Eli Junior` / `Camila` e B = `Rafa` / `Marvin`. Sem tocar no relógio, os rótulos viram **EC** e **RM**.
- **Passa:** tudo acima. **Falha:** relógio some da lista, aparece duplicado, ou pontua sem controle.

### 3. Delegar o controle
- Com o app aberto no relógio, em T1 (lista de presentes): **Tornar controlador** em Eli (Relógio) e depois **Passar controle**. A linha do tempo deve mostrar a transferência, não só a promoção.
- Em T1, N2 e N3: "Controle: **Eli (Relógio)**", sem +1/Desfazer no site. No relógio, os botões liberam.
- **Passa:** só o relógio pode marcar. **Falha:** o site ainda oferece +1, ou o relógio continua travado.

### 4. A, A, B no pulso
- Toque EC, EC, RM.
- Cada toque vibra na hora; o número sobe mais apagado, com um traço embaixo, enquanto estiver pendente. No alto: "● Conectado · N pendentes", depois "● Conectado".
- T1, N2 e N3 mostram **2 × 1**. A linha do tempo tem três pontos com autor **Eli (Relógio)**.
- **Passa:** 2 × 1 em todas as telas, com três eventos. **Falha:** 3 × 1, 2 × 2 ou evento repetido.

### 5. Toques rápidos
- Toque 5 vezes em sequência rápida (anote a ordem).
- **Passa:** soma exatamente 5, na ordem tocada. **Falha:** toque perdido, a mais ou fora de ordem.

### 6. Tela apagada não perde o controle
- Abaixe o pulso e espere **30 s** com a tela apagada. Toque a tela apagada.
- Levante o pulso e volte ao app.
- **Passa:** nenhum ponto registrado com a tela apagada; o controle continua com Eli (Relógio) (T1 mostra) e os botões voltam ativos. **Falha:** o controle volta para Eli sozinho.

### 7. Telefone bloqueado mantém o admin
- Bloqueie T1 por **3 minutos** e marque pontos, com o app do relógio aberto (toque de vez em quando para a tela não apagar).
- **Passa:** N3 recebe os pontos; ao desbloquear, T1 continua ADMIN (sem sucessão para Rafa). **Falha:** o admin passa para outra pessoa.

### 8. Sem conexão com fila
- Modo avião no relógio. Toque 2 pontos: "Sem conexão · 2 pendentes".
- Feche o app e abra de novo: os 2 pendentes continuam lá.
- Reative a rede **com o app aberto**.
- **Passa:** os 2 pontos entram uma única vez, na ordem. **Falha:** pontos perdidos ou duplicados.
- Observação: o envio só acontece com o app aberto. O envio em segundo plano é da US4.

### 9. Admin retoma e lance é recusado
- Modo avião no relógio; toque 1 ponto (pendente).
- Em T1: **Assumir o controle**. Religue a rede do relógio com o app aberto.
- O relógio mostra "O controle mudou…", "1 lance retido fora do placar" e **Descartar**. Toque Descartar → **Confirmar descarte**.
- **Passa:** o ponto nunca aparece em N3; o relógio volta ao placar com os botões travados. **Falha:** o ponto entra no placar.

### 10. Site sem controle não pontua (forja)
- Passe o controle de volta para Eli (Relógio). Em N2 (Rafa), no console do navegador:

  ```js
  const id = location.pathname.split('/').pop();
  const q = await (await fetch(`/api/quadras/${id}`)).json();
  const r = await fetch(`/api/quadras/${id}/pontos`, {method: 'POST', headers: {'Content-Type': 'application/json', 'x-control-version': String(q.controle_versao)}, body: '{"equipe":"A"}'});
  console.log(r.status, (await r.json()).detail);
  ```

- **Passa:** `403 Outro operador está no controle do placar.`, e o placar não muda. **Falha:** `201`.

### 11. Fim de partida
- Marque pelo relógio até a vitória (padrão: 12 com vantagem de 2).
- Na vitória prevista, os botões travam ("Fim de partida. Aguardando confirmação."), depois "Partida encerrada.".
- **Passa:** nenhum ponto depois da vitória. Em T1, **Iniciar próxima partida**: o relógio volta a 0 × 0 e a aceitar toques (o controle continua com ele). **Falha:** ponto a mais.

### 12. Revogar remove o relógio
- Em T1: ícone do relógio → **Revogar acesso**.
- **Passa:** Eli (Relógio) sai da lista; o controle volta para Eli; a linha do tempo mostra "Controle devolvido para Eli: relógio desvinculado"; o site volta a ter +1; o relógio volta à tela de vínculo.

### 13. Ergonomia (Watch 8, 44 mm)
- Sob luz externa: números e EC/RM legíveis a um braço de distância.
- Com **Remover animações** ligado: o número muda sem deslizar e continua legível.
- **Passa:** leitura e toque confortáveis com uma mão. Anote o que incomodar.

## Evidência automatizada
- `uv run pytest`: 151 passaram. São 16 testes em `tests/test_watch_comandos.py`; os testes da US1 foram reescritos para o participante próprio e para `eli` em qualquer caixa.
- `ruff check` e `ruff format --check`: ok.
- Web: `npm test` 25/25, `npm run check` sem erros nem avisos, `npm run build` ok.
- Android: 18 testes, `assembleDebug` e `lintDebug` ok (0 erros; os mesmos 7 avisos de antes).
