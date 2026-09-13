---
code: CV1.DS1.TS1
kind: test-guide
updated: 2026-09-13
---

# Guia de teste — CV1.DS1.TS1

## Testes automatizados

`tests/test_projecao.py`

| caso | o que verifica |
|---|---|
| sequência simples | dez pontos alternados produzem o placar esperado |
| desfazer intercalado | pontos e desfazimentos misturados produzem o placar correto |
| desfazer até zerar | desfazer todos os pontos leva a 0x0 sem erro |
| desfazer o ponto da vitória | partida encerrada volta ao estado não encerrado |
| regra alterada no meio | desligar a vantagem em 11x11 faz o próximo ponto encerrar |
| teto da vantagem | com alvo 12 e teto 15, encerra em 15x14 |
| determinismo | executar a projeção duas vezes sobre o mesmo log produz estado idêntico |
| log vazio | projeção de partida sem eventos retorna 0x0 não encerrada |

`tests/test_eventos.py`

| caso | o que verifica |
|---|---|
| append incrementa `seq` | eventos consecutivos recebem sequência monotônica |
| append concorrente | dois appends simultâneos na mesma partida não colidem nem pulam sequência |
| `seq` após restart | reabrir a conexão e appendar continua do último `seq` gravado, não de zero |
| imutabilidade | nenhum caminho de código faz `UPDATE` ou `DELETE` na tabela de eventos |

## Rota de validação do Navigator

1. `uv run pytest` — todos verdes.
2. Rodar um script curto que grave uma sequência de eventos e abrir o arquivo SQLite:
   - eventos em ordem de `seq`, sem buracos;
   - nenhum evento com `criado_em` fora de UTC;
   - nenhuma linha alterada ou removida após um desfazer.
3. Executar a projeção duas vezes sobre o mesmo banco e comparar a saída.

**Condição de aprovação:** suíte verde, sequência íntegra no arquivo e projeção idêntica nas duas execuções.

**Condição de falha:** qualquer buraco ou repetição de `seq`, qualquer linha de evento alterada, ou divergência entre as duas execuções da projeção.
