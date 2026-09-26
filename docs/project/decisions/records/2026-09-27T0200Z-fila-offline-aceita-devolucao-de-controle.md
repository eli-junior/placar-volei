---
id: fila-offline-aceita-devolucao-de-controle
status: Decided
raised: 2026-09-26
decided: 2026-09-26
deciders:
  - Eli (Navigator)
  - Claude Opus 5.5 (Driver)
related:
  - CV3.DS1.TS1
  - CV3.DS1.US4
---

# Fila Offline Aceita a Devolução do Controle ao Relógio

## Question

Toda troca de controle incrementa `controle_versao`. Se o controle sai do relógio e volta a ele enquanto há lances na fila, a versão vista no toque ficou velha e o servidor recusa tudo. Quando a fila deve valer mesmo assim?

## Decision

- Cada lance leva `base_seq`: o último seq confirmado que o relógio viu no toque.
- O servidor usa a versão atual do controle se: o controle está com este relógio, o token é válido, a partida é a mesma e, depois de `base_seq`, só houve eventos de controle (`CONTROLE_*`, `PAPEL_ALTERADO`, `ADMIN_*`) ou pontos e desfazer do próprio relógio.
- Qualquer outro evento (ponto alheio, regra, partida nova ou encerrada) mantém a recusa estrita; a revisão é da CV3.DS1.US4.
- Sem `base_seq` (APK antigo), vale a versão estrita. Nova partida pelo relógio não usa a regra.

## Rationale

- O Navigator decidiu que, na devolução, basta o token de vínculo válido; revogação continua nunca ignorada (token revogado responde 401).
- O servidor tem o log de eventos: decidir "partida inalterada" lá evita confiar em estado guardado no relógio.

## Options Considered

- Relógio reescrever a versão da fila ao ver o controle de volta: não sabe se alguém pontuou no intervalo sem reler o log.
- Exigir nova autorização explícita no telefone: rejeitada pelo Navigator; atrapalha o jogo sem ganho de segurança.

## Consequences

- `EVENTOS_DE_CONTROLE` em `app/watch.py` é mantida à mão. Tipo novo fora da lista recusa a fila (lado seguro); incluir nela um evento que muda o placar seria um erro.

## Review Trigger

Novo tipo de evento no log, ou sincronização offline entre vários operadores.
