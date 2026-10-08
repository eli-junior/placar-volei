---
id: recusa-do-segredo-e-bloqueio-sem-apagar
status: Decided
raised: 2026-10-08
decided: 2026-10-08
deciders:
  - Eli (Navigator)
  - Claude Sonnet 5.5 (Driver)
related:
  - CV8.DS7.US17
  - docs/qa/2026-10-08-auditoria-producao.md
---

# Recusa do segredo e bloqueio por tentativas sem apagar o segredo

## Question

Como o aparelho distingue "o servidor recusou o meu segredo" de um erro qualquer ou de um bloqueio temporário, sem revelar o endpoint a quem não tem segredo e sem apagar o segredo salvo por engano?

## Decision

- **Recusa é 404 sem `erros`.** O 404 mascarado do `validar_segredo_owner` não tem `erros`; o 404 de domínio (`erro_de_campo`) tem. O cliente marca `ErroJogadores.recusado` só no primeiro caso, e só ele (mais o WebSocket 4401) apaga o segredo salvo.
- **Bloqueio mantém o segredo.** 429 em HTTP mostra o tempo pelo `Retry-After`. No WebSocket do gerenciador o bloqueio fecha com **4429** (antes era 4401, igual à recusa); 4401 fica para segredo recusado e handshake inválido.
- **Sem segredo não é tentativa.** Cabeçalho ausente ou vazio (e WebSocket sem segredo) continua dando o mesmo 404, mas não chama `registrar_falha`. Segredo presente e errado conta como antes (5 falhas em 10 min bloqueiam o IP por 5 min).

## Rationale

O relatório do QA atribuiu a perda ao 429; no código, o 429 em HTTP não apaga nada. Quem apagava era qualquer 404 (HTTP) e o 4401 do WebSocket, que também cobria o bloqueio. Um sinal próprio de recusa revelaria o endpoint a quem não tem segredo; comparar o texto "Não encontrado." acopla ao texto. "404 sem `erros`" falha para o lado seguro: na dúvida, o segredo fica e o botão "Esquecer segredo neste aparelho" é a saída manual.

## Consequences

- Uma sondagem sem cabeçalho não bloqueia mais o dono. A força bruta segue limitada: só segredo presente e errado gasta tentativas.
- O aviso de 4429 não diz o tempo restante (o WebSocket não leva `Retry-After`).
- Um 404 de rota inexistente do framework (sem `erros`) seria lido como recusa; não ocorre nas telas.
- Quem opera sem o segredo do dono (QA F5.2) continua fora do Joguinho; é decisão de produto à parte.
