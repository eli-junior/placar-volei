---
code: CV3.DS1.US1
level: User Story
status: Active
status_reason: Validação física aprovada em produção (Checkpoint 2, 2026-09-23); revisão aprovada; habilitação por apelido-senha em validação
updated: 2026-09-23
---

# CV3.DS1.US1 — Vincular o relógio pelo telefone

## Intent
Como Eli, quero autorizar meu relógio na sala já configurada pelo telefone para operar sem redigitar configurações no pulso.

## Scope
Vínculo de dispositivo com credencial própria e revogável, identificação interna `eli-smartwatch` e nome público `eli`. O apelido não concede acesso; autorização depende do vínculo autenticado. Proposta: telefone e relógio representam o mesmo participante, com dispositivos distintos, evitando duplicação de Eli na lista e disputa entre suas próprias sessões. Modelagem aprovada pelo Navigator no Checkpoint 1. No Checkpoint 3 o Navigator definiu a habilitação pelo apelido-senha `eli.relogio` (exibido como `eli`), registrada em `docs/project/decisions/records/2026-09-23T1300Z-apelido-senha-habilita-relogio.md`.

## Acceptance / Done Condition
- Dada a sala configurada e Eli autorizado, quando aprovar o código temporário mostrado pelo relógio no telefone, então o relógio acessa somente a sala autorizada.
- Dado um espectador, quando tentar autorizar controle, então o backend rejeita a operação.
- Dado código expirado, reutilizado ou tentativas excessivas, então o vínculo é recusado.
- Dado vínculo revogado, então novos comandos são recusados e a fila pendente permanece identificada para revisão.
- Outros participantes e a linha do tempo exibem `eli`, sem expor credenciais nem o identificador técnico.

## Validation Route
Telefone admin, Watch e navegador espectador: autorizar, verificar nome público, tentar acesso indevido e revogar; observar permissão nas três telas.
