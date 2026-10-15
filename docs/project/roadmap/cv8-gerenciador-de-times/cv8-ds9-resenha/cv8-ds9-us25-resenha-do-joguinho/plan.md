---
code: CV8.DS9.US25
status: Validated
updated: 2026-10-15
---

# Plano — Resenha do Joguinho

## Checkpoint 1 (Navigator, 2026-10-15)

- Zoeira liberada ("quanto mais zoeira melhor"), sessão aberta ou a última encerrada, e uma galeria com a foto e um título positivo ou negativo de cada jogador.

## Entrega

- **Backend:** `app/estatisticas.py`: `calcular` é pura (prêmios, galeria, tabela, resumo) e `carregar` lê o `gerenciador.db`. Rota `GET /api/sessao/estatisticas`, só para o dono, como o resto de `/api/sessao`.
- **Web:** rota `/joguinho/resenha` (`rotas.js`, fora do APK), botão **Resenha** no topo do Joguinho, `Resenha.svelte` e `lib/resenha.js` (textos e divisão em cartões). `Avatar` aceita tamanho em qualquer medida CSS.
- **Imagens:** `html-to-image` 1.11.11 gera um PNG 1080 × 1350 por cartão; Web Share com arquivos quando existe, download quando não.

## Desvios do plano

- **Nomes curtos:** o cadastro exige nome e sobrenome; o print usa o primeiro nome, com a inicial do sobrenome (ou o nome todo) só para quem divide o primeiro nome com outro jogador do dia.
- **Cartões em vez de página longa (pedido no Checkpoint 2):** a página virou cartões 4:5 de tamanho fixo, medidos em `cqw`, e ganhou o botão de imagens. Entrou a dependência `html-to-image` (decisão registrada).
- **Prêmios de partida** (Jogo de infarto, Maratona) não viram título na galeria.
- Ficou de fora o card único "Carrasco + Pneu" (os dois saem da mesma partida); fica como está até o Navigator pedir.

## Testes

- `tests/test_estatisticas.py` (17): regras dos prêmios, galeria, tabela, nomes curtos, rota, sessão encerrada.
- `web/tests/resenha.test.js` (7) e `rotas.test.js`.
- `web/e2e/resenha.spec.js` (2): cartões, proporção 4:5 na largura da tela, axe, e o botão que baixa 4 PNGs de 1080 × 1350.
