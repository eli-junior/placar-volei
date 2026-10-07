---
code: CV8.DS1.US15
level: User Story
status: Planned
status_reason: registrada em 2026-10-07 a partir do pedido do Navigator; perguntas em aberto abaixo
updated: 2026-10-07
related:
  - ../cv8-ds1-us1-cadastrar-jogadores/index.md
---

# Nota, sobrenome e foto do jogador

## Intent

**Como** operador, **quero** registrar a nota (1 a 100), o sobrenome e, opcionalmente, a foto de cada jogador, **para** equilibrar as duplas pelo nível e identificar quem é quem. Estende a US1 (já entregue na 0.31.0); versão-alvo 0.32.0.

## Acceptance / Done Condition

- **CA1:** Nota inteira de 1 a 100; se não informada no cadastro, vale **60**. Fora da faixa é recusada com mensagem no campo.
- **CA2:** Sobrenome registrado junto do nome; o nome completo (nome + sobrenome) continua único entre ativos. *Em aberto:* campos separados ou o campo único atual?
- **CA3:** Foto opcional; cadastrar e editar funcionam sem ela. *Em aberto:* só envio de arquivo, ou captura pela câmera? Tamanho máximo e formato.
- **CA4:** Jogadores já cadastrados na 0.31.0 recebem nota 60 (migração aditiva do `gerenciador.db`, sem perder dados).
- **CA5:** Mesma proteção da US1: tudo pelo `OWNER_SECRET`, tela oculta no APK.

Regras: RN-14 (a nota alimenta o sorteio equilibrado). Ver [regras-de-negocio.md](../../regras-de-negocio.md).

## Validation Route

A definir no plano (Passo 2).

## Out of Scope

Ajuste automático da nota pelo saldo (depende da decisão da RN-14); histórico entre sessões.
