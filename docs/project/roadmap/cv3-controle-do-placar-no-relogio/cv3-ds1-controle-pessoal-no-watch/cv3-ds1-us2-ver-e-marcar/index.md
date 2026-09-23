---
code: CV3.DS1.US2
level: User Story
status: Done
status_reason: Validada em produção e entregue na 0.8.0 (2026-09-23)
updated: 2026-09-23
---

# CV3.DS1.US2 — Ver o placar e marcar pontos no pulso

## Intent
Como Eli jogando, quero ver o placar e tocar em dois botões grandes, um por equipe, para registrar o resultado de cada rally.

## Scope
App Wear OS nativo; pontuação legível em tela circular; identificação das equipes além de cor; dois alvos grandes; indicação de conexão e de lances pendentes; retorno visual imediato. A atualização local pendente não se apresenta como confirmação do servidor.

## Acceptance / Done Condition
- Dada uma partida ativa e controle autorizado, quando tocar na equipe A ou B, então um comando durável é registrado para aquela equipe e o placar mostra o resultado previsto.
- Quando o servidor confirmar, então as telas convergem e o lance consta uma única vez no histórico.
- Toques rápidos intencionais preservam ordem e quantidade; retransmissão não duplica pontos.
- Com telefone bloqueado e navegador em segundo plano, a operação deve funcionar pela rede disponível ao relógio.
- Ao voltar do modo ambiente, a tela recupera estado e fila; modo ambiente não registra toques de pontuação.
- Com partida encerrada confirmada, novos pontos são bloqueados; desfazer permanece disponível quando permitido.

## Validation Route
Watch real e espectador: sequência A, A, B; verificar 2×1 e três eventos. Repetir com telefone bloqueado, sob luz externa e com animações reduzidas. Verificar retomada ao levantar o pulso e ausência de comandos ao apagar a tela.

## Notes
- Entregue pela revisão 3 do [plano](plan.md): o relógio é o participante "Eli (Relógio)" e pontua quando o admin passa o controle para ele; `eli` em qualquer caixa habilita. Ver o registro de decisão `relogio-como-participante-com-controle-delegado`.
- Validado no relógio real: vínculo, participante próprio e pontuação com controle delegado. Os demais cenários do [roteiro](test-guide.md) têm cobertura automatizada no servidor, mas não foram confirmados um a um no aparelho.
- O envio acontece só com o app aberto; em segundo plano fica para a US4.
