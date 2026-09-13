---
date: 2026-09-13T14:30:00Z
author: Claude (Driver)
kind: milestone
related:
  - CV1
verification:
  - revisão do Navigator sobre a especificação de regras de negócio antes da escrita dos documentos
---

# Regras de negócio do MVP definidas e Ariad configurado

## What changed

O repositório tinha apenas os templates do Ariad, sem conteúdo. Após uma sessão de elucidação com o Navigator, ficaram definidas as regras de negócio do MVP e a instância local do método foi preenchida:

- `README.md` criado.
- `docs/project/briefing.md` preenchido com propósito, premissas de arquitetura e de produto, restrições e glossário.
- `docs/product/principles.md` preenchido com seis princípios e uma ordenação explícita de custo de falha.
- Seis decisões registradas em `docs/project/decisions/records/`, cinco `Decided` e uma `Open` (stack do frontend).
- Roadmap montado: `CV1` com quatro Delivery Stories, oito User Stories e duas Technical Stories.
- `docs/process/development-guide.md` preenchido nas seções de comandos, verificação, preferências do Navigator e exceções locais.

Decisões de produto tomadas nesta sessão: log de eventos como fonte da verdade; identidade por apelido preso à sessão, obrigatória inclusive para espectadores; primeiro a entrar vira admin e delega controladores; sucessão automática após 2 minutos de admin offline; owner takeover por código de 4 dígitos por quadra, consultável em endpoint protegido, com rate limit e visível na linha do tempo; set único com alvo, vantagem de 2 e teto configuráveis; encerramento com reinício automático e sem contador de vitórias; desfazer ponto a ponto até zerar; linha do tempo da partida; SQLite como persistência única.

## Why it matters

O projeto passa a ter memória. As regras que o Navigator carregava na cabeça agora estão em documento, e a próxima sessão de trabalho começa lendo em vez de perguntando.

O registro das decisões preserva também o que foi **rejeitado** e por quê — takeover silencioso, senha mestra global, código derivado de segredo, estado só em memória — o que evita re-litigar as mesmas escolhas.

## Verification

Especificação consolidada apresentada ao Navigator e aprovada antes da escrita dos documentos. Documentos ainda não exercitados por nenhuma sessão de implementação.

## Follow-up

- Decidir a stack do frontend antes de iniciar `CV1.DS1.US2`.
- Confirmar e corrigir a seção de comandos do development guide ao fechar `CV1.DS1.TS1`.
- O `index.md` da raiz ainda é o texto do repositório de templates do Ariad e não descreve este projeto. Decidir se é removido ou reescrito.
