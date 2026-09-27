# Roteiro de validação conjunta — CV5 (0.20.0)

Tudo sai da branch `integracao/cv5`. Cada bloco diz o que observar e quando o teste passa ou falha. Os detalhes de cada história estão no `index.md` dela, na seção "Revisão".

## 0. Preparar (uma vez)

1. No `.env` do Mini PC, defina um `OWNER_SECRET` próprio. Sem ele, o compose recusa subir; com o valor de exemplo, o app recusa.
2. Suba a integração:
   ```bash
   git fetch && git switch integracao/cv5 && docker compose up -d --build
   ```
3. **O primeiro deploy começa com o banco vazio** (volume novo e schema novo). Pareie o relógio de novo uma vez.
4. Relógio: `./wear/gradlew -p wear assembleDebug`, e instale. Para o APK de release, crie antes a keystore (veja `wear/README.md`).

## 1. Segurança e deploy (DS1)

| Teste | Passa | Falha |
|---|---|---|
| `curl` no owner 6 vezes, trocando `X-Forwarded-For` | 5×404 e depois 429 | seis 404 |
| 21 códigos de sala errados pelo `curl` | 20×404 e depois 429 | nunca 429 |
| Criar uma sala, depois `docker compose up -d --build` (mesma versão) | a sala continua | a sala sumiu |
| `curl -sI` no `/api/quadras` depois de entrar numa sala | `Set-Cookie` com `Secure` | sem `Secure` |
| `curl https://…/health` | sem o campo `db` | aparece o caminho do banco |

## 2. Relógio (DS2 e DS4.US1)

| Teste | Passa | Falha |
|---|---|---|
| 10 toques rápidos | 10 pontos no telefone, com vibração em cada um | falta ponto, ou a tela trava |
| `adb shell run-as br.com.placarvolei.watch sh -c 'echo "{x" > files/fila-lances.json'` e reabrir | aviso "Lances antigos ilegíveis" e o relógio segue marcando | crash ou nenhum aviso |
| Sair do app pelo botão lateral | o batimento some e o treino do Samsung Health continua | o sensor segue ligado |
| 5 min com o placar aberto e conectado | nenhum `/api/watch/session` no log do servidor | polling a cada 15 s |
| 10 min sem tocar | a tela pode apagar; um toque volta ao placar | fica acesa para sempre |
| Fim da partida: um toque em "▶ Nova" | vira "Tocar de novo" e não reinicia | a partida reinicia |
| Dois toques em até 3 s | a partida nova começa | nada acontece |
| Desfazer | a faixa mostra "↶ Desfazer +1 {equipe}" | só "Desfazer" |
| Wear OS 6, primeira abertura | pedido da permissão de frequência cardíaca | pedido de "sensores do corpo" |
| APK de release: parear, marcar, desfazer e batimento | tudo funciona | algo quebra (culpa do R8) |

## 3. Tempo real (DS3)

| Teste | Passa | Falha |
|---|---|---|
| 3 celulares, um com "Slow 3G" no DevTools | os outros recebem o ponto na hora | todos atrasam |
| Celular bloqueado por 5 min e depois desbloqueado | o placar atualiza em até 3 s ou mostra "Reconectando…" | placar congelado com "Ao vivo" |
| DevTools offline por 1 min, depois online | "Reconectando…" e volta sozinho | fica preso |
| `docker compose stop` e marcar um ponto | mensagem legível | "Unexpected token <" |
| Copiar o código em `http://IP-da-LAN` | não diz "Copiado!" | diz "Copiado!" |

## 4. Acessibilidade e linguagem (DS4 e DS5)

| Teste | Passa | Falha |
|---|---|---|
| TalkBack ou NVDA com a rede caindo | anuncia "Reconectando…" | silêncio |
| Movimento reduzido ligado no sistema | nada pulsa nem gira | pulsos continuam |
| Linha do Tempo: Tab e Esc | o foco fica dentro e volta ao botão ao fechar | o foco escapa |
| Modo Sol: marcar um ponto | "Enviando o toque…" legível | texto ciano apagado |
| Apelido digitado na Home, depois um link de sala em aba nova | apelido já preenchido | campo vazio |
| Abrir "Compartilhar" | o QR aparece e a câmera lê | sem QR |
| Recarregar a página com o Modo Sol salvo | já abre claro | pisca escuro |
| Fim de partida | "{nome} venceu!" | "Vitória da/de" |

## Resultado

Se tudo passar, o Navigator aprova o Checkpoint 4. O Driver então faz o merge da `integracao/cv5` na `master`, fecha a 0.20.0 no CHANGELOG e marca as 13 histórias como `Done`. Qualquer falha volta para a história indicada na tabela.
