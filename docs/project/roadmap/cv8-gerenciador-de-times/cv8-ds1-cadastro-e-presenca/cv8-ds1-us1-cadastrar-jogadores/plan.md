# Plano — CV8.DS1.US1 Cadastrar jogadores

Nível: User Story. Branch: `feature/cv8-ds1-us1-cadastrar-jogadores`. Versão-alvo: **0.31.0** (minor, capacidade nova; backend, web e APK; Wear inalterado).

## Achados que mudam o desenho

1. **O banco é efêmero por decisão do Navigator (2026-09-27).** `RESET_DB_ON_STARTUP=true` no compose apaga tudo a cada start, e uma mudança no DDL (`SCHEMA_VERSAO`) também recria o banco. O CA3 ("dados persistem entre reinícios") não pode viver nesse banco.
2. **O compose não tem volume para `/data`.** Mesmo sem o reset, o arquivo morre junto com o contêiner recriado.
3. **Não há conceito de operador.** Hoje só existe sessão por quadra (cookie) e o `OWNER_SECRET` (header `x-owner-secret`, com rate limit). A RN-12 diz que qualquer dispositivo conectado opera a rodada, mas a base de jogadores é um dado persistente e sem dono.

## Escopo

- **Armazenamento separado:** segundo arquivo SQLite (`GERENCIADOR_DB_PATH`, padrão `data/gerenciador.db`), com migração própria e **sem** reset nem apagar-por-schema. O banco das quadras continua efêmero, como está.
- **Compose:** volume nomeado `gerenciador-dados` montado em `/data-gerenciador`; `RESET_DB_ON_STARTUP` não toca nesse arquivo.
- **Tabela `jogadores`:** `id`, `nome`, `gerero`→`genero` (`H`|`M`), `ativo`, `criado_em`, `atualizado_em`.
- **API** (`/api/jogadores`): `GET` (ativos; `?incluir_inativos=1`), `POST`, `PATCH /{id}` (nome, gênero), `POST /{id}/inativar`, `POST /{id}/reativar`.
- **Regras:** nome obrigatório (aparado, até 40 caracteres); gênero obrigatório; nome único **entre ativos**, sem diferenciar maiúsculas/acentos (`João` = `joao`); inativar libera o nome; reativar recusa se o nome já estiver em uso por outro ativo.
- **Web:** tela "Jogadores" acessível pela home: lista, formulário criar/editar, inativar/reativar, erros de validação visíveis.
- **Testes:** pytest (regras, unicidade, persistência entre `init` repetido e com `RESET_DB_ON_STARTUP`), Playwright/axe da tela.

## Aceite (BDD)

- Given a base vazia, When crio "Ana" (M), Then ela aparece na lista de ativos.
- Given "Ana" ativa, When tento criar "ana" ou "ANA", Then recebo erro de nome já em uso e nada é gravado.
- Given um nome em branco ou sem gênero, When salvo, Then o formulário aponta o campo e nada é gravado.
- Given "Ana" ativa, When a inativo, Then some da lista de ativos e posso criar outra "Ana".
- Given jogadores cadastrados, When o servidor reinicia (inclusive com `RESET_DB_ON_STARTUP=true` e com release que muda o schema das quadras), Then todos continuam lá.

## Alternativas rejeitadas

- **Mesmo banco das quadras, poupando a tabela no reset:** acopla o ciclo de vida de dados duráveis ao de dados descartáveis; qualquer mudança de DDL das quadras voltaria a ameaçar os jogadores.
- **Tirar o reset do compose:** reverte decisão do Navigator e afeta quadras e relógio.
- **Persistir no navegador/celular:** não sincroniza entre dispositivos (RN-12).

## Fora do escopo

Sessão e presença (US2), qualquer uso dos jogadores no sorteio, histórico/ranking, backup/exportação do arquivo, apelido ou foto.

## Riscos e perguntas ao Navigator

1. **Quem pode escrever na base?** Opções: (a) qualquer pessoa com o link (coerente com a RN-12, mas a base fica aberta na internet via túnel); (b) exigir o `OWNER_SECRET` (digitado uma vez na tela e guardado no aparelho). **Recomendo (b)**: é a única proteção que já existe, e o dado é persistente.
2. **Volume no Mini PC:** aceita criar o volume `gerenciador-dados` (primeiro dado durável do projeto)? Sem ele o CA3 só vale para reinício sem recriar o contêiner.
3. **APK offline:** a tela de jogadores só funciona online (a base mora no servidor). No modo quadra local ela fica oculta. Ok?
