---
id: debt-contraste-do-modo-sol-sem-verificacao-automatica
status: Carried
kind: accessibility
severity: low
source: fix/modo-sol-placar
revisit_trigger: Entrada de um terceiro tema, retorno de acessibilidade ao roadmap, ou qualquer alteração ampla de tokens de cor
closure_condition: Verificação automática de contraste cobrindo os dois temas em execução no pipeline de testes
---

# Contraste do Modo Sol Depende de Verificação Manual

## Description

O Modo Sol foi corrigido para que todos os componentes sigam os tokens do tema, e os valores de contraste foram escolhidos para cumprir WCAG 2.2 AA — numeral do placar em preto puro sobre branco (21:1), textos de badge escurecidos, azul de informação escurecido.

Não existe verificação automática disso. A conformidade foi validada por inspeção visual do Navigator e por comparação do CSS construído entre os temas. Uma regressão de contraste no Modo Sol passaria pelos testes atuais sem falhar nada.

O projeto tem `node --test` para lógica e `pytest` para o backend, mas nenhum runner de browser. A checagem de contraste precisa de um DOM renderizado para resolver as variáveis CSS em cascata.

## Carrying Reason

Instalar e manter um runner de browser (Playwright + axe) para uma única checagem custa mais que o risco atual: dois temas, uma paleta estável e uma superfície de produto pequena. A comparação mecânica do CSS construído, descrita no decision record `cores-de-tema-como-token-e-veu-como-canal-de-cor`, cobre a regressão mais provável, que é um componente voltar a declarar cor literal.

## Revisit Trigger

Um terceiro tema, o retorno de acessibilidade ao roadmap, ou qualquer alteração ampla de tokens de cor.

## Closure Condition

Verificação automática de contraste cobrindo ambos os temas, rodando junto com os testes existentes.
