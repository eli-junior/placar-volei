---
id: relogio-como-participante-com-controle-delegado
status: Decided
date: 2026-09-23
source: feature/cv3-ds1-us2-ver-e-marcar (CV3.DS1.US2, revisão 3 do plano)
supersedes: apelido-senha-habilita-relogio; decisão 1 do plano da CV3.DS1 ("relógio como dispositivo de Eli, sem participante duplicado")
---

# Relógio Como Participante Próprio, com Controle Delegado; `eli` em Qualquer Caixa Habilita

## Context

A US1 vinculou o relógio como mais um dispositivo do participante `eli` e habilitou o vínculo pelo apelido-senha `eli.relogio`. A revisão 2 da US2 somou uma chave de sala, "Controlar pelo Relógio", para impedir o site de pontuar enquanto o relógio operasse.

No teste físico da US2, o Navigator criou a sala como `eli` e recebeu "não habilitado". Ele redirecionou o desenho: o apelido-senha era atrito sem ganho real para um recurso pessoal, e o relógio deveria aparecer na sala como alguém a quem o controle pudesse ser delegado.

## Decision

- `eli`, `ELI` ou `Eli` entram gravados como **`Eli`** e recebem a habilitação do relógio (`WATCH_AUTO_GRANT`, padrão `eli`). O apelido-senha deixa de existir.
- Aprovar o código cria o participante **"Eli (Relógio)"** (`<dono> (Relógio)`), como espectador. `watch_devices.owner_id` guarda o dono; o relógio vale enquanto o dono estiver habilitado e for ADMIN ou CONTROLADOR.
- O admin promove o relógio e usa **Passar controle**. Quem tem o controle pontua, pelas mesmas regras do site. Não há chave de sala.
- O controle nas mãos de um relógio **não** é devolvido por ausência. O admin retoma com "Assumir o controle".
- O relógio conectado, ou visto dentro da janela, conta como presença do dono para a sucessão de admin.
- Revincular reaproveita o participante (papel e controle). Revogar remove o participante e devolve o controle ao dono.

## Rationale

- A delegação reaproveita o modelo de controle que o site já tinha: uma só regra de quem pontua, auditável na linha do tempo, sem um segundo interruptor.
- A tela do relógio apaga durante o jogo. Com a devolução por ausência (15 s), o relógio perderia o controle a cada rally.
- O telefone fica bloqueado no bolso. Sem contar o relógio como presença do dono, o admin seria sucedido em 2 minutos.

## Consequences

- `eli` é um nome público. Numa sala sem o Eli, quem entrar como `eli` pode vincular um relógio naquela sala, que ele mesmo controla. Aceito para o uso pessoal atual.
- Se o relógio ficar sem bateria com o controle, o admin precisa tocar em "Assumir o controle".
- O `.env` do Mini PC com `WATCH_AUTO_GRANT=eli.relogio` precisa passar para `eli`.
- O "Eli (Relógio)" ocupa uma vaga na lista de presentes e conta na capacidade da sala.
