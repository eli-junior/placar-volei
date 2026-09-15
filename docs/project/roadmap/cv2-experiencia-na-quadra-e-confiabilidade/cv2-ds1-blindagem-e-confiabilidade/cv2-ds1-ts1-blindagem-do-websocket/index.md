---
code: CV2.DS1.TS1
level: Technical Story
status: Validated
status_reason: implementada e testada, aguardando validação do Navigator
updated: 2026-09-15
related:
  - CV1.DS2.TS1
  - docs/project/debt/items/2026-09-15T2200Z-codigo-mestre-vaza-no-snapshot-websocket.md
---

# CV2.DS1.TS1 — Blindagem do snapshot do WebSocket com allowlist de campos públicos

## Intent

Impedir que o `codigo_mestre` — e qualquer coluna sensível futura da tabela `quadras` — saia do servidor pelo canal WebSocket, trocando o reflexo automático de `SELECT *` por um contrato explícito do que é público.

## Scope

- `app/comandos.py`: constante `CAMPOS_PUBLICOS_QUADRA` com a allowlist de campos da tabela `quadras` que podem sair da borda, consulta `_SELECT_QUADRA_PUBLICA` derivada dessa allowlist e função `projetar_quadra_publica()` aplicada à chave `quadra` do snapshot.
- `snapshot()` e `executar_sync()` deixam de usar `SELECT * FROM quadras`.
- Testes de integração conectando um participante **espectador** ao WebSocket e afirmando a ausência da chave e do valor do código mestre em `ESTADO_INICIAL` e em `PLACAR_ATUALIZADO`.
- Teste que adiciona uma coluna sensível nova (`token_de_operacao`) à tabela e confirma que ela não aparece no snapshot sem alteração deliberada da allowlist.

## Acceptance / Done Condition

- Nenhum frame recebido por um espectador contém a chave `codigo_mestre` nem o valor do código mestre da sala.
- A chave `quadra` do payload contém exatamente os campos da allowlist mais `partida_id`.
- Uma coluna criada depois em `quadras` fica fora do payload por padrão.
- A suíte automatizada cobre os dois tipos de frame (`ESTADO_INICIAL` e `PLACAR_ATUALIZADO`).

## Validation Route

1. Subir o backend e criar uma sala.
2. Entrar como espectador em outro navegador e inspecionar os frames do WebSocket na aba Network → WS do DevTools.
3. Buscar por `codigo_mestre` no conteúdo dos frames: a busca precisa não encontrar nada.
4. `uv run pytest tests/test_blindagem_e_confiabilidade.py -k codigo_mestre`.

## Out of Scope

- Blindagem das rotas REST, já entregue e testada na `CV1.DS2.TS1`.
- Rotação ou reemissão do `codigo_mestre` das salas já criadas (nenhum vazamento conhecido em produção; se o Navigator quiser rotacionar, vira trabalho próprio).
- Criptografia do canal ou autenticação adicional do WebSocket.

## Notes

Classificada como Technical Story porque não muda nenhuma superfície observável pelo usuário: o placar continua idêntico na tela. O que muda é o contrato interno de projeção, verificável por teste e por inspeção do tráfego.

O desenho escolhido troca uma correção pontual ("não mande esta coluna") por uma inversão de padrão ("só sai o que está declarado"). Foi exatamente o comportamento implícito do `SELECT *` que transformou uma coluna nova em vazamento sem que ninguém escrevesse uma linha errada.
