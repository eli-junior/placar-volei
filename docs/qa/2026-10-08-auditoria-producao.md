# Auditoria em produção — 2026-10-08

Alvo: https://placar.elijunior.click (Mini PC, container `placar-volei`, imagem `placar-volei:local`, versão 0.46.1).
Método: navegação real no Chrome + leitura de logs/compose/código no servidor (somente leitura).
Evidências (screenshots): `docs/qa/evidencias/`.

## Resumo

| # | Gravidade | Problema |
|---|-----------|----------|
| P1 | Crítica | Joguinho preso: partida "chamada" aponta para quadra que não existe mais; nenhum botão da tela resolve |
| P2 | Alta | `RESET_DB_ON_STARTUP=true` apaga as quadras a cada start, mas o Joguinho é durável: estados ficam inconsistentes |
| P3 | Média | URL é `/sessao`; o nome do produto é "Joguinho" (`/joguinho` cai na home) |
| P4 | Média | Rota inexistente responde 200 e mostra a home (sem 404) |
| P5 | Média | Bloqueio por tentativas (429/404) apaga o segredo salvo no aparelho |
| P6 | Baixa | Texto "vincule de novo" sem controle para vincular |
| P7 | Info | Clone local atrasado em relação à produção |

---

## P1 — Joguinho preso (Crítica)

**Estado encontrado em `/sessao` (screenshots 01 e 02):** Rodada 1 · alvo 6; partida "Time 1 × Time 2" com selo **chamada**; "Quadra 29397: indisponível — vincule de novo"; botão **Encerrar partida** desabilitado; fila com 1 time; 6 presentes; "Presença travada: há uma rodada em andamento".

**Evidências de API/log:**
- `GET /api/quadras` → `{"quadras":[]}` (nenhuma quadra existe)
- `GET /api/quadras/29397` → 404 "Quadra não encontrada."
- `GET /api/quadras/29397/partida` → 404
- Container criado 2026-10-08 05:07 UTC e iniciado 10:42 UTC (Mini PC reiniciou ~11 min antes do teste).

**Por que não tem saída pela tela (deadlock):**
1. `app/ponte.py::_registrar_encerramento` — se `ler_placar()` devolve `None` (quadra sumiu), lança 409 `indisponivel`. Encerrar é impossível.
2. `app/ponte.py::vincular_sync` e `desvincular_sync` chamam `_exigir_sem_partida_chamada` — enquanto há partida `chamada`, **não é possível vincular nem desvincular** quadra.
3. `web/src/components/PainelConducao.svelte` — o formulário "vincular", "Desvincular" e "Criar quadra e vincular" ficam dentro de `{#if !temPartida}`. Com partida chamada, o painel mostra só "indisponível — vincule de novo", sem nenhum controle.
4. Única saída restante: **Cancelar rodada** (perde a rodada). Não executei, para não destruir o estado que você quer preservar/corrigir.

**Correção sugerida (decidir):**
- Permitir (re)vincular quadra mesmo com partida chamada **quando a quadra atual está indisponível** (no servidor e na UI).
- E/ou ação explícita "Anular partida chamada" (volta os times à fila sem cancelar a rodada) e "Registrar resultado manualmente".
- Teste de regressão: chamar partida → apagar a quadra → verificar que dá para recuperar sem cancelar a rodada.

## P2 — Banco das quadras efêmero × Joguinho durável (Alta)

`docker-compose.yml` (produção):
- `RESET_DB_ON_STARTUP=true` com o comentário "Banco efêmero por decisão do Navigator (2026-09-27): cada start do contêiner começa limpo".
- `DB_PATH=/data/placar.db` **sem volume** (camada gravável do container).
- `GERENCIADOR_DB_PATH=/data-gerenciador/gerenciador.db` em volume `placar-volei_gerenciador-dados` (durável) + backups em `./backups`.

Efeito: todo restart/reboot/deploy apaga as quadras, mas a sessão/rodada/partida chamada do Joguinho sobrevive apontando para uma quadra morta — é exatamente o P1. Isso vai se repetir a cada deploy (o container foi recriado hoje às 02:07 e o host reiniciou às 07:42).

**Correção sugerida:** ao subir, reconciliar o Joguinho com as quadras existentes (desvincular `quadra_id` inválido; anular partida `chamada` órfã), ou tornar o placar durável quando houver rodada em andamento. A decisão de 2026-09-27 precisa ser revista à luz do CV8.

Obs.: também há `QUADRA_TTL_SECONDS=3600` — uma quadra pode expirar por TTL no meio de uma rodada pelo mesmo caminho. Vale cobrir no mesmo teste.

## P3 — Rota `/sessao` em vez de `/joguinho` (Média)

- `web/src/App.svelte:261` — `telaSessao = window.location.pathname === '/sessao'`
- `web/src/App.svelte:332` — `pushState({}, '', '/sessao')` no botão "Joguinho" do topo.
- `/joguinho` hoje devolve 200 com a home (screenshot 03).
- A API segue `/api/sessao/*` (`app/ponte.py`, `app/sessao.py`); renomear a URL de tela não exige renomear a API.

**Correção sugerida:** tela em `/joguinho`; manter `/sessao` redirecionando (301 no servidor ou `replaceState` no cliente) para não quebrar favoritos como o seu link atual.

## P4 — Rota inexistente não dá 404 (Média)

`/rota-inexistente` → 200 e renderiza a home (screenshot 04). Mesmo comportamento esconde erros de digitação de URL (foi o que mascarou o `/joguinho`). Sugestão: tela "Página não encontrada" no `carregarRota`, mantendo o fallback do servidor para o SPA.

## P5 — Bloqueio por tentativas apaga o segredo salvo (Média)

Sequência observada:
1. `/jogadores` mostrou "Muitas tentativas incorretas. Aguarde um pouco." (log: `GET /api/jogadores?incluir_inativos=true` → **429**).
2. Em seguida `/sessao` passou a mostrar "Segredo recusado. Confira e tente de novo." (screenshot 05) e o `localStorage` perdeu a chave do segredo do dono.

`web/src/lib/jogadores.js:32-33` trata 404 como "segredo recusado" e 429 como "muitas tentativas"; a tela descarta o segredo salvo ao receber a recusa. Resultado: um bloqueio temporário por IP vira perda do segredo no aparelho, e o dono precisa redigitar.

**Correção sugerida:** só apagar o segredo salvo em recusa confirmada, nunca em 429; e não contar como tentativa incorreta uma requisição sem cabeçalho de segredo vinda de sondagem. (Ver nota de transparência abaixo.)

## P6 — "vincule de novo" sem ação (Baixa)

Consequência de P1/PainelConducao: a mensagem instrui uma ação que a tela não oferece quando há partida chamada.

## P7 — Clone local desatualizado (Info)

`D:\projetos\placar_volei` está na 0.30.x (master, atrás de `origin/master`) e não contém o código do Joguinho; o servidor roda a 0.46.1 (`5762045`). Faça `git pull` antes de corrigir. Há worktrees do Codex marcados como `prunable`.

---

## Nota de transparência (efeito colateral do teste)

Para investigar, fiz GETs sem o cabeçalho de segredo em `/api/sessao`, `/api/jogadores`, `/owner/quadras` e similares a partir do navegador. A API trata isso como segredo incorreto, o que muito provavelmente acionou o bloqueio por IP (P5) e fez o navegador perder o segredo salvo. **Ação necessária:** redigitar o segredo do dono no `/sessao` (está no `.env` do servidor) e aguardar o fim do bloqueio. Nenhum dado foi alterado, nada foi criado ou cancelado em produção. O estado do P1 foi capturado **antes** disso (screenshots 01 e 02).

## Não testado

- Criar/entrar em quadra, pontuar, desfazer, relógio e celular (criam dados em produção; posso rodar com sua autorização).
- Comportamento do Joguinho depois do P1 (precisa do segredo; ações como "Cancelar rodada" são destrutivas).
- Layout em celular real e `prefers-reduced-motion`.

---

## Encaminhamento (2026-10-08)

Os achados viraram a [CV8.DS7](../project/roadmap/cv8-gerenciador-de-times/cv8-ds7-joguinho-sem-becos/index.md). O deadlock da partida chamada foi corrigido na 0.46.2 (US16, "Anular partida").
