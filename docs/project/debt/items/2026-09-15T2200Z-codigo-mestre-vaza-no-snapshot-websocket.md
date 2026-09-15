---
id: debt-codigo-mestre-no-websocket
status: Paying
kind: security
severity: high
source: CV1.DS2.TS1
revisit_trigger: Qualquer alteração em app/comandos.py::snapshot ou no payload de ESTADO_INICIAL
closure_condition: Nenhum pacote de WebSocket recebido por espectador contém a chave codigo_mestre, com teste automatizado de asserção
---

# `codigo_mestre` Vaza no Snapshot do WebSocket

## Description

`snapshot()` em `app/comandos.py` monta a chave `quadra` do payload a partir de `dict(quadra)` sobre um `SELECT * FROM quadras`. Como a `CV1.DS2.TS1` adicionou a coluna `codigo_mestre` à tabela, o segredo de owner passou a ser incluído automaticamente em todo `ESTADO_INICIAL` e `PLACAR_ATUALIZADO` transmitido pelo hub.

As rotas REST foram blindadas explicitamente na TS1 (`tests/test_owner_endpoint.py::test_rotas_publicas_nao_vazam_codigo_mestre` cobre `POST /api/quadras`, listagem, detalhe e partida), mas o canal WebSocket não recebeu a mesma blindagem nem cobertura de teste. Qualquer espectador conectado à sala recebe o código mestre no primeiro frame.

## Carrying Reason

O débito não foi carregado por decisão consciente: ele nasceu do acoplamento entre `SELECT *` e uma coluna sensível adicionada depois, sem que a suíte de testes cobrisse o canal WebSocket. Foi identificado no relatório de Frontend, UX e Design Visual de 2026-09-15 (item C1).

## Revisit Trigger

Qualquer alteração na projeção do snapshot ou adição de nova coluna sensível em `quadras`.

## Closure Condition

Projeção de snapshot com allowlist explícita de campos públicos (nunca `SELECT *` refletido direto no payload) e teste de integração que conecta um participante espectador e afirma a ausência de `codigo_mestre` no frame recebido.

## Notes

Pago por `CV2.DS1` (escopo C1).
