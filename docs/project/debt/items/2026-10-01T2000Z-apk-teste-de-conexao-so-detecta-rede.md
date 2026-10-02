---
id: debt-apk-teste-de-conexao-so-detecta-rede
status: Carried
kind: validation
severity: low
source: CV7.TS1
revisit_trigger: Falso "Servidor disponível" em quadra (backend fora com o túnel de pé), ou a TS2 começar a depender do servidor
closure_condition: /health responde com `Access-Control-Allow-Origin: https://localhost` e a tela inicial do APK lê `status: ok` em vez de só detectar a rede
---

# Teste de Conexão do APK Só Detecta Rede

## Description

A tela inicial do APK testa o servidor com `fetch(..., { mode: 'no-cors' })` em `/health`. A resposta é opaca: qualquer resposta HTTP conta como disponível, inclusive um 502 do Cloudflare Tunnel com o backend fora do ar. Só a falta de rede ou o tempo esgotado bloqueiam o botão.

## Carrying Reason

O backend não envia CORS e a TS1 prometia não mudar o backend. A falha de backend com o túnel de pé aparece logo ao abrir a quadra, sem perda de dados.

## Notes

Fechar exige liberar CORS só em `/health` para a origem `https://localhost` do Capacitor.
