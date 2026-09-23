---
id: apelido-senha-habilita-relogio
status: Superseded
superseded_by: relogio-como-participante-com-controle-delegado
date: 2026-09-23
source: feature/cv3-ds1-us1-vincular-relogio (CV3.DS1.US1, Checkpoint 3)
supersedes: none
---

# Apelido-Senha Habilita o Relógio, e a Sala Vê Só o Nome Público

> Substituída em 2026-09-23 por `relogio-como-participante-com-controle-delegado` (CV3.DS1.US2): `eli` em qualquer caixa passou a habilitar o relógio.

## Context

O plano aprovado da US1 exigia que o owner habilitasse o participante `eli` em cada sala com `scripts/watch_access.py` e o segredo de owner. No teste físico isso pesou: cada sala nova, e cada recriação do contêiner (o banco não fica em volume), pedia terminal e segredo.

Uma primeira tentativa (`29d70d7`, `WATCH_AUTO_GRANT=eli`) habilitava por apelido: qualquer pessoa que entrasse como `eli` com papel de controle ganhava o vínculo. Como o apelido é público, qualquer um podia copiá-lo do placar.

## Decision

`WATCH_AUTO_GRANT` lista **apelidos-senha** (padrão `eli.relogio`). Quem cria ou entra na sala com um deles:

- é gravado e exibido só pelo trecho antes do ponto (`eli`), então o sufixo nunca aparece em presença, linha do tempo ou snapshot;
- recebe um registro em `watch_grants`, igual ao da habilitação pelo owner.

Digitar apenas `eli` não habilita nada. A autorização continua dependendo de papel ADMIN/CONTROLADOR e da aprovação do código temporário no telefone. `watch_access.py` fica como alternativa quando `WATCH_AUTO_GRANT` está vazio.

## Rationale

- O nome público é o que os outros veem; o apelido-senha é o que só o dono digita. Assim o acesso não pode ser copiado olhando o placar.
- Gravar o nome público no banco evita tocar em todos os pontos que exibem apelido.
- A unicidade de apelido por quadra já impede um segundo `eli` enquanto o dono estiver na sala.

## Consequences

- O apelido-senha padrão está no `docker-compose.yml` de um repositório público. O dano possível é pequeno: quem o usar só vincula o próprio relógio à sala que ele mesmo controla. Para restringir, defina outro valor em `.env` no Mini PC.
- Se alguém já estiver como `eli` na sala, entrar como `eli.relogio` é recusado por apelido em uso.
- O site guarda o apelido digitado só no aparelho do dono, para preencher na próxima vez.
