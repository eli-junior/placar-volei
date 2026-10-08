# Plano — CV8.DS7.US17 Segredo do dono não some por engano

Branch: `fix/cv8-ds7-us17-segredo-nao-some` · Versão alvo: **0.46.4** (patch; backend, web e APK)

## Onde o segredo se perde hoje (confirmado no código)

1. **Todo 404 vira "segredo recusado".** `chamarApi` (`web/src/lib/jogadores.js`) troca qualquer 404 por `ErroJogadores('Segredo recusado…', 404)` sem ler o corpo, e `Sessao.svelte` / `Jogadores.svelte` chamam `sair()` (apaga do `localStorage`) em todo `status === 404`. O servidor também usa 404 para erro de domínio (`erro_de_campo(404, "jogador", "não encontrado")`, foto não encontrada).
2. **O WebSocket do gerenciador fecha com 4401 também no bloqueio (429).** `websocket_gerenciador` captura a `HTTPException` do `validar_segredo_owner` — 404 (segredo errado) ou 429 (bloqueio) — e fecha sempre com 4401; `Sessao.svelte` trata 4401 com `sair()`. É o caminho provável do P5: o 429 de `/jogadores` seguido da sessão "recusando" o segredo.
3. **Requisição sem cabeçalho conta como tentativa errada** (`registrar_falha` quando `secret` é vazio). Uma sondagem sem segredo gasta as 5 tentativas do IP e dispara o 429 do item 2.

## Desenho

- **Servidor, sem segredo não é tentativa:** em `validar_segredo_owner`, `secret` ausente ou vazio continua dando o mesmo 404 mascarado, mas **não** chama `registrar_falha`. Segredo presente e errado conta como hoje. O bloqueio (429) continua valendo para quem já está bloqueado.
- **Servidor, bloqueio no WebSocket tem código próprio:** 429 fecha com **4429**; 4401 fica só para segredo recusado/handshake inválido.
- **Cliente, recusa se distingue pelo corpo:** 404 **sem** `erros` (o mascarado) é recusa; 404 **com** `erros[]` é erro de domínio. Sem sinal novo, então nada é revelado a quem não tem segredo (o corpo mascarado é o mesmo de sempre). `ErroJogadores` ganha `recusado` (booleano) e as telas usam `e.recusado` no lugar de `e.status === 404`.
- **Cliente, 429 diz quanto falta:** a mensagem usa o `Retry-After` ("Tente de novo em 4 min"); o segredo continua salvo. No WebSocket, 4429 mostra a mesma ideia e não reconecta em laço.
- **Só `recusado` e 4401 apagam o segredo.** O botão "Esquecer segredo neste aparelho" segue como saída manual.

### Alternativas descartadas

- **Sinal próprio de recusa** (cabeçalho ou código no corpo): revelaria o endpoint a quem não tem segredo, que é o que o 404 mascarado evita.
- **Comparar o texto "Não encontrado."**: acopla ao texto; "404 sem `erros`" é a regra da história e falha para o lado seguro (mantém o segredo).
- **Trocar o 404 de domínio por 422/409 no servidor:** muda contrato e testes por uma regra que o cliente resolve sozinho.

## Escopo

- `app/api.py`: sem segredo não conta falha. `app/main.py`: 4429 no WebSocket.
- `web/src/lib/jogadores.js`: `recusado`, 404 de domínio, mensagem do 429 com `Retry-After`.
- `web/src/components/Sessao.svelte`, `Jogadores.svelte`: `e.recusado` e tratamento do 4429.
- Testes: pytest (sem cabeçalho não conta; 429 no WS → 4429; segredo errado ainda conta e ainda 4401), unitários da web (`jogadores.test.js`) e e2e (404 de domínio não apaga o segredo; segredo errado apaga).
- Docs: CHANGELOG 0.46.4, roadmap, worklog, guia se couber; registro de decisão curto (regra da recusa).

## Fora do escopo

US18, US19, US20, US21; trocar o modelo de autenticação do Joguinho (F5.2: quem opera sem segredo); o bloqueio por IP em si (limites e janelas).

## Aceite (BDD)

- **Dado** o segredo certo salvo **quando** uma ação recebe 404 de domínio (com `erros[].campo`) **então** o segredo continua salvo e o erro aparece no lugar.
- **Dado** um bloqueio por tentativas (429), em HTTP ou no WebSocket, **então** o segredo continua salvo e a tela diz quanto falta.
- **Dado** uma requisição **sem** o cabeçalho de segredo **então** ela não conta como tentativa errada no bloqueio por IP.
- **Dado** o segredo errado **então** o aparelho o esquece, como hoje.

## Riscos

- Quem sonda sem cabeçalho deixa de gastar tentativas; a força bruta só vale com cabeçalho, e esse caminho segue limitado a 5 falhas por 10 min.
- Um 404 de rota inexistente do framework (sem `erros`) seria lido como recusa; não ocorre nas telas, e o botão manual cobre o resto.
