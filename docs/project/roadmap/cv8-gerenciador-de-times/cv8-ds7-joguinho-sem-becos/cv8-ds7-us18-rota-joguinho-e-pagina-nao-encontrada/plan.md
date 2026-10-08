# Plano — CV8.DS7.US18 Rota `/joguinho` e página não encontrada

Branch: `fix/cv8-ds7-us18-rota-joguinho` · Versão alvo: **0.46.5** (patch; só web e APK, o backend não muda)

## Estado atual (confirmado no código)

- `App.svelte::carregarRota` reconhece `/jogadores`, `/sessao` e `/quadra/<id>`; **qualquer outro caminho cai na home** sem aviso (`/joguinho`, `/rota-inexistente`, `/quadra/1/2`).
- O botão "Joguinho" faz `pushState('/sessao')` e a tela é `telaSessao = pathname === '/sessao'`.
- O servidor devolve o SPA (200) para qualquer caminho fora de `/api/*`; a API do joguinho é `/api/sessao/*` e fica como está.
- No APK (páginas do servidor dentro do Capacitor) `/jogadores` e o Joguinho são ocultos; hoje isso é "cair na home".

## Desenho

1. **Tabela de rotas pura** em `web/src/lib/rotas.js` (`resolverRota(caminho, { apk })`), testável sem navegador:

   | Caminho | Tela |
   |---|---|
   | `/`, `/index.html` | início |
   | `/quadra/<id>` (`[a-zA-Z0-9_-]+`) | sala (fluxo de hoje, inclusive "sala expirada") |
   | `/joguinho` | Joguinho |
   | `/sessao` (legado) | Joguinho, com `replaceState` para `/joguinho` |
   | `/jogadores` | Jogadores |
   | qualquer outro | **Página não encontrada** |

   A barra final é ignorada (`/jogadores/` = `/jogadores`). No APK, `/joguinho`, `/sessao` e `/jogadores` valem como não encontrada (a tela não existe lá).
2. **`PaginaNaoEncontrada.svelte`:** título "Página não encontrada", o endereço digitado e o link "Voltar ao início" (`href="/"`, funciona também sem JS de navegação interna). Fica de fora do `ModalEntrar`/sala; `carregarRota` não toca em estado de sala nesse caso.
3. **`App.svelte`:** `carregarRota` passa a decidir pela tabela; o botão do topo faz `pushState('/joguinho')`; `/sessao` vira `replaceState('/joguinho')` preservando `?query` e `#hash`, sem quebrar favoritos nem o "voltar".
4. **Servidor:** inalterado (continua devolvendo o SPA). Status HTTP 404 para o SPA fica fora, como a história pede.

### Alternativas descartadas

- **Redirecionar `/sessao` com 301 no servidor:** exige mexer no `serve_spa` e não ajuda o APK; o `replaceState` no cliente basta e a história pede isso.
- **Renomear a API para `/api/joguinho`:** muda contrato, testes e o MCP sem ganho para o usuário (a URL de tela é o que aparece).
- **Manter `/joguinho` e `/sessao` ambos como "oficiais":** perpetua dois endereços para a mesma tela.

## Escopo

- `web/src/lib/rotas.js` (+ teste unitário), `web/src/components/PaginaNaoEncontrada.svelte`, `web/src/App.svelte`.
- e2e: botão leva a `/joguinho`; `/sessao` → `/joguinho`; `/rota-inexistente` e `/quadra/1/2` mostram a página; `/quadra/<id>` e `/jogadores` seguem iguais; APK não abre `/joguinho`; axe na página nova; ajuste do e2e que hoje abre `/sessao` no APK.
- Docs: CHANGELOG 0.46.5, roadmap, worklog, guia (mapa de rotas de tela).

## Fora do escopo

Status HTTP 404 do servidor para rotas de tela; renomear a API; US19, US20, US21; mensagens do Joguinho.

## Aceite (BDD)

- **Dado** o botão "Joguinho" do topo **quando** tocado **então** a URL é `/joguinho` e a tela abre.
- **Dado** um favorito `/sessao` **quando** aberto **então** a URL vira `/joguinho` (sem entrada extra no histórico) e a tela abre.
- **Dado** `/rota-inexistente` **então** aparece "Página não encontrada" com link para o início; o servidor segue devolvendo o SPA.
- **E** `/api/sessao/*` continua igual.

## Riscos

- Quem tinha `/joguinho` salvo (que antes abria a home) passa a abrir a tela: é o esperado.
- Qualquer caminho que o app use e que não esteja na tabela viraria "não encontrada". Conferi os `pushState`/`replaceState` do `App.svelte` (`/`, `/jogadores`, `/sessao`, `/quadra/<id>`); o e2e completo cobre o resto.
