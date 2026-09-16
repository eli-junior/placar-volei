---
date: 2026-09-16T01:30:00Z
author: Claude Code (Driver, orquestrador)
kind: milestone
related:
  - CV2.DS1
  - CV2.DS3.TS1
  - CV2.DS2
  - CV2.DS4
  - debt-codigo-mestre-no-websocket
  - debt-lotacao-fantasma
  - debt-integridade-de-toques-e-erros-422
  - debt-tokens-e-cores-acopladas
verification:
  - uv run pytest (98 testes aprovados)
  - uv run ruff check . (0 erros)
  - uv run ruff format --check . (149 arquivos formatados)
  - npm run check (0 erros)
  - npm test (6 aprovados)
  - npm run build (sucesso)
---

# CV2 — Ondas 1 e 2: o que entrou, o que ficou e como retomar

## What changed

O Navigator selecionou o backlog completo do CV2 (DS1 a DS4) mais a reativação de
`CV1.DS2.US3`, com execução coordenada por sub agentes em worktrees isolados e
integração sequencial na branch de trabalho.

Antes de qualquer código, sete itens de débito técnico foram abertos em
`docs/project/debt/items/` para nomear a dívida que o CV2 se propõe a quitar.

A Onda 1 fechou e está integrada:

- `CV2.DS3.TS1` — tokens visuais (merge `3ab117a`). 41 tamanhos de fonte para 8
  degraus, 17 raios para 4, 32 sombras para 3. Ciano e laranja restritos aos
  Times A e B, com 18 aliases legados preservados para nada quebrar no caminho.
  Anel de foco global `:focus-visible` e o tema claro "Modo Sol" definido em
  tokens, pré-requisito da `CV2.DS2.US4`.
- `CV2.DS1` — blindagem e confiabilidade (merges `71c4ec5` e `7e7ccda`). Fecha o
  vazamento de `codigo_mestre` no WebSocket por allowlist de campos públicos,
  conta capacidade por presença efetiva em vez de linhas na tabela, dá feedback e
  fila ao `+1` e normaliza os erros 422.

A Onda 2 (`CV2.DS2` e `CV2.DS4`) foi interrompida duas vezes: primeiro por limite
de sessão da API, depois a pedido do Navigator. **Nada da Onda 2 foi integrado.**

## Why it matters

O ciclo do CV2 parou no meio, com duas Delivery Stories integradas e duas em
trabalho parcial fora da branch. Sem este registro, a retomada dependeria da
memória de uma sessão que não existe mais: qual base cada branch de apoio usa,
qual delas precisa de rebase, quais testes nunca chegaram a ser escritos e quais
decisões de produto continuam esperando o Navigator.

O vazamento fechado pela `CV2.DS1` é a razão de o ciclo ter valido a pena mesmo
inacabado: `snapshot()` montava a chave `quadra` com `dict()` sobre `SELECT *`, e
a coluna `codigo_mestre` adicionada pela `CV1.DS2.TS1` passou a trafegar para
todo espectador conectado, embora as rotas REST tivessem sido blindadas e
testadas naquela story.

## Verification

Estado verificado da branch `claude/subagentes-backlog-features-sqbsfs`:
`uv run pytest` **98 passed** (baseline era 90), `ruff check` e
`ruff format --check` limpos, `npm run check` 0 erros, `npm test` 6 pass,
`npm run build` OK.

O fechamento do vazamento foi conferido de forma independente, fora dos testes
do agente que o implementou: criando uma sala real, lendo a linha da tabela e
comparando com o payload projetado. A tabela traz `codigo_mestre`; o payload
expõe apenas `id`, `nome`, `criado_em`, `atualizado_em`, `controle_id`,
`controle_versao` e `partida_id`. Nem a chave nem o valor aparecem.

Um teste da `CV2.DS1` falhou na integração e não era regressão: passava isolado e
falhava na suíte completa porque presumia que sair do bloco `websocket_connect`
já tivesse concluído o `finally` do servidor que remove a conexão do hub. Foi
corrigido para esperar pelo comportamento observável com prazo, e a suíte rodou
três vezes seguidas verde.

Atenção operacional: `app/static` é gerado pelo build e está no `.gitignore`.
**Rodar `cd web && npm run build` antes do pytest**, senão 5 testes de SPA falham
por ausência dos estáticos. `web/node_modules` também não é versionado.

## Follow-up

### Preservado sem integrar

Duas branches remotas carregam trabalho parcial. Nenhuma foi verificada pela
suíte e nenhuma deve ser integrada como está.

- `wip/cv2-ds2-parcial` — backend de governança de controle (US5) e apelidos
  únicos (US6), cerca de 330 linhas em `app/`. **Base correta.** O agente parou
  logo antes de escrever os testes, então `tests/test_governanca_de_controle.py`
  e `tests/test_apelidos_unicos.py` podem estar vazios ou parciais. Nada de
  frontend foi feito.
- `wip/cv2-ds4-parcial` — `Dialogo.svelte` sobre a tag nativa, `Icone.svelte`,
  módulo de ícones, encoder de QR Code sem dependência (o agente relatou 155/155
  casos batendo com implementação de referência, mas o teste permanente com
  fixtures não chegou a ser gravado) e as fontes Teko e Inter em woff2 legítimo.
  **A base desta branch é anterior à `CV2.DS1` e aos tokens**: precisa de rebase,
  e o CSS herdado foi escrito quando os tokens ainda não existiam.

### Pendente

- `CV2.DS2` completa: US1 paisagem, US2 zona do polegar, US3 wake lock,
  US4 Modo Sol, US5 governança de controle, US6 apelidos únicos, TS1 backoff.
- `CV2.DS4`: retomar o parcial e ainda US1 (tela de vitória) e US4 (microcopy).
- `CV2.DS3` restante: US1 overflow, US2 Home, US3 entrada em 1 toque,
  US4 container queries, US5 WCAG 2.2, mais os 23 ajustes de componente listados
  na seção 9 de `cv2-ds3-ts1-tokens-e-cores-semanticas/plan.md`.
- `CV1.DS2.US3` — owner takeover por código mestre.

### Decisões que continuam com o Navigator

1. **Cor da ação primária.** Desacoplar ciano e laranja dos times empurra a ação
   primária do sistema (hoje ciano, o botão mais clicado do produto) para o
   amarelo de marca. É o item 17 dos ajustes adiados e condiciona os outros 22.
   Não foi executado à espera da decisão.
2. **Debounce do `+1`.** A `CV2.DS1` removeu o debounce de 250 ms, que era
   proteção contra duplo toque acidental e também um ponto de descarte
   silencioso. Hoje dois toques acidentais viram dois pontos, reversíveis pelo
   Desfazer. Mantido assim até decisão contrária.
3. **Rotação do `codigo_mestre`.** O vazamento pelo WebSocket existiu enquanto a
   `CV1.DS2.TS1` esteve em uso. Se o Navigator considerar que pode ter sido
   explorado em alguma instância, os códigos das salas existentes devem ser
   tratados como comprometidos e a rotação vira trabalho próprio.

### Como retomar

1. `git fetch origin && git checkout claude/subagentes-backlog-features-sqbsfs && git pull`
2. `cd web && npm install && npm run build && cd ..` antes de qualquer pytest.
3. Confirmar o baseline: `UV_HTTP_TIMEOUT=180 uv run pytest -q` deve dar 98 passed.
4. Decidir os dois primeiros pontos acima antes de disparar a onda de `CV2.DS3`.
5. Retomar a Onda 2 com dois agentes em worktrees isolados e propriedade de
   arquivo disjunta, como registrado no `CHANGELOG.md`: um para `CV2.DS2`
   (partindo de `wip/cv2-ds2-parcial`, já na base certa) e outro para `CV2.DS4`
   (partindo de `wip/cv2-ds4-parcial`, **rebaseando primeiro**).
6. Integrar em sequência, rodando a suíte inteira entre cada merge, e fechar os
   débitos correspondentes em `docs/project/debt/items/` na integração.

### Lição registrada

Sub agente em worktree deve commitar cada história assim que ela estiver
funcionando e testada, em vez de guardar tudo para um commit final. As duas
interrupções desta noite mostraram que trabalho não commitado em ambiente
efêmero é trabalho perdido, e que empurrar as branches de apoio para o remoto é
parte de preservar, não um detalhe de arrumação.
