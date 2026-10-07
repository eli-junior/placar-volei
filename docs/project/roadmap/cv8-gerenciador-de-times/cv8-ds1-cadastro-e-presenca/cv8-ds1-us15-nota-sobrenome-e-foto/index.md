---
code: CV8.DS1.US15
level: User Story
status: Validated
status_reason: validada pelo Navigator em 2026-10-07 (0.32.0); aguarda merge
updated: 2026-10-07
related:
  - ../cv8-ds1-us1-cadastrar-jogadores/index.md
---

# Nota, sobrenome e foto do jogador

## Intent

**Como** operador, **quero** registrar a nota (1 a 100), o sobrenome e, opcionalmente, a foto de cada jogador, **para** equilibrar as duplas pelo nível e identificar quem é quem. Estende a US1 (já entregue na 0.31.0); versão-alvo 0.32.0.

## Acceptance / Done Condition

- **CA1:** Nota inteira de 1 a 100; se não informada no cadastro, vale **60**. Fora da faixa é recusada com mensagem no campo.
- **CA2:** Nome e sobrenome no **mesmo campo**, que passa a exigir **ao menos 2 palavras** ("Ana" é recusado; "Ana Souza" vale). A unicidade entre ativos segue como na US1. Jogadores da 0.31.0 com uma palavra só continuam válidos, mas a edição exige completar o nome.
- **CA3:** Foto opcional; cadastrar e editar funcionam sem ela. A tela de cadastro tem um **botão de câmera**: o operador tira a foto na hora e a aplicação faz o **upload ao servidor**. O plano define formato, redução no aparelho, tamanho máximo, onde o arquivo mora (no volume `gerenciador-dados`, para sobreviver ao reset) e como a câmera abre no celular.
- **CA4:** Jogadores já cadastrados na 0.31.0 recebem nota 60 (migração aditiva do `gerenciador.db`, sem perder dados).
- **CA5:** Mesma proteção da US1: tudo pelo `OWNER_SECRET`, tela oculta no APK.

Regras: RN-14 (nota e sorteio), RN-05 e RN-13/RN-15 não mudam por esta história (a nota alimenta o sorteio equilibrado). Ver [regras-de-negocio.md](../../regras-de-negocio.md).

## Entregue

Nota 1–100 (padrão 60), nome com ao menos 2 palavras e foto opcional (câmera, JPEG reduzido, BLOB no `gerenciador.db`). Plano: [plan.md](plan.md). Validação: [test-guide.md](test-guide.md).

## Validation Route

A definir no plano (Passo 2).

## Out of Scope

Ajuste automático da nota pelo saldo (depende da decisão da RN-14); histórico entre sessões.
