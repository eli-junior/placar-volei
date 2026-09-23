---
code: CV3.DS1.US1
level: User Story
status: Active
status_reason: Plano aprovado; implementando vínculo do relógio
updated: 2026-09-22
---

# CV3.DS1.US1 — Vincular o relógio pelo telefone

## Intent
Como Eli, quero autorizar meu relógio na sala já configurada pelo telefone para operar sem redigitar configurações no pulso.

## Scope
Vínculo de dispositivo com credencial própria e revogável, identificação interna `eli-smartwatch` e nome público `eli`. O apelido não concede acesso; autorização depende do vínculo autenticado. Proposta: telefone e relógio representam o mesmo participante, com dispositivos distintos, evitando duplicação de Eli na lista e disputa entre suas próprias sessões. Essa modelagem depende do aceite do plano.

## Acceptance / Done Condition
- Dada a sala configurada e Eli autorizado, quando aprovar o código temporário mostrado pelo relógio no telefone, então o relógio acessa somente a sala autorizada.
- Dado um espectador, quando tentar autorizar controle, então o backend rejeita a operação.
- Dado código expirado, reutilizado ou tentativas excessivas, então o vínculo é recusado.
- Dado vínculo revogado, então novos comandos são recusados e a fila pendente permanece identificada para revisão.
- Outros participantes e a linha do tempo exibem `eli`, sem expor credenciais nem o identificador técnico.

## Validation Route
Telefone admin, Watch e navegador espectador: autorizar, verificar nome público, tentar acesso indevido e revogar; observar permissão nas três telas.
