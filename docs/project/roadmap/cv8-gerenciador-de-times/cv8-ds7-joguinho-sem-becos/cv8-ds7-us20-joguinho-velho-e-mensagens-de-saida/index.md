---
code: CV8.DS7.US20
level: User Story
status: Done
status_reason: validada pelo Navigator em 2026-10-08 (0.47.0); recriar a quadra ficou fora (recriar-quadra-nao-vira-botao)
updated: 2026-10-08
---

# Joguinho de ontem e mensagens que ensinam a saída

## Intent

**Como** operador, **quero** saber que o joguinho aberto é de outro dia e ler mensagens que digam o que fazer, **para** não ficar preso num estado velho (QA F1.5, F4, F5.1, F5.3).

## Acceptance

- **Dado** um joguinho aberto em dia anterior **quando** abro a tela **então** vejo "Joguinho aberto em <data>" com as opções continuar ou encerrar.
- **Dado** "Encerrar joguinho" bloqueado por rodada ativa **então** a mensagem diz o que se perde ao cancelar e oferece a ação ali.
- **Dado** "Cancelar rodada" **então** a confirmação resume o que se perde (partidas, reis, fila).
- **Dado** qualquer botão desabilitado no painel da rodada **então** o motivo aparece junto dele.
