---
code: CV1.DS1.US1
level: User Story
status: Done
status_reason: atualizado para fluxo direto de salas com código PIN de 5 dígitos, criador como admin, espectador via código, limite de 20 salas/participantes e TTL de 1h
updated: 2026-09-14
related:
  - 2026-09-13T1405Z-identidade-por-apelido-e-sessao
  - 2026-09-14T1625Z-salas-por-codigo-pin-de-5-digitos
---

# CV1.DS1.US1 — Criar quadra e entrar por apelido (Salas com PIN de 5 dígitos)

## Intent

Chegar na quadra, abrir a página e estar dentro do jogo em poucos segundos, sem cadastro, com um código PIN de 5 dígitos fácil de compartilhar.

## Scope

Tela inicial direta com opções de **Criar Placar** ou **Acompanhar** via código PIN de 5 dígitos, geração aleatória de código (`10000` a `99999`), criador como `ADMIN`, ingressante como `ESPECTADOR`, exibição destacada do código no topo da sala, limites de capacidade (20 salas e 20 participantes por sala) e expiração automática por inatividade de 1 hora.

## Acceptance / Done Condition

Given a tela inicial aberta
When o usuário clica em "Criar Placar" e informa seu apelido
Then uma sala com código numérico de 5 dígitos é criada
And o criador entra como ADMIN com o código destacado no topo da tela
When outro usuário informa o código da sala e seu apelido em "Acompanhar"
Then ele entra imediatamente na sala como ESPECTADOR
And salas sem atividade por mais de 1 hora são eliminadas automaticamente
And o sistema impede a criação de mais de 20 salas simultâneas ou mais de 20 pessoas por sala.

## Validation Route

Abrir duas abas/navegadores: na primeira, criar placar informando apelido e verificar o código de 5 dígitos gerado no topo e papel ADMIN; na segunda, digitar o código e apelido em Acompanhar e verificar entrada como ESPECTADOR e sincronização em tempo real.

## Out of Scope

Proteção por senha de espectador, controle avançado de permissões granulares além de Admin/Espectador.

## Notes

Decisão registrada em `docs/project/decisions/records/2026-09-14T1625Z-salas-por-codigo-pin-de-5-digitos.md`.
