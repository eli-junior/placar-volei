---
id: debt-casca-spec-falha-na-master
status: Carried
kind: test
severity: medium
source: CV6.DS1.US10
revisit_trigger: Qualquer mudança na casca do APK (CV7) ou na tela de escolha de servidor, ou a próxima rodada completa do e2e
closure_condition: Os 4 testes de `web/e2e/casca.spec.js` passando num checkout limpo da master, com a causa registrada
---

# Testes da Casca (e2e) Falham na Master

## Description

Em 2026-10-15, com o build local (`npm run build`) e o `playwright test e2e/casca.spec.js`, 4 testes falham tanto na `master` quanto na branch da US10: "escolha de servidor sem violações axe" (tema escuro e sol), "servidor fixo, testa a conexão e só então libera o botão" e "sem rede ou com o backend fora, o botão online fica bloqueado" (`toBeVisible` não acha o elemento). Não foram investigados; a suspeita é o ambiente (o build do e2e não embute o servidor fixo, `PLACAR_SERVIDOR`).

## Carrying Reason

Não nasceram da US10 e a casca não mudou nela; investigar sairia do escopo da história.

## Notes

O resto do e2e do espectador, de acessibilidade e de sequência passa (21 testes).

Em 2026-10-17 (CV8.DS7.US21): rodando a suíte inteira (`npx playwright test`), 8 testes falham, os da casca e também os de `e2e/local.spec.js`; rodando só `e2e/casca.spec.js e2e/local.spec.js`, os 7 passam, tanto na `master` quanto na branch. Isso enfraquece a suspeita de ambiente (`PLACAR_SERVIDOR`) e aponta para interferência entre testes na suíte completa.
