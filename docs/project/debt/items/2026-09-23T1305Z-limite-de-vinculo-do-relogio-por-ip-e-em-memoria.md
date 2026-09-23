---
id: debt-limite-de-vinculo-do-relogio-por-ip-e-em-memoria
status: Carried
kind: operation
severity: low
source: CV3.DS1.US1
revisit_trigger: Mais de uma pessoa usando relógio, ou 429 em POST /api/watch/pairing sem abuso aparente
closure_condition: Limite por cliente real (proxy confiável com --proxy-headers/forwarded-allow-ips) e persistido ou compartilhado entre reinícios
---

# Limite de Geração de Código do Relógio por IP Visto e em Memória

## Description

`POST /api/watch/pairing` limita a 5 códigos por 10 minutos, pela chave `request.client.host`. O uvicorn roda sem `--proxy-headers`: atrás de túnel ou proxy, todos os relógios chegam com o mesmo IP e dividem um único limite global. O contador vive em memória e zera a cada reinício.

## Carrying Reason

O recurso é pessoal (um relógio). Confiar em `X-Forwarded-For` sem proxy confiável configurado permitiria burlar o limite.

## Revisit Trigger

Uso por mais pessoas, ou 429 inesperado no vínculo.

## Closure Condition

IP real vindo de proxy confiável e contador que sobrevive a reinícios, com teste.
