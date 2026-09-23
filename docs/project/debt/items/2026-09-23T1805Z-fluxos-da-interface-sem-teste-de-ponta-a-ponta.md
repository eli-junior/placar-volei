---
id: debt-fluxos-da-interface-sem-teste-de-ponta-a-ponta
status: Carried
kind: validation
severity: medium
source: CV3.DS1.US2
revisit_trigger: Escolha de um runner de navegador (o mesmo que a dívida de contraste do Modo Sol pede), ou mais um defeito de interface achado só no teste físico
closure_condition: Um teste que percorra, num navegador, criar sala → vincular relógio → tornar controlador → passar controle, rodando junto com os demais
---

# Fluxos da Interface sem Teste de Ponta a Ponta

## Description

O site tem `node --test` para lógica pura e `svelte-check`, mas nenhum teste que renderize e clique nas telas. Os testes do backend chamam as rotas direto.

## Carrying Reason

Montar um runner de navegador é trabalho próprio, fora do escopo da US2. Os dois defeitos achados foram corrigidos com testes de lógica.

## Impact

Na US2, dois defeitos de interface só apareceram no teste físico do Navigator:

- a engrenagem das configurações aparecia vazia desde a CV2 (ícone `engrenagem` inexistente);
- não havia botão para passar o controle, embora a rota existisse desde a CV2.DS2.US5.

Cada um custou um ciclo de deploy no Mini PC, e cada deploy apaga as salas (`debt-banco-de-producao-sem-volume-persistente`).

## Revisit Trigger

Ver frontmatter.

## Closure Condition

Ver frontmatter.

## Notes

`web/tests/icones-usados.test.js` cobre só a classe de defeito do ícone.
