---
id: sessao-unica-presenca-e-ordem-de-chegada
status: Decided
raised: 2026-10-07
decided: 2026-10-07
deciders:
  - Eli (Navigator)
  - Claude Sonnet 5.5 (Driver)
related:
  - CV8.DS1.US2
  - base-de-jogadores-duravel-e-protegida
---

# Sessão Única, Presença e Ordem de Chegada

## Question

Como garantir uma sessão aberta por vez e registrar a ordem de chegada editável (RN-13, RN-15) no `gerenciador.db`?

## Decision

- **Esquema 3** do `gerenciador.db` (aditivo): `sessoes` e `presencas`. Um **índice único parcial por expressão constante** (`ON sessoes ((1)) WHERE encerrada_em IS NULL`) garante no banco uma só sessão aberta, mesmo com aberturas concorrentes.
- **Ordem de chegada** é a coluna `ordem`, de 1 a N. Marcar entra no fim; desmarcar renumera; marcar de novo vai ao fim. Reordenar recebe a lista completa e ordenada dos presentes e a grava de forma atômica (lista que não bate com os presentes é recusada, 422). A renumeração é feita linha a linha, porque um `UPDATE` com subconsulta pode empatar posições.
- **Escritas** da sessão usam `BEGIN IMMEDIATE`, para que dois operadores não recebam a mesma posição.
- **Encerrar sessão** entra (não estava nos CAs): sem ele o CA1 travaria o sistema. As linhas ficam gravadas; não há tela de histórico (US-12).
- **Inativar** um jogador presente o tira da presença (com renumeração); reativar não o recoloca.
- **Acesso:** continua o `OWNER_SECRET`, como a base de jogadores. A RN-12 ("qualquer dispositivo opera") volta como tema na DS3, quando houver rodada e sincronia (US-05).
- **Mínimo de 4 (RN-11)** aparece como aviso na tela; o bloqueio do sorteio é da US-03. A trava da reordenação antes do sorteio (RN-15) também é da US-03.

## Rationale

- Uma regra de unicidade no banco vale mesmo com vários processos ou pedidos simultâneos; checar no código não valeria.
- Coluna `ordem` explícita é mais simples e fiel que sobrescrever horários de chegada.

## Options Considered

- Arrastar para reordenar: pior acessibilidade e mais código.
- Sessão que fecha sozinha à meia-noite: esconde estado.
- Presenças como JSON dentro da sessão: impediria chave única e consultas das próximas histórias.
