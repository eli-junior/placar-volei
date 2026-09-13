---
code: CV1.DS1.TS1
kind: plan
status: Approved
approved_by: Navigator
approved: 2026-09-13
updated: 2026-09-13
---

# Plano — CV1.DS1.TS1 Fundação do backend e event store

Plano aprovado pelo Navigator no Checkpoint 1 em 2026-09-13. Implementação adiada por decisão dele. Este documento é o contrato do que será construído quando a story for puxada.

## Nível e versão

Technical Story. Trabalho dentro de `0.1.0`. Não fecha versão.

## Restrição de operação vigente

O shell na máquina do Navigator está indisponível desde a atualização do Windows de 2026-09-08. Enquanto durar:

- O Driver escreve os arquivos no container e grava em `D:\projetos\placar_volei`.
- Testes rodam no container do Driver.
- `uv sync`, execução local e `git` ficam com o Navigator.
- Alternativa disponível: Claude Code na máquina do Navigator não é afetado e pode assumir a execução.

## Escopo

Esqueleto FastAPI, schema SQLite, tipos de evento, append serializado, projeção determinística, reconstrução de estado sob demanda e hub de conexões WebSocket.

Nenhuma rota de jogo, nenhuma tela.

## Estrutura de arquivos

```text
app/
  main.py          # app FastAPI, lifespan, montagem de estáticos
  config.py        # settings via .env (pydantic-settings)
  db.py            # conexão SQLite, WAL, migração inicial
  eventos.py       # tipos de evento + append serializado
  projecao.py      # log -> EstadoPartida (função pura)
  hub.py           # conexões WebSocket por quadra
tests/
  test_projecao.py
  test_eventos.py
.env.example
```

## Modelo de dados

Quatro tabelas: `quadras`, `partidas`, `participantes`, `eventos`.

Envelope do evento:

| campo | descrição |
|---|---|
| `id` | uuid |
| `quadra_id` | quadra a que pertence |
| `partida_id` | partida a que pertence |
| `seq` | inteiro monotônico dentro da partida |
| `tipo` | tipo do evento |
| `payload` | JSON com os dados específicos do tipo |
| `autor_id` | participante que originou o evento |
| `criado_em` | timestamp UTC |

Constraint `UNIQUE(partida_id, seq)`.

Tipos de evento do MVP: `PARTIDA_INICIADA`, `PONTO_MARCADO`, `PONTO_DESFEITO`, `REGRA_ALTERADA`, `PARTIDA_ENCERRADA`, `PAPEL_ALTERADO`, `ADMIN_SUCEDIDO`, `ADMIN_ASSUMIDO`.

## Decisões de design

### Serialização do append

`asyncio.Lock` por quadra na camada de aplicação, com `UNIQUE(partida_id, seq)` como rede de segurança no banco.

Dois controladores marcando ponto no mesmo instante produzem sequência determinística. Uma corrida que escape do lock falha ruidosamente em vez de gravar sequência ambígua.

### Desfazer na projeção

`PONTO_DESFEITO` carrega `ref_seq` apontando o evento de ponto anulado.

A projeção varre o log uma vez, coleta os `ref_seq` anulados e ignora esses pontos ao somar.

Duas consequências desejadas:

- Desfazer é idempotente por referência.
- Desfazer o ponto da vitória devolve a partida ao estado não encerrado sem tratamento especial, resolvendo o pendente registrado em `CV1.DS1.US4`.

### Configuração de regra alterada no meio da partida

A projeção aplica a configuração **vigente no momento da avaliação**, não a do início da partida.

Alterar a regra em 11x11 muda o desfecho imediatamente. É o comportamento especificado pelo Navigator em `CV1.DS3.US1` e decorre do princípio "a quadra manda, o software obedece".

### Acesso ao SQLite

`sqlite3` da stdlib executado em `asyncio.to_thread`, com WAL ligado.

Sem SQLAlchemy, sem aiosqlite. O modelo são quatro tabelas e o padrão de acesso é append mais leitura completa por partida.

Alternativa rejeitada: **SQLAlchemy** — ganha em migração de schema, perde em transparência de um log append-only, que é o coração do sistema.

### Reconstrução de estado

Sob demanda, por quadra, no primeiro acesso, com cache em memória.

Não reconstrói tudo no boot: uma quadra que ninguém abriu não precisa existir na RAM.

### Fuso horário

Todo timestamp gravado em UTC. Conversão para `America/Sao_Paulo` acontece apenas na exibição.

### Configuração

`.env` com caminho do banco, segredo de owner e timeout de sucessão do admin. `.env.example` versionado, `.env` nunca.

### Ferramentas

Python 3.12, `uv`, `ruff`, `pytest`. Sem `mypy` por ora.

## Aceite

Given uma sequência de eventos gravada no log
When a projeção é executada sobre essa sequência
Then o estado resultante é idêntico ao esperado
And executar de novo sobre o mesmo log produz exatamente o mesmo estado.

## Fora de escopo

Rotas HTTP de jogo, sessão e papéis, endpoint de owner, frontend, `Dockerfile` e `docker-compose` (ver `CV1.DS1.TS2`).

## Riscos

1. **Comandos do development guide não verificados** — foram escritos sem execução. Corrigir ao fechar esta story, com o retorno da primeira execução do Navigator.
2. **Migração de schema** — o log é append-only inclusive em migração. Definir a estratégia mínima antes da primeira partida real gravada.
3. **Contador de sequência após restart** — o `seq` seguinte precisa vir do banco, nunca de estado em memória.
