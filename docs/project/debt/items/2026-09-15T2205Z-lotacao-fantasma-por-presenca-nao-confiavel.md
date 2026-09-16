---
id: debt-lotacao-fantasma
status: Paid
kind: correctness
severity: medium
source: CV1.DS1.US1
revisit_trigger: Relato de sala recusando entrada com quadra visivelmente vazia
closure_condition: Limite de capacidade avaliado sobre presença efetiva (conexão ativa ou último visto recente), com teste automatizado
---

# Lotação Fantasma: Capacidade Conta Participantes Sem Conexão Ativa

## Description

`app/quadras.py` valida `settings.max_participantes_por_quadra` (20) contando linhas da tabela `participantes` da quadra, sem considerar se a pessoa ainda está conectada. O hub (`app/hub.py`) já conhece a presença real via `participantes_online`, e a coluna `ultimo_visto_em` já é atualizada na conexão e desconexão, mas nenhuma das duas informações participa da decisão de capacidade.

Na prática, uma pelada com rotatividade de pessoas (entra, fecha o navegador, entra de novo com outra sessão) esgota o limite da sala sem que exista ninguém de fato ocupando as vagas, bloqueando a entrada de quem está na quadra.

## Carrying Reason

O limite foi implementado na `CV1.DS1.US1` como proteção simples contra abuso, antes de existir a noção de presença online no hub (introduzida junto com a sucessão de admin). A contagem por linha bastava no fluxo original.

## Revisit Trigger

Qualquer sala real recusando participante legítimo, ou mudança no modelo de presença/sucessão.

## Closure Condition

Contagem de capacidade baseada em participantes com conexão ativa no hub ou `ultimo_visto_em` dentro da janela de inatividade, com teste cobrindo entrada liberada após expiração de participantes fantasmas.

## Notes

Pago por `CV2.DS1` (escopo C2).
