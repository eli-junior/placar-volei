---
id: debt-regra-de-vitoria-duplicada-no-relogio
status: Carried
kind: maintainability
severity: low
source: CV3.DS1.US2
revisit_trigger: Qualquer mudança em `app.projecao.avaliar_vitoria` ou nas regras da partida
closure_condition: O servidor envia no snapshot o que o relógio precisa para travar os botões (ex.: vitória prevista para +1 de cada equipe), ou a regra passa a ser gerada de uma fonte única
---

# Regra de Vitória Duplicada no Relógio

## Description

`wear/.../Scoreboard.kt` tem `avaliarVitoria`, cópia de `app.projecao.avaliar_vitoria` (alvo, vantagem de 2, teto). O relógio usa a cópia para travar os botões quando o placar previsto já é vitória.

Na US3 (0.9.0), o relógio passou a repetir também um pedaço da projeção: `stack` em `Scoreboard.kt` monta os pontos ativos confirmados (`equipes_ativas` do snapshot) e aplica os lances e desfazeres da fila. É o mesmo padrão: o relógio só prevê, e o servidor decide.

## Carrying Reason

Sem a cópia, o toque depois do ponto de vitória vira uma recusa previsível, e a fila pausa pedindo descarte. São ~15 linhas, com testes em Kotlin que repetem os casos do Python.

## Impact

Se as regras divergirem, o servidor continua sendo a autoridade: o pior caso é o relógio travar cedo demais ou deixar um toque que o servidor recusa. Nenhum ponto é aplicado indevidamente.

## Revisit Trigger

Ver frontmatter.

## Closure Condition

Ver frontmatter.
