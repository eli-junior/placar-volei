# Plano de Implementação — CV2.DS1.TS1: Blindagem do snapshot do WebSocket

## 1. Contexto e Intenção

`snapshot()` em `app/comandos.py` montava a chave `quadra` do payload com `dict(quadra)` sobre um `SELECT * FROM quadras`. Quando a `CV1.DS2.TS1` adicionou a coluna `codigo_mestre` à tabela, o segredo de owner passou a viajar automaticamente em todo `ESTADO_INICIAL` e `PLACAR_ATUALIZADO`, para qualquer espectador conectado.

As rotas REST tinham sido blindadas explicitamente naquela story; o canal WebSocket não. O problema não é uma linha errada: é o reflexo automático do esquema no payload.

## 2. Nível no Roadmap e Branch

- **Nível**: Technical Story (`CV2.DS1.TS1`, dentro da Delivery Story `CV2.DS1 — Blindagem e Confiabilidade do Placar em Tempo Real`).
- **Branch**: `worktree-agent-a5cb003370b910540` (worktree dedicado do agente, criado a partir do backlog do CV2).

## 3. Escopo

1. `app/comandos.py`:
   - `CAMPOS_PUBLICOS_QUADRA = ("id", "nome", "criado_em", "atualizado_em", "controle_id", "controle_versao")`.
   - `_SELECT_QUADRA_PUBLICA` derivada da própria allowlist, para que consulta e projeção não possam divergir.
   - `projetar_quadra_publica(row)` monta o dicionário campo a campo a partir da allowlist.
   - `snapshot()` usa a consulta e a projeção; `executar_sync()` deixa de usar `SELECT *` (não emite o payload, mas mantém a mesma disciplina).
2. `tests/test_blindagem_e_confiabilidade.py`:
   - `test_espectador_nao_recebe_codigo_mestre_em_nenhum_frame`.
   - `test_coluna_sensivel_futura_fica_fora_do_snapshot_por_padrao`.

## 4. Decisões de Design

- **Allowlist, não denylist.** Uma denylist (`del sala["codigo_mestre"]`) corrigiria o sintoma e repetiria o erro na próxima coluna sensível. A allowlist inverte o padrão: o default é não sair.
- **Consulta derivada da allowlist.** A string SQL é construída a partir da mesma tupla usada na projeção. Não existe estado em que a consulta traga uma coluna que a projeção esqueceu de filtrar, nem o contrário.
- **Dupla barreira mantida.** Mesmo com a consulta já restrita, a projeção continua filtrando campo a campo. Se alguém no futuro voltar a consulta para `SELECT *`, o payload continua limpo.
- **Teste que prova o padrão, não só o caso.** Além de afirmar a ausência de `codigo_mestre`, um teste adiciona uma coluna nova em tempo de execução e confirma que ela também não vaza. É esse teste que protege a próxima coluna sensível.

## 5. O que está Fora de Escopo

- Rotação do `codigo_mestre` de salas existentes.
- Blindagem das rotas REST (já entregue na `CV1.DS2.TS1`).

## 6. Intenção de Versão

- **Patch** dentro da entrega da `CV2.DS1`: correção de segurança sem mudança de contrato para o cliente (nenhum campo que o frontend consumia foi removido).
